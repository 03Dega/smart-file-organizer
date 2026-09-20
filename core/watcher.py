import shutil
import threading
import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.analyzer import analyze_file
from core.rules import find_matching_rule
from core.file_manager import get_safe_destination
from config.settings import load_rules

try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except Exception:
    NOTIFICATIONS_AVAILABLE = False


def notify(title, message):
    """
    Envía una notificación nativa de Windows. Si plyer falla por cualquier
    motivo (ej. permisos, sistema no compatible), simplemente no notifica
    en vez de tumbar la app.
    """

    if not NOTIFICATIONS_AVAILABLE:
        return

    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Smart File Organizer",
            timeout=6
        )

    except Exception:
        pass


def wait_until_file_ready(file_path, timeout=15, interval=0.5):
    """
    Espera hasta que el tamaño del archivo deje de cambiar, para no
    procesar un archivo que todavía se está copiando o descargando.

    Retorna False si el archivo desaparece mientras se espera (por
    ejemplo, si otro proceso lo movió o borró).
    """

    elapsed = 0.0
    last_size = -1

    while elapsed < timeout:
        try:
            current_size = file_path.stat().st_size

        except FileNotFoundError:
            return False

        if current_size == last_size:
            return True

        last_size = current_size

        time.sleep(interval)
        elapsed += interval

    return True


class AutoOrganizeHandler(FileSystemEventHandler):
    """
    Reacciona cuando llega un archivo nuevo a la carpeta vigilada:
    lo analiza, busca la primera regla que le aplique, y si hay una,
    lo mueve automáticamente.
    """

    def __init__(self, folder_path, on_file_organized=None):
        super().__init__()

        self.folder_path = Path(folder_path)
        self.on_file_organized = on_file_organized

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Se procesa en un hilo aparte para no bloquear al observador
        # de watchdog mientras se espera a que el archivo termine de escribirse.
        threading.Thread(
            target=self._process_file,
            args=(file_path,),
            daemon=True
        ).start()

    def _process_file(self, file_path):
        if not wait_until_file_ready(file_path):
            return

        if not file_path.exists():
            return

        try:
            file_info = analyze_file(file_path)

        except Exception:
            return

        rules = load_rules()

        rule = find_matching_rule(file_info, rules)

        if rule is None:
            return  # Ningún archivo se mueve si no hay una regla que aplique

        destination_folder = self.folder_path / rule.destination_folder
        destination_path = get_safe_destination(destination_folder, file_info["name"])

        try:
            destination_folder.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(destination_path))

        except Exception:
            return

        notify(
            "Smart File Organizer",
            f"'{file_info['name']}' organizado en '{rule.destination_folder}' "
            f"(regla: {rule.name})"
        )

        if self.on_file_organized:
            self.on_file_organized(
                file_info["name"],
                rule.name,
                str(destination_folder)
            )


class FolderWatcher:
    """
    Envuelve un Observer de watchdog para vigilar una carpeta (no sus
    subcarpetas) y organizar automáticamente los archivos nuevos que
    lleguen, según las reglas guardadas.
    """

    def __init__(self, folder_path, on_file_organized=None):
        self.folder_path = str(folder_path)
        self.observer = Observer()
        self.handler = AutoOrganizeHandler(folder_path, on_file_organized)

    def start(self):
        self.observer.schedule(self.handler, self.folder_path, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join(timeout=5)
import subprocess
import sys
from pathlib import Path

TASK_PREFIX = "SmartFileOrganizer_"


def _get_executable_command():
    """
    Arma la parte del comando que Windows debe ejecutar.

    Si la app corre como .exe empaquetado, usa esa misma ruta.
    Si corre como script (desarrollo), usa pythonw.exe + main.py.
    """

    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    python_exe = Path(sys.executable).parent / "pythonw.exe"
    main_script = Path(__file__).parent.parent / "main.py"

    return f'"{python_exe}" "{main_script}"'


def create_daily_task(task_name, folder_path, hour, minute):
    """
    Crea (o reemplaza si ya existe) una tarea programada de Windows que
    organiza la carpeta indicada todos los días a la hora indicada,
    usando las reglas guardadas — sin abrir la interfaz gráfica.

    Lanza RuntimeError con el mensaje de Windows si algo falla.
    """

    full_task_name = TASK_PREFIX + task_name
    time_str = f"{hour:02d}:{minute:02d}"

    command = _get_executable_command()
    full_command = f'{command} --auto-organize "{folder_path}"'

    result = subprocess.run(
        [
            "schtasks", "/create",
            "/tn", full_task_name,
            "/tr", full_command,
            "/sc", "daily",
            "/st", time_str,
            "/f"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or "No se pudo crear la tarea programada."
        )


def delete_task(task_name):
    """
    Elimina una tarea programada de Windows. No lanza error si ya
    no existe (por ejemplo, si el usuario la borró manualmente).
    """

    full_task_name = TASK_PREFIX + task_name

    subprocess.run(
        ["schtasks", "/delete", "/tn", full_task_name, "/f"],
        capture_output=True,
        text=True
    )
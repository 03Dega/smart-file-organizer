import sys
import webbrowser
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk

from core.analyzer import analyze_folder, generate_statistics
from core.file_manager import build_organization_plan, execute_plan
from core.rules import build_rules_plan
from core.version import APP_VERSION
from config.settings import load_rules


def resource_path(relative_path):
    """
    Resuelve una ruta a un recurso (como el ícono) tanto si el programa
    corre como script normal como si corre empaquetado con PyInstaller.
    """

    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent

    return base_path / relative_path


class MainWindow:
    def __init__(self, root):
        self.root = root

        self.root.title(f"Smart File Organizer v{APP_VERSION}")
        self.root.geometry("1000x800")
        self.root.minsize(900, 700)

        try:
            self.root.iconbitmap(resource_path("assets/icon.ico"))
        except Exception:
            pass  # Si el ícono no se encuentra, la app sigue funcionando sin él

        self.style = ttk.Style()
        self.colors = self.style.colors

        self.analyzed_files = []
        self.row_to_file = {}
        self.rules_window = None
        self.watcher = None

        self.create_interface()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_interface(self):
        # =====================================================
        # TÍTULO
        # =====================================================

        title = ttk.Label(
            self.root,
            text="SMART FILE ORGANIZER",
            font=("Segoe UI", 24, "bold"),
            bootstyle="light"
        )

        title.pack(pady=(20, 5))

        subtitle = ttk.Label(
            self.root,
            text="Organizador Inteligente de Archivos",
            font=("Segoe UI", 11),
            bootstyle="secondary"
        )

        subtitle.pack(pady=(0, 20))

        # =====================================================
        # SECCIÓN DE CARPETA
        # =====================================================

        folder_frame = ttk.Frame(self.root)

        folder_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )

        folder_label = ttk.Label(
            folder_frame,
            text="Carpeta:",
            font=("Segoe UI", 10, "bold")
        )

        folder_label.pack(side="left")

        self.folder_entry = ttk.Entry(
            folder_frame,
            font=("Segoe UI", 10)
        )

        self.folder_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=10
        )

        browse_button = ttk.Button(
            folder_frame,
            text="Examinar",
            bootstyle="secondary",
            command=self.select_folder
        )

        browse_button.pack(side="right")

        # =====================================================
        # BOTÓN ANALIZAR
        # =====================================================

        analyze_button = ttk.Button(
            self.root,
            text="ANALIZAR CARPETA",
            bootstyle="primary",
            padding=(20, 10),
            command=self.analyze
        )

        analyze_button.pack(pady=15)

        # =====================================================
        # RESUMEN
        # =====================================================

        summary_frame = ttk.LabelFrame(
            self.root,
            text="Resumen",
            bootstyle="secondary"
        )

        summary_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )

        self.total_label = ttk.Label(
            summary_frame,
            text="Total de archivos: 0",
            font=("Segoe UI", 11, "bold")
        )

        self.total_label.pack(
            anchor="w",
            padx=15,
            pady=10
        )

        self.statistics_label = ttk.Label(
            summary_frame,
            text="Sin análisis realizado.",
            font=("Segoe UI", 10),
            justify="left"
        )

        self.statistics_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        # =====================================================
        # PIE DE PÁGINA (versión + actualizaciones) — se ubica primero
        # para quedar en el fondo absoluto de la ventana
        # =====================================================

        footer_frame = ttk.Frame(self.root)

        footer_frame.pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=8
        )

        version_label = ttk.Label(
            footer_frame,
            text=f"Smart File Organizer v{APP_VERSION}",
            font=("Segoe UI", 8),
            bootstyle="secondary"
        )

        version_label.pack(side="left")

        update_button = ttk.Button(
            footer_frame,
            text="Buscar actualizaciones",
            bootstyle="link",
            command=self.check_updates
        )

        update_button.pack(side="right")

        # =====================================================
        # SECCIÓN: ORGANIZACIÓN POR REGLAS
        # =====================================================

        rules_section = ttk.LabelFrame(
            self.root,
            text="Organización por reglas personalizadas",
            bootstyle="info"
        )

        rules_section.pack(
            side="bottom",
            fill="x",
            padx=25,
            pady=(5, 5)
        )

        rules_buttons_frame = ttk.Frame(rules_section)

        rules_buttons_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(
            rules_buttons_frame,
            text="REGLAS...",
            bootstyle="secondary",
            padding=(15, 8),
            command=self.open_rules_window
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            rules_buttons_frame,
            text="VISTA PREVIA",
            bootstyle="info-outline",
            padding=(15, 8),
            command=self.preview_rules_organization
        ).pack(side="left", padx=10)

        ttk.Button(
            rules_buttons_frame,
            text="ORGANIZAR POR REGLAS",
            bootstyle="warning",
            padding=(15, 8),
            command=self.organize_by_rules
        ).pack(side="left", padx=10)

        # =====================================================
        # SECCIÓN: ORGANIZACIÓN POR CATEGORÍA
        # =====================================================

        category_section = ttk.LabelFrame(
            self.root,
            text="Organización rápida por categoría",
            bootstyle="success"
        )

        category_section.pack(
            side="bottom",
            fill="x",
            padx=25,
            pady=(5, 5)
        )

        category_buttons_frame = ttk.Frame(category_section)

        category_buttons_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(
            category_buttons_frame,
            text="VISTA PREVIA",
            bootstyle="info",
            padding=(15, 8),
            command=self.preview_organization
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            category_buttons_frame,
            text="ORGANIZAR ARCHIVOS SELECCIONADOS",
            bootstyle="success",
            padding=(15, 8),
            command=self.organize_selected
        ).pack(side="left", padx=10)

        # =====================================================
        # SECCIÓN: VIGILANCIA AUTOMÁTICA
        # =====================================================

        watch_section = ttk.LabelFrame(
            self.root,
            text="Vigilancia automática de carpeta",
            bootstyle="warning"
        )

        watch_section.pack(
            side="bottom",
            fill="x",
            padx=25,
            pady=(15, 5)
        )

        watch_controls_frame = ttk.Frame(watch_section)

        watch_controls_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.watch_toggle_button = ttk.Button(
            watch_controls_frame,
            text="ACTIVAR VIGILANCIA",
            bootstyle="success",
            padding=(15, 8),
            command=self.toggle_watching
        )

        self.watch_toggle_button.pack(side="left", padx=(0, 15))

        self.watch_status_label = ttk.Label(
            watch_controls_frame,
            text="Vigilancia: inactiva",
            font=("Segoe UI", 9, "bold"),
            bootstyle="secondary"
        )

        self.watch_status_label.pack(side="left")

        self.watch_log_label = ttk.Label(
            watch_section,
            text="Cuando esté activa, los archivos nuevos que lleguen a esta "
                 "carpeta se organizarán solos según tus reglas guardadas.",
            font=("Segoe UI", 8),
            bootstyle="secondary",
            wraplength=900,
            justify="left"
        )

        self.watch_log_label.pack(anchor="w", padx=10, pady=(0, 10))

        # =====================================================
        # TABLA DE ARCHIVOS (ocupa el espacio restante)
        # =====================================================

        files_frame = ttk.LabelFrame(
            self.root,
            text="Archivos encontrados (selecciona con clic, Ctrl+clic o Shift+clic)",
            bootstyle="secondary"
        )

        files_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        columns = (
            "name",
            "extension",
            "category",
            "size"
        )

        self.file_table = ttk.Treeview(
            files_frame,
            columns=columns,
            show="headings",
            selectmode="extended",
            bootstyle="dark"
        )

        self.file_table.heading("name", text="Nombre")
        self.file_table.heading("extension", text="Extensión")
        self.file_table.heading("category", text="Categoría")
        self.file_table.heading("size", text="Tamaño")

        self.file_table.column("name", width=400)
        self.file_table.column("extension", width=100, anchor="center")
        self.file_table.column("category", width=150, anchor="center")
        self.file_table.column("size", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(
            files_frame,
            orient="vertical",
            command=self.file_table.yview,
            bootstyle="round"
        )

        self.file_table.configure(yscrollcommand=scrollbar.set)

        self.file_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # =========================================================
    # CIERRE DE LA APP
    # =========================================================

    def on_close(self):
        if self.watcher is not None:
            self.watcher.stop()

        self.root.destroy()

    # =========================================================
    # SELECCIONAR CARPETA
    # =========================================================

    def select_folder(self):
        folder = filedialog.askdirectory(
            title="Seleccionar carpeta"
        )

        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    # =========================================================
    # ANALIZAR
    # =========================================================

    def analyze(self):
        folder = self.folder_entry.get().strip()

        if not folder:
            messagebox.showwarning(
                "Carpeta no seleccionada",
                "Selecciona una carpeta antes de analizar."
            )

            return

        try:
            self.analyzed_files = analyze_folder(folder)

            statistics = generate_statistics(self.analyzed_files)

            self.update_summary(statistics)
            self.update_table()

        except FileNotFoundError:
            messagebox.showerror("Error", "La carpeta indicada no existe.")

        except NotADirectoryError:
            messagebox.showerror("Error", "La ruta indicada no es una carpeta.")

        except PermissionError:
            messagebox.showerror(
                "Error",
                "No tienes permisos para acceder a esta carpeta."
            )

        except Exception as error:
            messagebox.showerror(
                "Error inesperado",
                f"Ocurrió un error:\n\n{error}"
            )

    # =========================================================
    # ACTUALIZAR RESUMEN
    # =========================================================

    def update_summary(self, statistics):
        total = len(self.analyzed_files)

        self.total_label.config(text=f"Total de archivos: {total}")

        categories = [
            "Imagen", "Video", "Audio", "Documento",
            "Comprimido", "Instalador", "Otro"
        ]

        lines = [
            f"{category}: {statistics.get(category, 0)}"
            for category in categories
        ]

        self.statistics_label.config(text="    ".join(lines))

    # =========================================================
    # ACTUALIZAR TABLA
    # =========================================================

    def update_table(self):
        for item in self.file_table.get_children():
            self.file_table.delete(item)

        self.row_to_file = {}

        for file in self.analyzed_files:
            size = self.format_size(file["size"])

            row_id = self.file_table.insert(
                "",
                tk.END,
                values=(file["name"], file["extension"], file["category"], size)
            )

            self.row_to_file[row_id] = file

    # =========================================================
    # OBTENER ARCHIVOS SELECCIONADOS
    # =========================================================

    def get_selected_files(self):
        selected_rows = self.file_table.selection()

        if not selected_rows:
            return self.analyzed_files

        return [self.row_to_file[row_id] for row_id in selected_rows]

    # =========================================================
    # TABLA DE VISTA PREVIA (reutilizable)
    # =========================================================

    def show_preview_table(self, title, columns, rows):
        window = ttk.Toplevel(self.root)

        window.title(title)
        window.geometry("800x480")

        window.transient(self.root)

        table_frame = ttk.Frame(window)

        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            bootstyle="dark"
        )

        for column in columns:
            table.heading(column, text=column)
            table.column(column, width=220)

        for row in rows:
            table.insert("", tk.END, values=row)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=table.yview,
            bootstyle="round"
        )

        table.configure(yscrollcommand=scrollbar.set)

        table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        count_label = ttk.Label(
            window,
            text=f"Total: {len(rows)} archivo(s)",
            font=("Segoe UI", 9, "bold"),
            bootstyle="secondary"
        )

        count_label.pack(anchor="w", padx=15, pady=(0, 10))

    # =========================================================
    # VISTA PREVIA (POR CATEGORÍA)
    # =========================================================

    def preview_organization(self):
        folder = self.folder_entry.get().strip()

        if not self.analyzed_files:
            messagebox.showwarning(
                "Sin análisis",
                "Analiza una carpeta antes de continuar."
            )

            return

        files = self.get_selected_files()

        plan = build_organization_plan(files, folder)

        rows = [
            (item["source"].name, str(item["destination_folder"]))
            for item in plan
        ]

        self.show_preview_table(
            "Vista previa",
            ("Archivo", "Carpeta destino"),
            rows
        )

    # =========================================================
    # VISTA PREVIA (POR REGLAS)
    # =========================================================

    def preview_rules_organization(self):
        folder = self.folder_entry.get().strip()

        if not self.analyzed_files:
            messagebox.showwarning(
                "Sin análisis",
                "Analiza una carpeta antes de continuar."
            )

            return

        rules = load_rules()

        if not rules:
            messagebox.showwarning(
                "Sin reglas",
                "No has creado ninguna regla todavía. Usa el botón 'REGLAS...' para crear una."
            )

            return

        plan = build_rules_plan(self.analyzed_files, rules, folder)

        if not plan:
            messagebox.showinfo(
                "Sin coincidencias",
                "Ningún archivo coincide con las reglas activas."
            )

            return

        rows = [
            (item["source"].name, str(item["destination_folder"]), item["rule_name"])
            for item in plan
        ]

        self.show_preview_table(
            "Vista previa por reglas",
            ("Archivo", "Carpeta destino", "Regla aplicada"),
            rows
        )

    # =========================================================
    # ORGANIZAR ARCHIVOS SELECCIONADOS (POR CATEGORÍA)
    # =========================================================

    def organize_selected(self):
        folder = self.folder_entry.get().strip()

        if not self.analyzed_files:
            messagebox.showwarning(
                "Sin análisis",
                "Analiza una carpeta antes de continuar."
            )

            return

        files = self.get_selected_files()

        confirm = messagebox.askyesno(
            "Confirmar organización",
            f"Se moverán {len(files)} archivo(s) a subcarpetas por categoría.\n\n"
            "Esta acción no se puede deshacer. ¿Continuar?"
        )

        if not confirm:
            return

        plan = build_organization_plan(files, folder)

        result = execute_plan(plan)

        message = f"Archivos movidos: {len(result['moved'])}"

        if result["errors"]:
            message += f"\nErrores: {len(result['errors'])}"

            for error in result["errors"]:
                message += f"\n- {error['source'].name}: {error['error']}"

        messagebox.showinfo("Organización completada", message)

        self.analyze()

    # =========================================================
    # ABRIR VENTANA DE REGLAS (reutiliza si ya está abierta)
    # =========================================================

    def open_rules_window(self):
        from ui.rules_window import RulesWindow

        if self.rules_window is not None and self.rules_window.winfo_exists():
            self.rules_window.lift()
            self.rules_window.focus_force()
            return

        self.rules_window = RulesWindow(self.root)

    # =========================================================
    # ORGANIZAR SEGÚN REGLAS GUARDADAS
    # =========================================================

    def organize_by_rules(self):
        folder = self.folder_entry.get().strip()

        if not self.analyzed_files:
            messagebox.showwarning(
                "Sin análisis",
                "Analiza una carpeta antes de continuar."
            )

            return

        rules = load_rules()

        if not rules:
            messagebox.showwarning(
                "Sin reglas",
                "No has creado ninguna regla todavía. Usa el botón 'REGLAS...' para crear una."
            )

            return

        plan = build_rules_plan(self.analyzed_files, rules, folder)

        if not plan:
            messagebox.showinfo(
                "Sin coincidencias",
                "Ningún archivo coincide con las reglas activas."
            )

            return

        confirm = messagebox.askyesno(
            "Confirmar organización por reglas",
            f"Se moverán {len(plan)} archivo(s) según tus reglas.\n\n"
            "Esta acción no se puede deshacer. ¿Continuar?"
        )

        if not confirm:
            return

        result = execute_plan(plan)

        message = f"Archivos movidos: {len(result['moved'])}"

        if result["errors"]:
            message += f"\nErrores: {len(result['errors'])}"

            for error in result["errors"]:
                message += f"\n- {error['source'].name}: {error['error']}"

        messagebox.showinfo("Organización completada", message)

        self.analyze()

    # =========================================================
    # VIGILANCIA AUTOMÁTICA
    # =========================================================

    def toggle_watching(self):
        if self.watcher is not None:
            self.watcher.stop()
            self.watcher = None

            self.watch_toggle_button.config(
                text="ACTIVAR VIGILANCIA",
                bootstyle="success"
            )

            self.watch_status_label.config(text="Vigilancia: inactiva")

            return

        folder = self.folder_entry.get().strip()

        if not folder:
            messagebox.showwarning(
                "Carpeta no seleccionada",
                "Selecciona una carpeta antes de activar la vigilancia."
            )

            return

        rules = load_rules()

        if not rules:
            messagebox.showwarning(
                "Sin reglas",
                "La vigilancia automática organiza los archivos nuevos según "
                "tus reglas guardadas. Crea al menos una regla en 'REGLAS...' "
                "antes de activarla."
            )

            return

        from core.watcher import FolderWatcher

        self.watcher = FolderWatcher(
            folder,
            on_file_organized=self.handle_file_organized
        )

        self.watcher.start()

        self.watch_toggle_button.config(
            text="DESACTIVAR VIGILANCIA",
            bootstyle="danger"
        )

        self.watch_status_label.config(text=f"Vigilancia: activa en {folder}")

    def handle_file_organized(self, file_name, rule_name, destination_folder):
        # Este callback llega desde un hilo secundario (watchdog); hay que
        # pasar la actualización de la interfaz al hilo principal con after().
        self.root.after(
            0,
            lambda: self._update_watch_log(file_name, rule_name, destination_folder)
        )

    def _update_watch_log(self, file_name, rule_name, destination_folder):
        self.watch_log_label.config(
            text=f"Último organizado automáticamente: '{file_name}' -> "
                 f"{destination_folder} (regla: {rule_name})"
        )

        if self.analyzed_files:
            self.analyze()

    # =========================================================
    # BUSCAR ACTUALIZACIONES
    # =========================================================

    def check_updates(self):
        from utils.updater import check_for_updates

        update_info = check_for_updates()

        if update_info is None:
            messagebox.showinfo(
                "Actualizaciones",
                f"Ya tienes la última versión (v{APP_VERSION}) o no fue "
                "posible comprobarlo en este momento."
            )

            return

        notes = update_info.get("notes", "")

        confirm = messagebox.askyesno(
            "Actualización disponible",
            f"Hay una nueva versión disponible: v{update_info['version']}\n\n"
            f"{notes}\n\n¿Abrir la página de descarga?"
        )

        if confirm:
            webbrowser.open(update_info["download_url"])

    # =========================================================
    # FORMATEAR TAMAÑO
    # =========================================================

    @staticmethod
    def format_size(size):
        if size < 1024:
            return f"{size} B"

        if size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"

        if size < 1024 ** 3:
            return f"{size / (1024 ** 2):.2f} MB"

        return f"{size / (1024 ** 3):.2f} GB"


def start_application():
    root = ttk.Window(themename="superhero")

    MainWindow(root)

    root.mainloop()
import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk

from core.scheduler import create_daily_task, delete_task
from config.settings import load_scheduled_tasks, save_scheduled_tasks


class ScheduledTasksWindow(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Tareas programadas")
        self.geometry("750x550")
        self.minsize(700, 500)

        self.transient(parent)

        self.colors = ttk.Style().colors

        self.tasks = load_scheduled_tasks()

        self.create_interface()
        self.refresh_tasks_list()

    def make_dark_listbox(self, parent, **kwargs):
        return tk.Listbox(
            parent,
            bg=self.colors.inputbg,
            fg=self.colors.inputfg,
            selectbackground=self.colors.selectbg,
            selectforeground=self.colors.selectfg,
            relief="flat",
            highlightthickness=0,
            **kwargs
        )

    def create_interface(self):
        main_frame = ttk.Frame(self)

        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(
            main_frame,
            text="Organiza una carpeta automáticamente todos los días, a la "
                 "hora que elijas, aunque la app esté cerrada.",
            font=("Segoe UI", 9, "bold"),
            wraplength=700,
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        # ================= LISTA DE TAREAS =================

        list_frame = ttk.LabelFrame(
            main_frame,
            text="Tareas programadas",
            bootstyle="secondary"
        )

        list_frame.pack(fill="both", expand=True, pady=(0, 15))

        self.tasks_listbox = self.make_dark_listbox(
            list_frame,
            font=("Segoe UI", 10),
            height=8
        )

        self.tasks_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(
            list_frame,
            text="Eliminar tarea seleccionada",
            bootstyle="danger-outline",
            command=self.delete_selected_task
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # ================= FORMULARIO NUEVA TAREA =================

        form_frame = ttk.LabelFrame(
            main_frame,
            text="Nueva tarea",
            bootstyle="secondary"
        )

        form_frame.pack(fill="x")

        ttk.Label(
            form_frame,
            text="Nombre de la tarea:",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 0))

        self.name_entry = ttk.Entry(form_frame, font=("Segoe UI", 10))

        self.name_entry.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(
            form_frame,
            text="Carpeta a organizar:",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=10)

        folder_row = ttk.Frame(form_frame)

        folder_row.pack(fill="x", padx=10, pady=(0, 10))

        self.folder_entry = ttk.Entry(folder_row, font=("Segoe UI", 10))

        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ttk.Button(
            folder_row,
            text="Examinar",
            bootstyle="secondary",
            command=self.select_folder
        ).pack(side="right")

        time_row = ttk.Frame(form_frame)

        time_row.pack(fill="x", padx=10, pady=(0, 15))

        ttk.Label(
            time_row,
            text="Hora todos los días:",
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        self.hour_spinbox = ttk.Spinbox(
            time_row, from_=0, to=23, width=5, format="%02.0f"
        )

        self.hour_spinbox.set("20")

        self.hour_spinbox.pack(side="left", padx=(10, 5))

        ttk.Label(time_row, text=":").pack(side="left")

        self.minute_spinbox = ttk.Spinbox(
            time_row, from_=0, to=59, width=5, format="%02.0f"
        )

        self.minute_spinbox.set("00")

        self.minute_spinbox.pack(side="left", padx=(5, 0))

        ttk.Label(
            form_frame,
            text="La carpeta se organiza según tus reglas guardadas en 'REGLAS...'.",
            font=("Segoe UI", 8),
            bootstyle="secondary"
        ).pack(anchor="w", padx=10, pady=(0, 10))

        bottom_frame = ttk.Frame(form_frame)

        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(
            bottom_frame,
            text="Crear tarea",
            bootstyle="primary",
            padding=(15, 8),
            command=self.create_task
        ).pack(side="left")

        ttk.Button(
            bottom_frame,
            text="Cerrar",
            bootstyle="secondary",
            padding=(15, 8),
            command=self.destroy
        ).pack(side="right")

    def select_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta")

        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    def refresh_tasks_list(self):
        self.tasks_listbox.delete(0, tk.END)

        for task in self.tasks:
            self.tasks_listbox.insert(
                tk.END,
                f"{task['name']}  —  {task['folder']}  —  "
                f"todos los días a las {task['hour']:02d}:{task['minute']:02d}"
            )

    def create_task(self):
        name = self.name_entry.get().strip()
        folder = self.folder_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Falta el nombre",
                "Ponle un nombre a la tarea.",
                parent=self
            )
            return

        if not folder:
            messagebox.showwarning(
                "Falta la carpeta",
                "Selecciona qué carpeta se debe organizar.",
                parent=self
            )
            return

        if any(task["name"].lower() == name.lower() for task in self.tasks):
            messagebox.showwarning(
                "Nombre repetido",
                f"Ya existe una tarea llamada '{name}'. Usa otro nombre.",
                parent=self
            )
            return

        try:
            hour = int(self.hour_spinbox.get())
            minute = int(self.minute_spinbox.get())

        except ValueError:
            messagebox.showerror(
                "Hora inválida",
                "La hora y los minutos deben ser números.",
                parent=self
            )
            return

        try:
            create_daily_task(name, folder, hour, minute)

        except RuntimeError as error:
            messagebox.showerror(
                "No se pudo crear la tarea",
                f"Windows reportó un error:\n\n{error}",
                parent=self
            )
            return

        self.tasks.append({
            "name": name,
            "folder": folder,
            "hour": hour,
            "minute": minute
        })

        save_scheduled_tasks(self.tasks)

        self.refresh_tasks_list()

        self.name_entry.delete(0, tk.END)
        self.folder_entry.delete(0, tk.END)

        messagebox.showinfo(
            "Tarea creada",
            f"'{name}' organizará esa carpeta todos los días a las "
            f"{hour:02d}:{minute:02d}, aunque la app esté cerrada.",
            parent=self
        )

    def delete_selected_task(self):
        selection = self.tasks_listbox.curselection()

        if not selection:
            messagebox.showwarning(
                "Sin selección",
                "Selecciona una tarea de la lista para eliminarla.",
                parent=self
            )
            return

        index = selection[0]
        task = self.tasks[index]

        confirm = messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la tarea '{task['name']}'?",
            parent=self
        )

        if not confirm:
            return

        delete_task(task["name"])

        del self.tasks[index]

        save_scheduled_tasks(self.tasks)

        self.refresh_tasks_list()
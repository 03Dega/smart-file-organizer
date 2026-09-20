import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

from core.rules import Rule, Condition
from config.settings import load_rules, save_rules


# =========================================================
# TRADUCCIÓN: lo que ve el usuario  ->  lo que usa el motor
# =========================================================

FIELD_OPTIONS = {
    "Extensión de archivo": "extension",
    "Nombre del archivo": "name",
    "Categoría": "category",
    "Tamaño (MB)": "size_mb",
    "Antigüedad (días)": "age_days",
    "Ancho (píxeles)": "width",
    "Alto (píxeles)": "height",
    "Duración (segundos)": "duration",
    "Velocidad de video (FPS)": "fps",
}

REVERSE_FIELD = {value: key for key, value in FIELD_OPTIONS.items()}

TEXT_OPERATORS = {
    "es igual a": "==",
    "es diferente de": "!=",
    "contiene": "contains",
    "empieza con": "starts_with",
    "termina con": "ends_with",
}

CATEGORY_OPERATORS = {
    "es igual a": "==",
    "es diferente de": "!=",
}

NUMERIC_OPERATORS = {
    "es igual a": "==",
    "es menor que": "<",
    "es menor o igual que": "<=",
    "es mayor que": ">",
    "es mayor o igual que": ">=",
}

FIELD_TO_OPERATOR_OPTIONS = {
    "extension": TEXT_OPERATORS,
    "name": TEXT_OPERATORS,
    "category": CATEGORY_OPERATORS,
    "size_mb": NUMERIC_OPERATORS,
    "age_days": NUMERIC_OPERATORS,
    "width": NUMERIC_OPERATORS,
    "height": NUMERIC_OPERATORS,
    "duration": NUMERIC_OPERATORS,
    "fps": NUMERIC_OPERATORS,
}

REVERSE_OPERATOR = {
    "==": "es igual a",
    "!=": "es diferente de",
    "contains": "contiene",
    "starts_with": "empieza con",
    "ends_with": "termina con",
    "<": "es menor que",
    "<=": "es menor o igual que",
    ">": "es mayor que",
    ">=": "es mayor o igual que",
}

FIELD_HINTS = {
    "extension": "Ejemplo: .pdf   .jpg   .exe   (con el punto al inicio)",
    "name": "Ejemplo: factura   informe   captura",
    "category": "Escribe: Imagen, Video, Audio, Documento, Comprimido, Instalador u Otro",
    "size_mb": "Escribe solo el número, en megabytes. Ejemplo: 5",
    "age_days": "Escribe solo el número, en días. Ejemplo: 30",
    "width": "Solo aplica a Imágenes y Videos. Número en píxeles. Ejemplo: 1920",
    "height": "Solo aplica a Imágenes y Videos. Número en píxeles. Ejemplo: 1080",
    "duration": "Solo aplica a Audio y Video. Número en segundos. Ejemplo: 60",
    "fps": "Solo aplica a Video. Número de cuadros por segundo. Ejemplo: 30",
}

NUMERIC_FIELDS = {"size_mb", "age_days", "width", "height", "duration", "fps"}


# =========================================================
# PLANTILLAS DE REGLAS PREDETERMINADAS
# =========================================================

PRESET_RULES = [
    # ---------- IMÁGENES ----------
    {
        "name": "Imágenes Pesadas",
        "description": "Imagen de más de 5 MB",
        "conditions": [
            ("category", "==", "Imagen"),
            ("size_mb", ">", 5),
        ],
        "logic": "AND",
        "destination_folder": "Imágenes Pesadas",
    },
    {
        "name": "Imágenes Livianas",
        "description": "Imagen de menos de 500 KB (0.5 MB)",
        "conditions": [
            ("category", "==", "Imagen"),
            ("size_mb", "<", 0.5),
        ],
        "logic": "AND",
        "destination_folder": "Imágenes Livianas",
    },
    {
        "name": "Imágenes en Alta Resolución",
        "description": "Imagen con ancho de 3000px o más",
        "conditions": [
            ("category", "==", "Imagen"),
            ("width", ">=", 3000),
        ],
        "logic": "AND",
        "destination_folder": "Imágenes Alta Resolución",
    },
    {
        "name": "Capturas de Pantalla",
        "description": "Nombre de archivo que contiene 'captura' o 'screenshot'",
        "conditions": [
            ("name", "contains", "captura"),
            ("name", "contains", "screenshot"),
        ],
        "logic": "OR",
        "destination_folder": "Capturas de Pantalla",
    },
    {
        "name": "Imágenes PNG",
        "description": "Archivos con extensión .png",
        "conditions": [
            ("extension", "==", ".png"),
        ],
        "logic": "AND",
        "destination_folder": "Imágenes PNG",
    },

    # ---------- VIDEOS ----------
    {
        "name": "Videos Cortos",
        "description": "Video con duración menor a 60 segundos",
        "conditions": [
            ("category", "==", "Video"),
            ("duration", "<", 60),
        ],
        "logic": "AND",
        "destination_folder": "Videos Cortos",
    },
    {
        "name": "Videos Largos",
        "description": "Video con duración mayor a 20 minutos (1200 segundos)",
        "conditions": [
            ("category", "==", "Video"),
            ("duration", ">", 1200),
        ],
        "logic": "AND",
        "destination_folder": "Videos Largos",
    },
    {
        "name": "Videos en Alta Resolución",
        "description": "Video con ancho de 1920px o más (Full HD o superior)",
        "conditions": [
            ("category", "==", "Video"),
            ("width", ">=", 1920),
        ],
        "logic": "AND",
        "destination_folder": "Videos HD",
    },
    {
        "name": "Videos 4K",
        "description": "Video con ancho de 3840px o más",
        "conditions": [
            ("category", "==", "Video"),
            ("width", ">=", 3840),
        ],
        "logic": "AND",
        "destination_folder": "Videos 4K",
    },
    {
        "name": "Videos Pesados",
        "description": "Video de más de 200 MB",
        "conditions": [
            ("category", "==", "Video"),
            ("size_mb", ">", 200),
        ],
        "logic": "AND",
        "destination_folder": "Videos Pesados",
    },

    # ---------- AUDIO ----------
    {
        "name": "Audios Largos",
        "description": "Audio con duración mayor a 10 minutos (600 segundos)",
        "conditions": [
            ("category", "==", "Audio"),
            ("duration", ">", 600),
        ],
        "logic": "AND",
        "destination_folder": "Audios Largos",
    },
    {
        "name": "Música MP3",
        "description": "Archivos con extensión .mp3",
        "conditions": [
            ("extension", "==", ".mp3"),
        ],
        "logic": "AND",
        "destination_folder": "Música",
    },

    # ---------- DOCUMENTOS ----------
    {
        "name": "PDFs Grandes",
        "description": "Archivo .pdf de más de 20 MB",
        "conditions": [
            ("extension", "==", ".pdf"),
            ("size_mb", ">", 20),
        ],
        "logic": "AND",
        "destination_folder": "PDFs Grandes",
    },
    {
        "name": "Documentos Word",
        "description": "Archivos .doc o .docx",
        "conditions": [
            ("extension", "==", ".doc"),
            ("extension", "==", ".docx"),
        ],
        "logic": "OR",
        "destination_folder": "Documentos Word",
    },
    {
        "name": "Hojas de Cálculo",
        "description": "Archivos .xls o .xlsx",
        "conditions": [
            ("extension", "==", ".xls"),
            ("extension", "==", ".xlsx"),
        ],
        "logic": "OR",
        "destination_folder": "Hojas de Cálculo",
    },
    {
        "name": "Presentaciones",
        "description": "Archivos .ppt o .pptx",
        "conditions": [
            ("extension", "==", ".ppt"),
            ("extension", "==", ".pptx"),
        ],
        "logic": "OR",
        "destination_folder": "Presentaciones",
    },
    {
        "name": "Facturas y Recibos",
        "description": "Nombre de archivo que contiene 'factura' o 'recibo'",
        "conditions": [
            ("name", "contains", "factura"),
            ("name", "contains", "recibo"),
        ],
        "logic": "OR",
        "destination_folder": "Facturas y Recibos",
    },

    # ---------- COMPRIMIDOS E INSTALADORES ----------
    {
        "name": "Comprimidos",
        "description": "Archivos .zip, .rar o .7z",
        "conditions": [
            ("extension", "==", ".zip"),
            ("extension", "==", ".rar"),
            ("extension", "==", ".7z"),
        ],
        "logic": "OR",
        "destination_folder": "Comprimidos",
    },
    {
        "name": "Instaladores",
        "description": "Archivos .exe o .msi",
        "conditions": [
            ("extension", "==", ".exe"),
            ("extension", "==", ".msi"),
        ],
        "logic": "OR",
        "destination_folder": "Instaladores",
    },

    # ---------- GENERALES (cualquier tipo) ----------
    {
        "name": "Archivos Antiguos",
        "description": "Cualquier archivo con más de 180 días sin modificarse",
        "conditions": [
            ("age_days", ">", 180),
        ],
        "logic": "AND",
        "destination_folder": "Archivos Antiguos",
    },
    {
        "name": "Archivos Recientes",
        "description": "Cualquier archivo modificado en los últimos 7 días",
        "conditions": [
            ("age_days", "<", 7),
        ],
        "logic": "AND",
        "destination_folder": "Archivos Recientes",
    },
    {
        "name": "Archivos Muy Pesados",
        "description": "Cualquier archivo de más de 500 MB, sin importar el tipo",
        "conditions": [
            ("size_mb", ">", 500),
        ],
        "logic": "AND",
        "destination_folder": "Archivos Muy Pesados",
    },
]


class RulesWindow(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Gestor de reglas")
        self.geometry("1150x780")
        self.minsize(1000, 680)

        # Ancla esta ventana a la principal: evita que la ventana principal
        # se ponga encima al cerrar diálogos o cambiar de foco.
        self.transient(parent)

        self.colors = ttk.Style().colors

        self.rules = load_rules()
        self.current_conditions = []
        self.editing_index = None

        self.create_interface()
        self.refresh_rules_list()

    # =========================================================
    # LISTBOX CON COLORES DEL TEMA (widget clásico, no ttk)
    # =========================================================

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

    # =========================================================
    # INTERFAZ
    # =========================================================

    def create_interface(self):
        main_frame = ttk.Frame(self)

        main_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # ================= LISTA DE REGLAS (izquierda) =================

        list_frame = ttk.LabelFrame(
            main_frame,
            text="Reglas guardadas",
            bootstyle="secondary"
        )

        list_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        self.rules_listbox = self.make_dark_listbox(
            list_frame,
            font=("Segoe UI", 10)
        )

        self.rules_listbox.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.rules_listbox.bind(
            "<<ListboxSelect>>",
            self.on_select_rule
        )

        list_buttons_frame = ttk.Frame(list_frame)

        list_buttons_frame.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

        ttk.Button(
            list_buttons_frame,
            text="+ Nueva regla",
            bootstyle="success",
            command=self.new_rule
        ).pack(side="left", padx=5)

        ttk.Button(
            list_buttons_frame,
            text="Usar plantilla",
            bootstyle="info",
            command=self.open_templates_window
        ).pack(side="left", padx=5)

        ttk.Button(
            list_buttons_frame,
            text="Eliminar regla",
            bootstyle="danger",
            command=self.delete_rule
        ).pack(side="left", padx=5)

        # ================= FORMULARIO (derecha) =================

        form_frame = ttk.LabelFrame(
            main_frame,
            text="Detalle de la regla",
            bootstyle="secondary"
        )

        form_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        ttk.Label(
            form_frame,
            text="1. Ponle un nombre a la regla:",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 0))

        self.name_entry = ttk.Entry(
            form_frame,
            font=("Segoe UI", 10)
        )

        self.name_entry.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(
            form_frame,
            text="2. ¿A qué carpeta se deben mover los archivos que cumplan la regla?",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=10)

        self.destination_entry = ttk.Entry(
            form_frame,
            font=("Segoe UI", 10)
        )

        self.destination_entry.pack(fill="x", padx=10, pady=(0, 2))

        ttk.Label(
            form_frame,
            text="Se creará dentro de la carpeta que analizaste. Ejemplo: Facturas",
            font=("Segoe UI", 8),
            bootstyle="secondary"
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # ================= CONDICIONES =================

        ttk.Label(
            form_frame,
            text="3. ¿Qué archivos debe atrapar esta regla?",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=10)

        self.conditions_listbox = self.make_dark_listbox(
            form_frame,
            font=("Segoe UI", 9),
            height=5
        )

        self.conditions_listbox.pack(
            fill="both",
            expand=False,
            padx=10,
            pady=(5, 5)
        )

        ttk.Button(
            form_frame,
            text="Quitar condición seleccionada",
            bootstyle="danger-outline",
            command=self.remove_condition
        ).pack(anchor="w", padx=10, pady=(0, 10))

        condition_builder = ttk.LabelFrame(
            form_frame,
            text="Agregar una condición nueva",
            bootstyle="secondary"
        )

        condition_builder.pack(fill="x", padx=10, pady=(0, 10))

        row_1 = ttk.Frame(condition_builder)

        row_1.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(
            row_1,
            text="El archivo...",
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.field_combo = ttk.Combobox(
            row_1,
            values=list(FIELD_OPTIONS.keys()),
            state="readonly",
            width=22,
            bootstyle="secondary"
        )

        self.field_combo.set("Extensión de archivo")

        self.field_combo.pack(side="left", padx=8)

        self.field_combo.bind(
            "<<ComboboxSelected>>",
            self.update_operator_options
        )

        self.operator_combo = ttk.Combobox(
            row_1,
            values=list(TEXT_OPERATORS.keys()),
            state="readonly",
            width=18,
            bootstyle="secondary"
        )

        self.operator_combo.set("es igual a")

        self.operator_combo.pack(side="left", padx=8)

        row_2 = ttk.Frame(condition_builder)

        row_2.pack(fill="x", padx=10, pady=(0, 5))

        ttk.Label(
            row_2,
            text="Valor:",
            font=("Segoe UI", 9)
        ).pack(side="left")

        self.value_entry = ttk.Entry(row_2, width=25)

        self.value_entry.pack(side="left", padx=8)

        ttk.Button(
            row_2,
            text="Agregar condición",
            bootstyle="success",
            command=self.add_condition
        ).pack(side="left", padx=8)

        self.hint_label = ttk.Label(
            condition_builder,
            text=FIELD_HINTS["extension"],
            font=("Segoe UI", 8),
            bootstyle="secondary",
            wraplength=380,
            justify="left"
        )

        self.hint_label.pack(anchor="w", padx=10, pady=(0, 10))

        logic_frame = ttk.Frame(form_frame)

        logic_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(
            logic_frame,
            text="4. Si hay varias condiciones, ¿cómo se combinan?",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        self.logic_var = tk.StringVar(value="AND")

        ttk.Radiobutton(
            logic_frame,
            text="Deben cumplirse TODAS",
            variable=self.logic_var,
            value="AND",
            bootstyle="info"
        ).pack(anchor="w", padx=15)

        ttk.Radiobutton(
            logic_frame,
            text="Basta con que se cumpla UNA",
            variable=self.logic_var,
            value="OR",
            bootstyle="info"
        ).pack(anchor="w", padx=15)

        self.enabled_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            form_frame,
            text="Regla activa",
            variable=self.enabled_var,
            bootstyle="round-toggle"
        ).pack(anchor="w", padx=10, pady=(0, 5))

        bottom_frame = ttk.Frame(form_frame)

        bottom_frame.pack(
            fill="x",
            padx=10,
            pady=10,
            side="bottom"
        )

        ttk.Button(
            bottom_frame,
            text="Guardar regla",
            bootstyle="primary",
            padding=(15, 8),
            command=self.save_rule
        ).pack(side="left", padx=5)

        ttk.Button(
            bottom_frame,
            text="Cerrar",
            bootstyle="secondary",
            padding=(15, 8),
            command=self.destroy
        ).pack(side="right", padx=5)

    # =========================================================
    # PLANTILLAS
    # =========================================================

    def open_templates_window(self):
        templates_window = ttk.Toplevel(self)

        templates_window.title("Plantillas de reglas")
        templates_window.geometry("480x420")

        templates_window.transient(self)

        ttk.Label(
            templates_window,
            text="Elige una plantilla para empezar. Podrás editarla antes de guardar.",
            font=("Segoe UI", 9, "bold"),
            wraplength=440,
            justify="left"
        ).pack(anchor="w", padx=10, pady=10)

        templates_listbox = self.make_dark_listbox(
            templates_window,
            font=("Segoe UI", 10),
            height=10
        )

        templates_listbox.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 5)
        )

        for preset in PRESET_RULES:
            templates_listbox.insert(tk.END, preset["name"])

        description_label = ttk.Label(
            templates_window,
            text="",
            font=("Segoe UI", 8),
            bootstyle="secondary",
            wraplength=440,
            justify="left"
        )

        description_label.pack(anchor="w", padx=10, pady=(0, 10))

        def on_template_select(event=None):
            selection = templates_listbox.curselection()

            if not selection:
                return

            preset = PRESET_RULES[selection[0]]

            description_label.config(text=preset["description"])

        templates_listbox.bind("<<ListboxSelect>>", on_template_select)

        def use_selected_template():
            selection = templates_listbox.curselection()

            if not selection:
                Messagebox.show_info(
                    "Selecciona una plantilla de la lista.",
                    "Nada seleccionado",
                    parent=templates_window
                )

                return

            preset = PRESET_RULES[selection[0]]

            self.load_preset_into_form(preset)

            templates_window.destroy()

        ttk.Button(
            templates_window,
            text="Usar esta plantilla",
            bootstyle="primary",
            padding=(15, 8),
            command=use_selected_template
        ).pack(pady=(0, 10))

    def load_preset_into_form(self, preset):
        self.new_rule()

        self.name_entry.insert(0, preset["name"])
        self.destination_entry.insert(0, preset["destination_folder"])
        self.logic_var.set(preset["logic"])

        self.current_conditions = [
            Condition(field, operator, value)
            for field, operator, value in preset["conditions"]
        ]

        for condition in self.current_conditions:
            self.conditions_listbox.insert(
                tk.END,
                self.describe_condition(condition)
            )

    # =========================================================
    # CONDICIONES
    # =========================================================

    def update_operator_options(self, event=None):
        field_label = self.field_combo.get()
        field = FIELD_OPTIONS.get(field_label, "extension")

        operator_options = FIELD_TO_OPERATOR_OPTIONS.get(field, TEXT_OPERATORS)

        self.operator_combo.config(values=list(operator_options.keys()))
        self.operator_combo.set(list(operator_options.keys())[0])

        self.hint_label.config(text=FIELD_HINTS.get(field, ""))

    def add_condition(self):
        field_label = self.field_combo.get()
        operator_label = self.operator_combo.get()
        raw_value = self.value_entry.get().strip()

        field = FIELD_OPTIONS[field_label]
        operator = FIELD_TO_OPERATOR_OPTIONS[field][operator_label]

        if not raw_value:
            Messagebox.show_warning(
                "Escribe un valor para esta condición antes de agregarla.",
                "Falta el valor",
                parent=self
            )

            return

        if field in NUMERIC_FIELDS:
            try:
                value = float(raw_value)

            except ValueError:
                Messagebox.show_error(
                    f"'{raw_value}' no es un número.\n\n{FIELD_HINTS[field]}",
                    "Valor inválido",
                    parent=self
                )

                return

        else:
            value = raw_value

        condition = Condition(field, operator, value)

        self.current_conditions.append(condition)

        self.conditions_listbox.insert(
            tk.END,
            self.describe_condition(condition)
        )

        self.value_entry.delete(0, tk.END)

    def describe_condition(self, condition):
        field_label = REVERSE_FIELD.get(condition.field, condition.field)
        operator_label = REVERSE_OPERATOR.get(condition.operator, condition.operator)

        return f"El archivo {field_label.lower()} {operator_label} \"{condition.value}\""

    def remove_condition(self):
        selection = self.conditions_listbox.curselection()

        if not selection:
            Messagebox.show_info(
                "Haz clic sobre una condición de la lista para poder quitarla.",
                "Nada seleccionado",
                parent=self
            )

            return

        index = selection[0]

        self.conditions_listbox.delete(index)

        del self.current_conditions[index]

    # =========================================================
    # LISTA DE REGLAS
    # =========================================================

    def refresh_rules_list(self):
        self.rules_listbox.delete(0, tk.END)

        for rule in self.rules:
            status = "" if rule.enabled else " (inactiva)"

            self.rules_listbox.insert(
                tk.END,
                f"{rule.name}{status}"
            )

    def on_select_rule(self, event=None):
        selection = self.rules_listbox.curselection()

        if not selection:
            return

        index = selection[0]

        rule = self.rules[index]

        self.load_rule_into_form(rule, index)

    def load_rule_into_form(self, rule, index):
        self.editing_index = index

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, rule.name)

        self.destination_entry.delete(0, tk.END)
        self.destination_entry.insert(0, rule.destination_folder)

        self.logic_var.set(rule.logic)
        self.enabled_var.set(rule.enabled)

        self.current_conditions = list(rule.conditions)

        self.conditions_listbox.delete(0, tk.END)

        for condition in self.current_conditions:
            self.conditions_listbox.insert(
                tk.END,
                self.describe_condition(condition)
            )

    def new_rule(self):
        self.editing_index = None

        self.name_entry.delete(0, tk.END)
        self.destination_entry.delete(0, tk.END)

        self.logic_var.set("AND")
        self.enabled_var.set(True)

        self.current_conditions = []

        self.conditions_listbox.delete(0, tk.END)

        self.rules_listbox.selection_clear(0, tk.END)

    def save_rule(self):
        name = self.name_entry.get().strip()
        destination = self.destination_entry.get().strip()

        if not name:
            Messagebox.show_warning(
                "Ponle un nombre a la regla (paso 1).",
                "Falta el nombre",
                parent=self
            )

            return

        if not destination:
            Messagebox.show_warning(
                "Indica a qué carpeta se moverán los archivos (paso 2).",
                "Falta la carpeta destino",
                parent=self
            )

            return

        # Evitar nombres duplicados (sin contar la regla que se está editando)
        for index, existing_rule in enumerate(self.rules):
            if index == self.editing_index:
                continue

            if existing_rule.name.strip().lower() == name.lower():
                Messagebox.show_warning(
                    f"Ya existe una regla llamada '{existing_rule.name}'. "
                    "Usa otro nombre.",
                    "Nombre repetido",
                    parent=self
                )

                return

        if not self.current_conditions:
            Messagebox.show_warning(
                "Agrega al menos una condición (paso 3) para que la regla sepa qué archivos atrapar.",
                "Sin condiciones",
                parent=self
            )

            return

        rule = Rule(
            name=name,
            conditions=self.current_conditions,
            logic=self.logic_var.get(),
            destination_folder=destination,
            enabled=self.enabled_var.get()
        )

        if self.editing_index is not None:
            self.rules[self.editing_index] = rule

        else:
            self.rules.append(rule)

        save_rules(self.rules)

        self.refresh_rules_list()

        Messagebox.show_info(
            f"La regla '{name}' se guardó correctamente.",
            "Guardado",
            parent=self
        )

    def delete_rule(self):
        selection = self.rules_listbox.curselection()

        if not selection:
            Messagebox.show_warning(
                "Selecciona una regla de la lista para eliminarla.",
                "Sin selección",
                parent=self
            )

            return

        index = selection[0]
        rule_name = self.rules[index].name

        # Se usa el messagebox clásico de Tkinter aquí (no el de ttkbootstrap)
        # porque su valor de retorno es un booleano fijo (True/False) sin
        # importar el idioma del sistema — el de ttkbootstrap devuelve el
        # texto del botón, que cambia según el idioma de Windows.
        confirm = messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la regla '{rule_name}'?",
            parent=self
        )

        if not confirm:
            return

        del self.rules[index]

        save_rules(self.rules)

        self.refresh_rules_list()

        self.new_rule()
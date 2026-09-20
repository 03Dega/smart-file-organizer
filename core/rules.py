from datetime import datetime
from pathlib import Path

from core.file_manager import get_safe_destination


# =========================================================
# CAMPOS Y OPERADORES DISPONIBLES
# =========================================================

# Campos de texto: extension, name, category
# Operadores de texto: "==", "!=", "contains", "starts_with", "ends_with"

# Campos numéricos/fecha: size_mb, age_days, width, height, duration, fps
# Operadores numéricos: "<", "<=", ">", ">=", "=="

# width, height, duration y fps solo existen en archivos de Imagen/Audio/Video.
# Si el archivo no tiene ese dato (por ejemplo, un Documento no tiene "duration"),
# la condición simplemente no se cumple para ese archivo.


class Condition:
    """
    Una condición individual dentro de una regla.

    Ejemplos:
        Condition("extension", "==", ".pdf")
        Condition("size_mb", ">", 20)
        Condition("age_days", ">", 30)
        Condition("name", "contains", "factura")
        Condition("duration", "<", 60)
        Condition("width", ">=", 1920)
    """

    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value

    def to_dict(self):
        return {
            "field": self.field,
            "operator": self.operator,
            "value": self.value
        }

    @staticmethod
    def from_dict(data):
        return Condition(
            data["field"],
            data["operator"],
            data["value"]
        )


class Rule:
    """
    Una regla completa: condiciones + lógica + destino.

    logic: "AND" (todas las condiciones deben cumplirse)
           "OR"  (basta con que se cumpla una)
    """

    def __init__(self, name, conditions, logic, destination_folder, enabled=True):
        self.name = name
        self.conditions = conditions
        self.logic = logic.upper()
        self.destination_folder = destination_folder
        self.enabled = enabled

    def to_dict(self):
        return {
            "name": self.name,
            "conditions": [c.to_dict() for c in self.conditions],
            "logic": self.logic,
            "destination_folder": str(self.destination_folder),
            "enabled": self.enabled
        }

    @staticmethod
    def from_dict(data):
        return Rule(
            name=data["name"],
            conditions=[Condition.from_dict(c) for c in data["conditions"]],
            logic=data["logic"],
            destination_folder=data["destination_folder"],
            enabled=data.get("enabled", True)
        )


# =========================================================
# EXTRAER VALOR DE UN CAMPO CALCULADO
# =========================================================

def get_field_value(file, field):
    if field == "extension":
        return file["extension"]

    if field == "name":
        return file["name"]

    if field == "category":
        return file["category"]

    if field == "size_mb":
        return file["size"] / (1024 ** 2)

    if field == "age_days":
        modified = datetime.fromtimestamp(file["modified"])
        return (datetime.now() - modified).days

    if field == "width":
        return file.get("width")

    if field == "height":
        return file.get("height")

    if field == "duration":
        return file.get("duration")

    if field == "fps":
        return file.get("fps")

    raise ValueError(f"Campo desconocido: {field}")


# =========================================================
# EVALUAR UNA CONDICIÓN
# =========================================================

def evaluate_condition(file, condition):
    actual_value = get_field_value(file, condition.field)

    # Campos multimedia (width, height, duration, fps) pueden ser None
    # en archivos que no aplican (ej. un Documento no tiene "duration").
    # En ese caso, la condición no se cumple.
    if actual_value is None:
        return False

    operator = condition.operator
    expected_value = condition.value

    # Operadores de texto

    if operator == "==":
        if isinstance(actual_value, str):
            return actual_value.lower() == str(expected_value).lower()

        return actual_value == expected_value

    if operator == "!=":
        if isinstance(actual_value, str):
            return actual_value.lower() != str(expected_value).lower()

        return actual_value != expected_value

    if operator == "contains":
        return str(expected_value).lower() in str(actual_value).lower()

    if operator == "starts_with":
        return str(actual_value).lower().startswith(str(expected_value).lower())

    if operator == "ends_with":
        return str(actual_value).lower().endswith(str(expected_value).lower())

    # Operadores numéricos

    if operator == "<":
        return actual_value < expected_value

    if operator == "<=":
        return actual_value <= expected_value

    if operator == ">":
        return actual_value > expected_value

    if operator == ">=":
        return actual_value >= expected_value

    raise ValueError(f"Operador desconocido: {operator}")


# =========================================================
# EVALUAR UNA REGLA COMPLETA
# =========================================================

def evaluate_rule(file, rule):
    if not rule.enabled:
        return False

    if not rule.conditions:
        return False

    results = [
        evaluate_condition(file, condition)
        for condition in rule.conditions
    ]

    if rule.logic == "OR":
        return any(results)

    # Por defecto: "AND"
    return all(results)


# =========================================================
# ENCONTRAR LA PRIMERA REGLA QUE APLICA A UN ARCHIVO
# =========================================================

def find_matching_rule(file, rules):
    """
    Retorna la primera regla (en orden de la lista) que aplica al archivo,
    o None si ninguna aplica. El orden de las reglas importa: la primera
    que coincide gana.
    """

    for rule in rules:
        if evaluate_rule(file, rule):
            return rule

    return None


# =========================================================
# CONSTRUIR PLAN DE ORGANIZACIÓN BASADO EN REGLAS
# =========================================================

def build_rules_plan(analyzed_files, rules, base_folder):
    """
    Igual que build_organization_plan, pero usando reglas personalizadas
    en vez de categoría automática.

    Archivos que no coinciden con ninguna regla se omiten del plan
    (no se tocan).
    """

    base_folder = Path(base_folder)

    plan = []

    for file in analyzed_files:
        rule = find_matching_rule(file, rules)

        if rule is None:
            continue

        destination_folder = base_folder / rule.destination_folder

        destination_path = get_safe_destination(
            destination_folder,
            file["name"]
        )

        plan.append({
            "source": Path(file["path"]),
            "rule_name": rule.name,
            "destination_folder": destination_folder,
            "destination_path": destination_path
        })

    return plan
import json
from pathlib import Path

import sys

if getattr(sys, "frozen", False):
    # El programa está corriendo como .exe empaquetado (PyInstaller)
    BASE_DIR = Path(sys.executable).parent
else:
    # El programa está corriendo como script normal (python main.py)
    BASE_DIR = Path(__file__).parent

SETTINGS_PATH = BASE_DIR / "settings.json"


def load_settings():
    """
    Carga el archivo de configuración completo.
    Si no existe todavía, retorna una configuración vacía por defecto.
    """

    if not SETTINGS_PATH.exists():
        return {"rules": []}

    with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_settings(settings):
    """
    Guarda la configuración completa en disco.
    """

    with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4, ensure_ascii=False)


def load_rules():
    """
    Carga únicamente las reglas guardadas, ya convertidas a objetos Rule.
    """

    from core.rules import Rule

    settings = load_settings()

    return [Rule.from_dict(data) for data in settings.get("rules", [])]


def save_rules(rules):
    """
    Guarda la lista de reglas (objetos Rule), preservando el resto
    de la configuración existente.
    """

    settings = load_settings()

    settings["rules"] = [rule.to_dict() for rule in rules]

    save_settings(settings)
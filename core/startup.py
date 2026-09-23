import sys
import winreg
from pathlib import Path

APP_NAME = "SmartFileOrganizer"
REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _get_startup_command():
    """
    Arma el comando que Windows debe ejecutar al iniciar sesión.

    Si la app corre como .exe empaquetado, usa esa misma ruta.
    Si corre como script (durante desarrollo), usa pythonw.exe (sin
    consola) apuntando a main.py.
    """

    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    python_exe = Path(sys.executable).parent / "pythonw.exe"
    main_script = Path(__file__).parent.parent / "main.py"

    return f'"{python_exe}" "{main_script}"'


def is_startup_enabled():
    """
    Retorna True si la app ya está configurada para iniciar con Windows.
    """

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_READ
        ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True

    except FileNotFoundError:
        return False


def enable_startup():
    """
    Agrega la app al inicio automático de Windows para el usuario actual.
    """

    command = _get_startup_command()

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        REGISTRY_PATH,
        0,
        winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)


def disable_startup():
    """
    Quita la app del inicio automático de Windows.
    """

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_PATH,
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, APP_NAME)

    except FileNotFoundError:
        pass
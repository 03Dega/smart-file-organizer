import json
import urllib.request

from core.version import APP_VERSION

# TODO: cuando tengas un repositorio en GitHub, reemplaza esta URL por la
# ruta "raw" de tu propio archivo version.json. Instrucciones al final.
UPDATE_INFO_URL = "https://raw.githubusercontent.com/TU_USUARIO/TU_REPO/main/version.json"


def check_for_updates():
    """
    Consulta UPDATE_INFO_URL, que debe ser un JSON público con este formato:

        {
            "version": "4.1.0",
            "download_url": "https://github.com/TU_USUARIO/TU_REPO/releases/latest",
            "notes": "Descripción breve de los cambios de esta versión"
        }

    Retorna:
        None  -> si ya tienes la última versión, no hay conexión a internet,
                 o el archivo todavía no existe (ej. URL de ejemplo sin configurar).
        dict  -> con la info de la nueva versión, si hay una disponible.
    """

    try:
        with urllib.request.urlopen(UPDATE_INFO_URL, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        remote_version = data.get("version", "0.0.0")

        if _is_newer(remote_version, APP_VERSION):
            return data

        return None

    except Exception:
        return None


def _is_newer(remote, current):
    """
    Compara dos versiones tipo "4.1.0" sin depender de librerías externas.
    """

    try:
        remote_parts = [int(part) for part in remote.split(".")]
        current_parts = [int(part) for part in current.split(".")]

        return remote_parts > current_parts

    except Exception:
        return False
from pathlib import Path


def scan_folder(folder_path, recursive=False, excluded_dir_names=None):
    """
    Analiza una carpeta y devuelve los archivos encontrados.

    recursive=False (por defecto): solo el primer nivel, como antes.
    recursive=True: entra a las subcarpetas también.

    excluded_dir_names: nombres de subcarpeta (sin importar mayúsculas)
    que se deben ignorar por completo al escanear en modo recursivo.
    Se usa para no volver a organizar carpetas que el propio programa
    ya creó como destino (ej. "Imágenes", "Videos Cortos").

    No modifica, mueve ni elimina ningún archivo.
    """

    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError("La carpeta indicada no existe.")

    if not folder.is_dir():
        raise NotADirectoryError("La ruta indicada no es una carpeta.")

    if not recursive:
        return [item for item in folder.iterdir() if item.is_file()]

    excluded = {name.lower() for name in (excluded_dir_names or [])}

    files = []

    for item in folder.rglob("*"):
        if item.is_dir():
            continue

        relative_parts = item.relative_to(folder).parts[:-1]

        if any(part.lower() in excluded for part in relative_parts):
            continue

        files.append(item)

        return files
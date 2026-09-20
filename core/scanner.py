from pathlib import Path


def scan_folder(folder_path):
    """
    Analiza una carpeta y devuelve los archivos encontrados.

    No modifica, mueve ni elimina ningún archivo.
    """

    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError("La carpeta indicada no existe.")

    if not folder.is_dir():
        raise NotADirectoryError("La ruta indicada no es una carpeta.")

    files = []

    for item in folder.iterdir():
        if item.is_file():
            files.append(item)

    return files
from pathlib import Path


# Extensiones de imágenes
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
    ".tiff",
    ".svg",
    ".ico",
}


# Extensiones de videos
VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".webm",
    ".flv",
    ".m4v",
}


# Extensiones de audio
AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".flac",
    ".aac",
    ".m4a",
    ".ogg",
    ".wma",
}


# Extensiones de documentos
DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".rtf",
    ".odt",
    ".xls",
    ".xlsx",
    ".csv",
    ".ppt",
    ".pptx",
    ".odp",
}


# Extensiones de archivos comprimidos
ARCHIVE_EXTENSIONS = {
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".bz2",
}


# Extensiones de instaladores
INSTALLER_EXTENSIONS = {
    ".exe",
    ".msi",
}


def classify_file(file_path):
    """
    Determina la categoría de un archivo según su extensión.

    Retorna:
        Imagen
        Video
        Audio
        Documento
        Comprimido
        Instalador
        Otro
    """

    file = Path(file_path)

    extension = file.suffix.lower()

    if extension in IMAGE_EXTENSIONS:
        return "Imagen"

    if extension in VIDEO_EXTENSIONS:
        return "Video"

    if extension in AUDIO_EXTENSIONS:
        return "Audio"

    if extension in DOCUMENT_EXTENSIONS:
        return "Documento"

    if extension in ARCHIVE_EXTENSIONS:
        return "Comprimido"

    if extension in INSTALLER_EXTENSIONS:
        return "Instalador"

    return "Otro"

import shutil


# Nombres de carpeta por categoría
CATEGORY_FOLDER_NAMES = {
    "Imagen": "Imágenes",
    "Video": "Videos",
    "Audio": "Audio",
    "Documento": "Documentos",
    "Comprimido": "Comprimidos",
    "Instalador": "Instaladores",
    "Otro": "Otros",
}


def get_safe_destination(destination_folder, filename):
    """
    Calcula una ruta de destino que nunca sobrescribe un archivo existente.

    Si "foto.jpg" ya existe, prueba "foto (1).jpg", "foto (2).jpg", etc.
    """

    destination_folder = Path(destination_folder)

    candidate = destination_folder / filename

    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix

    counter = 1

    while True:
        new_name = f"{stem} ({counter}){suffix}"

        candidate = destination_folder / new_name

        if not candidate.exists():
            return candidate

        counter += 1


def build_organization_plan(analyzed_files, base_folder):
    """
    Construye un plan de organización sin mover nada todavía.

    Retorna una lista de diccionarios:
        {
            "source": Path,
            "category": str,
            "destination_folder": Path,
            "destination_path": Path
        }
    """

    base_folder = Path(base_folder)

    plan = []

    for file in analyzed_files:
        category = file["category"]

        folder_name = CATEGORY_FOLDER_NAMES.get(category, "Otros")

        destination_folder = base_folder / folder_name

        destination_path = get_safe_destination(
            destination_folder,
            file["name"]
        )

        plan.append({
            "source": Path(file["path"]),
            "category": category,
            "destination_folder": destination_folder,
            "destination_path": destination_path
        })

    return plan


def execute_plan(plan):
    """
    Ejecuta un plan de organización: crea carpetas y mueve archivos.

    No sobrescribe archivos existentes (el plan ya reserva nombres únicos).

    Retorna:
        {
            "moved": [...],
            "errors": [{"source": Path, "error": str}, ...]
        }
    """

    moved = []

    errors = []

    for item in plan:
        try:
            item["destination_folder"].mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.move(
                str(item["source"]),
                str(item["destination_path"])
            )

            moved.append(item)

        except Exception as error:
            errors.append({
                "source": item["source"],
                "error": str(error)
            })

    return {
        "moved": moved,
        "errors": errors
    }
from collections import Counter

from core.scanner import scan_folder
from core.file_manager import classify_file, CATEGORY_FOLDER_NAMES
from analyzers.image_analyzer import get_image_resolution
from analyzers.audio_analyzer import get_audio_duration
from analyzers.video_analyzer import get_video_info


def analyze_file(file_path):
    """
    Analiza un único archivo y retorna su información completa:
    nombre, extensión, categoría, tamaño, fecha de modificación y,
    según la categoría, resolución/duración/fps.

    Se usa tanto en analyze_folder() como en la vigilancia automática
    de carpetas (core/watcher.py), para no duplicar esta lógica.
    """

    category = classify_file(file_path)

    width = None
    height = None
    duration = None
    fps = None

    if category == "Imagen":
        resolution = get_image_resolution(file_path)

        if resolution is not None:
            width, height = resolution

    elif category == "Audio":
        duration = get_audio_duration(file_path)

    elif category == "Video":
        video_info = get_video_info(file_path)

        if video_info is not None:
            duration = video_info["duration"]
            width = video_info["width"]
            height = video_info["height"]
            fps = video_info["fps"]

    return {
        "path": file_path,
        "name": file_path.name,
        "extension": file_path.suffix.lower(),
        "category": category,
        "size": file_path.stat().st_size,
        "modified": file_path.stat().st_mtime,
        "width": width,
        "height": height,
        "duration": duration,
        "fps": fps
    }


def _get_excluded_dir_names():
    """
    Nombres de carpeta que el escaneo recursivo debe evitar: las carpetas
    de categoría por defecto (Imágenes, Videos, etc.) más las carpetas
    destino de las reglas guardadas por el usuario. Así el escaneo
    recursivo no vuelve a meterse a organizar lo que ya organizó antes.
    """

    excluded = list(CATEGORY_FOLDER_NAMES.values())

    try:
        from config.settings import load_rules

        rules = load_rules()

        excluded += [rule.destination_folder for rule in rules]

    except Exception:
        pass  # Si no se pueden cargar las reglas, se sigue solo con las de categoría

    return excluded


def analyze_folder(folder_path, recursive=False):
    """
    Analiza una carpeta y clasifica los archivos encontrados.

    recursive=True incluye subcarpetas, excluyendo automáticamente las
    carpetas que el propio programa usa como destino de organización.

    No mueve, copia ni elimina archivos.
    """

    excluded_dir_names = _get_excluded_dir_names() if recursive else None

    files = scan_folder(
        folder_path,
        recursive=recursive,
        excluded_dir_names=excluded_dir_names
    )

    return [analyze_file(file) for file in files]


def generate_statistics(analyzed_files):
    """
    Genera estadísticas según las categorías de los archivos.
    """

    statistics = Counter()

    for file in analyzed_files:
        statistics[file["category"]] += 1

    return statistics
from collections import Counter

from core.scanner import scan_folder
from core.file_manager import classify_file
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


def analyze_folder(folder_path):
    """
    Analiza una carpeta y clasifica los archivos encontrados.

    No mueve, copia ni elimina archivos.
    """

    files = scan_folder(folder_path)

    return [analyze_file(file) for file in files]


def generate_statistics(analyzed_files):
    """
    Genera estadísticas según las categorías de los archivos.
    """

    statistics = Counter()

    for file in analyzed_files:
        statistics[file["category"]] += 1

    return statistics
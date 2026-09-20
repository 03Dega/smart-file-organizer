from PIL import Image


def get_image_resolution(file_path):
    """
    Retorna la resolución de una imagen como (ancho, alto) en píxeles.

    Retorna None si el archivo no se puede leer como imagen
    (por ejemplo, si está corrupto o no es una imagen real).
    """

    try:
        with Image.open(file_path) as image:
            return image.size  # (ancho, alto)

    except Exception:
        return None
from mutagen import File as MutagenFile


def get_audio_duration(file_path):
    """
    Retorna la duración de un archivo de audio en segundos (float).

    Retorna None si el archivo no se puede leer o no tiene
    información de duración.
    """

    try:
        audio = MutagenFile(file_path)

        if audio is None or audio.info is None:
            return None

        return audio.info.length

    except Exception:
        return None

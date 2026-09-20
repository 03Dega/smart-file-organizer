import json
import subprocess


def get_video_info(file_path):
    """
    Retorna un diccionario con:
        duration -> segundos (float)
        width    -> píxeles (int)
        height   -> píxeles (int)
        fps      -> cuadros por segundo (float)

    Usa ffprobe, que viene incluido con FFmpeg.

    Retorna None si FFmpeg/ffprobe no está instalado, no está en el
    PATH del sistema, o el archivo no se puede leer.
    """

    try:
        command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate:format=duration",
            "-of", "json",
            str(file_path)
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)

        if not data.get("streams"):
            return None

        stream = data["streams"][0]

        duration = float(data["format"]["duration"])
        width = stream.get("width")
        height = stream.get("height")


                # Preferimos avg_frame_rate (framerate real promedio); r_frame_rate a veces
        # refleja el timebase interno del stream y no el framerate real.
        fps_raw = stream.get("avg_frame_rate", "0/1")

        if fps_raw == "0/0":
            fps_raw = stream.get("r_frame_rate", "0/1")

        numerator, denominator = fps_raw.split("/")

        fps = float(numerator) / float(denominator) if float(denominator) != 0 else None

        return {
            "duration": duration,
            "width": width,
            "height": height,
            "fps": fps
        }

    except Exception:
        return None

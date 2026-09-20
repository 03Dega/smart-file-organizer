from core.analyzer import analyze_folder

files = analyze_folder("D:/prueba de organizador")

for file in files:
    print(f"\n{file['name']} ({file['category']})")
    print(f"  Tamaño: {file['size']} bytes")

    if file["category"] == "Imagen":
        print(f"  Resolución: {file['width']}x{file['height']}")

    elif file["category"] == "Audio":
        print(f"  Duración: {file['duration']} segundos")

    elif file["category"] == "Video":
        print(f"  Duración: {file['duration']} segundos")
        print(f"  Resolución: {file['width']}x{file['height']}")
        print(f"  FPS: {file['fps']}")
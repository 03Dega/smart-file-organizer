from collections import Counter


def generate_statistics(files):
    """
    Genera estadísticas de los archivos encontrados.

    Recibe una lista de archivos y devuelve
    la cantidad de archivos por categoría.
    """

    categories = []

    for file in files:
        categories.append(file["category"])

    statistics = Counter(categories)

    return statistics
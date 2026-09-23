import sys


def run_headless_organize(folder_path):
    """
    Organiza una carpeta según las reglas guardadas, sin abrir la interfaz
    gráfica. Pensado para ser invocado por una tarea programada de Windows.
    """

    from core.analyzer import analyze_folder
    from core.rules import build_rules_plan
    from core.file_manager import execute_plan
    from config.settings import load_rules

    try:
        from plyer import notification
        notifications_available = True
    except Exception:
        notifications_available = False

    rules = load_rules()

    if not rules:
        return

    analyzed_files = analyze_folder(folder_path)

    plan = build_rules_plan(analyzed_files, rules, folder_path)

    if not plan:
        return

    result = execute_plan(plan)

    if notifications_available:
        try:
            notification.notify(
                title="Smart File Organizer",
                message=(
                    f"Tarea programada: {len(result['moved'])} archivo(s) "
                    f"organizado(s) en '{folder_path}'."
                ),
                app_name="Smart File Organizer",
                timeout=6
            )
        except Exception:
            pass


def main():
    if "--auto-organize" in sys.argv:
        index = sys.argv.index("--auto-organize")

        if index + 1 < len(sys.argv):
            run_headless_organize(sys.argv[index + 1])

        return

    from ui.main_window import start_application

    start_application()


if __name__ == "__main__":
    main()
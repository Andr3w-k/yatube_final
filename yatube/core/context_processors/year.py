from datetime import datetime


def year(request) -> int:
    """Добавляет переменную с текущим годом."""
    currentYear = datetime.now().year
    return {
        "year": int(currentYear),
    }

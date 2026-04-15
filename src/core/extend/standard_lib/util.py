import os

from config import global_storage


def path_normpath(path: str) -> str:
    # Формируем полный путь относительно рабочей директории
    # Если путь абсолютный, os.path.join корректно его обработает
    full_path = os.path.join(global_storage.LW_SCRIPT_DIR, path)

    # Нормализуем путь (убираем ../, ./ и т.д.)
    return os.path.normpath(full_path)

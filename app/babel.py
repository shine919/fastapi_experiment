from pathlib import Path

from fastapi_babel import Babel, BabelConfigs

# Создаем объект конфигурации для Babel:
babel_configs = BabelConfigs(
    ROOT_DIR=Path(__file__).resolve().parent,
    BABEL_DEFAULT_LOCALE="en",  # Язык по умолчанию
    BABEL_TRANSLATION_DIRECTORY="locales",  # Папка с переводами
)


# Инициализируем объект Babel с использованием конфигурации
babel = Babel(configs=babel_configs)





# FASTAPI BABEL
Настройка 

# Конфигурация

babel_configs = BabelConfigs( 

    ROOT_DIR=Path(__file__).resolve().parent, #Путь папки

    BABEL_DEFAULT_LOCALE="en",# Язык по умолчанию

    BABEL_TRANSLATION_DIRECTORY="locales"# Папка с переводами
)

# Инициализируем объект Babel с использованием конфигурации
babel = Babel(configs=babel_configs)

# Добавляем мидлварь, который будет устанавливать локаль для каждого запроса
app.add_middleware(BabelMiddleware, babel_configs=babel_configs)

# Шаги

1.pybabel extract -o messages.pot . 

2.pybabel init -i messages.pot -d locales -l en -D messages 

  pybabel init -i messages.pot -d locales -l ru -D messages 

3.меняем в файле messages.po mgstr на нужную локализацию 

4.После внесения изменений в файлы .po выполните команду для компиляции переводов: pybabel compile -d locales -D messages

# При добавлении новых строк в код

1.pybabel extract -o messages.pot .

2.pybabel update -i messages.pot -d locales -D messages

3.Внесите изменения в файлы .po

4.pybabel compile -d locales -D messages
# Примечание

Переводы хранятся в папке locales, структура которой должна соответствовать стандарту gettext.

После изменения файлов .po всегда необходимо выполнять команду pybabel compile -d locales -D messages, чтобы обновить скомпилированные переводы.

Мидлварь BabelMiddleware автоматически определяет язык ответа на основе заголовка Accept-Language. При необходимости можно настроить другой способ выбора языка.

Для продакшена рекомендуется добавить кэширование переводов, чтобы уменьшить нагрузку.


# Запуск тестов
Для запуска всех тестов проекта выполните команду:

pytest

Дополнительные полезные команды:

Запустить тесты из конкретного файла:

pytest tests/test_main.py
Остановиться на первом упавшем тесте:

pytest -x

Перезапустить только упавшие тесты:

pytest --lf

Запуск тестов, измененных с последнего коммита (если установлен pytest-xdist):

pytest --last-failed

Запуск тестов с измерением времени выполнения:

pytest --durations=5

Пропуск тестов с определенной меткой (например, медленных):

pytest -m "not slow"


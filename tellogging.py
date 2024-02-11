import logging

from tg_logger import setup as tg_setup

# Определение пользовательского уровня логирования для сообщений Telegram
TELEGA_LEVEL = 25  # Уровень между INFO (20) и WARNING (30)
logging.addLevelName(TELEGA_LEVEL, "TELEGA")


def telega(self, message, *args, **kwargs):
    if self.isEnabledFor(TELEGA_LEVEL):
        self._log(TELEGA_LEVEL, message, args, **kwargs)


# Добавление метода telega к классу Logger
logging.Logger.telega = telega


class TelegramHandler(logging.Handler):
    def __init__(self, token, users):
        super().__init__()
        self.token = token
        self.users = users
        self.is_logging_exception = False  # Флаг для предотвращения рекурсии

    def emit(self, record):
        if self.is_logging_exception:
            return  # Прекращаем обработку, если уже логгируем исключение

        try:
            self.is_logging_exception = True
            # Ваш код для отправки сообщения через Telegram API
        except Exception as e:
            # Обработка исключения без вызова дополнительного логгирования
            pass
        finally:
            self.is_logging_exception = False


# Обновление функции setup_logger для использования нового TelegramHandler
def setup_logger(token: str, users: list, logger_name: str = None):
    base_logger = logging.getLogger(logger_name)
    base_logger.setLevel(logging.ERROR)

    # Настройка и добавление обработчика Telegram
    tg_handler = tg_setup(
        base_logger=base_logger,
        token=token,
        users=users,
        timeout=10,
        tg_format="<b>%(name)s:%(levelname)s</b> - <code>%(message)s</code>",
    )
    base_logger.addHandler(tg_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    base_logger.addHandler(console_handler)

    return base_logger

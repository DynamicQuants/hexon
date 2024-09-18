import logging

from colorama import Fore, Style, init

from .singleton import Singleton

# Reset the colorama style.
init(autoreset=True)


class _LoggerConfig(logging.Formatter):
    def format(self, record: logging.LogRecord):
        log_colors = {
            logging.DEBUG: Fore.BLUE,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.RED + Style.BRIGHT,
        }
        level_color = log_colors.get(record.levelno, "")
        message = super().format(record)
        return f"{level_color}{message}{Style.RESET_ALL}"


@Singleton
class _Logger:
    """Provides a simple colored console logger."""

    def __init__(self):
        self.logger = logging.getLogger("colored_logger")
        handler = logging.StreamHandler()
        formatter = _LoggerConfig("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)


Logger = _Logger()
"""Singleton console colored logger."""

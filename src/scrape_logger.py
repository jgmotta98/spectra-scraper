import logging
from enum import Enum
from typing import Optional

class LoggerLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class Logger:
    def __init__(self, logger_level: Optional[LoggerLevel] = LoggerLevel.INFO,
                 write_logger: Optional[bool] = False,
                 written_logger_path: Optional[str] = 'spectral_data.log'):
        
        self.logger_level = logger_level
        self.write_logger = write_logger
        self.written_logger_path = written_logger_path
        self.logger = logging.getLogger('MyLogger')

    def log_config(self) -> None:
        logging.basicConfig(
            format='\033[92m%(asctime)s - %(levelname)s - %(message)s\033[0m',
            level=self.logger_level.value
        )

        if self.write_logger:
            file_handler = logging.FileHandler(self.written_logger_path)
            file_handler.setLevel(self.logger_level.value)
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def log(self, message: str, 
            level: Optional[LoggerLevel]=LoggerLevel.INFO) -> None:
        log_method = getattr(self.logger, level.name.lower())
        log_method(message)
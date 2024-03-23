import logging
from typing import Optional

class Logger:
    def __init__(self, logger_level: Optional[int] = logging.INFO,
                 write_logger: Optional[bool] = False,
                 written_logger_path: Optional[str] = 'spectral_data.log'):
        
        self.logger_level = logger_level
        self.write_logger = write_logger
        self.written_logger_path = written_logger_path
        self.logger = logging.getLogger('Scrape_logger')
        self.log_colors = {
            logging.DEBUG: '\033[94m',
            logging.INFO: '\033[92m',
            logging.WARNING: '\033[93m',
            logging.ERROR: '\033[91m',
            logging.CRITICAL: '\033[91m',
        }
        self.log_config()

    def log_config(self) -> None:
        logging.basicConfig(
            format='%(color_code)s%(asctime)s - %(levelname)s - %(message)s\033[0m',
            level=self.logger_level
        )

        if self.write_logger:
            file_handler = logging.FileHandler(self.written_logger_path)
            file_handler.setLevel(self.logger_level)
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def log(self, message: str, 
            level: Optional[int]=logging.INFO) -> None:
        
        log_method = getattr(self.logger, logging.getLevelName(level).lower())
        color_code = self.log_colors.get(level, '')
        log_method(message, extra={'color_code': color_code})
        
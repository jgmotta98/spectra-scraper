from src.sdbs_data_extractor import SDBSDataExtractor
from src.sdbs_page_scraper import SDBSPageScraper
from src.specta_mod import SpectraMod
from src.scrape_logger import Logger, LoggerLevel
import subprocess
import os
import logging

#Change according to your path
DATABASE_PATH = '.\\IR_spectral_data\\comp_sdbs_no.csv'
TESSERACT_PATH = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
CONCURRENT_BROWSERS = 5

logger = Logger(LoggerLevel.INFO, 
                write_logger=True,
                written_logger_path='.\\IR_spectral_data\\spectral_data.log')
logger.log_config()

def main() -> None:
    SDBSDataExtractor(DATABASE_PATH, TESSERACT_PATH).run()
    logger.log('Extraction complete!')
    
    SDBSPageScraper(DATABASE_PATH, CONCURRENT_BROWSERS).run()
    logger.log("Scraping complete!")
    
    SpectraMod().run()
    logger.log("Image mod complete!")
    
    os.chdir('.\\src')
    subprocess.check_call(['npm', 'start'], shell=True)
    logger.log("All files were added to the database!")

if __name__ == "__main__":
    main()
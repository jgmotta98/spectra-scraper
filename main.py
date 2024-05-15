import logging
import os
import subprocess

from src.scrape_logger import Logger
from src.sdbs_data_extractor import SDBSDataExtractor
from src.sdbs_page_scraper import SDBSPageScraper
from src.specta_mod import SpectraMod
from src.store_database import create_database

#Change according to your path
DATABASE_PATH = '.\\IR_spectral_data\\comp_sdbs_no.csv'
FINAL_DATABASE_PATH = '.\\IR_spectral_data\\spectral_database.db'
CSV_PATH = '.\\IR_spectral_data\\img_output_data'
TESSERACT_PATH = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
CONCURRENT_BROWSERS = 5

LOGGER = Logger(logging.INFO, 
                write_logger=True,
                written_logger_path='.\\IR_spectral_data\\spectral_data.log')

def main() -> None:
    SDBSDataExtractor(DATABASE_PATH, TESSERACT_PATH, LOGGER).run()
    LOGGER.log('Extraction complete!')
    
    SDBSPageScraper(DATABASE_PATH, CONCURRENT_BROWSERS, LOGGER).run()
    LOGGER.log("Scraping complete!")
    
    SpectraMod(LOGGER).run()
    LOGGER.log("Image mod complete!")
    
    os.chdir('.\\src')
    subprocess.check_call(['npm', 'start'], shell=True)
    LOGGER.log("Files data extracted!")

    create_database(FINAL_DATABASE_PATH, CSV_PATH)
    LOGGER.log("All files were added to the database!")

if __name__ == "__main__":
    main()
    
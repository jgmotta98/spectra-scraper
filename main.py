from src.sdbs_data_extractor import SDBSDataExtractor
from src.sdbs_page_scraper import SDBSPageScraper
from src.specta_mod import SpectraMod
import subprocess
import os
import logging

#Change according to your path
DATABASE_PATH = '.\\IR_spectral_data\\comp_sdbs_no.csv'
TESSERACT_PATH = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
CONCURRENT_BROWSERS = 5

# Configuring basic logging
logging.basicConfig(
    format='\033[92m%(asctime)s - %(levelname)s - %(message)s\033[0m',
    level=logging.INFO
)

def main() -> None:
    '''SDBSDataExtractor(DATABASE_PATH, TESSERACT_PATH).run()
    logging.info('Extraction complete!')'''
    
    SDBSPageScraper(DATABASE_PATH, CONCURRENT_BROWSERS).run()
    logging.info("Scraping complete!")
    
    SpectraMod().run()
    logging.info("Image mod complete!")
    
    os.chdir('.\\src')
    subprocess.check_call(['npm', 'start'], shell=True)
    logging.info("All files were added to the database!")

if __name__ == "__main__":
    main()
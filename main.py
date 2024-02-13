from files.sdbs_data_extractor import SDBSDataExtractor
from files.sdbs_page_scraper import SDBSPageScraper
from files.specta_mod import SpectraMod
from files.sdbs_automatic_data_extractor import SDBSAutomaticDataExtractor
import subprocess
import os

#Change according to your path
DATABASE_PATH = '.\\IR_spectral_data\\comp_sdbs_no.csv'
TESSERACT_PATH = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
AUTO_EXTRACTOR_PATH = '' #In progress

if __name__ == "__main__":
    is_manual = input('Use the manual extraction? (y/n): ')
    if is_manual == 'y':
        SDBSDataExtractor(DATABASE_PATH, TESSERACT_PATH).run()
    else:
        pass
        #SDBSAutomaticDataExtractor(DATABASE_PATH, AUTO_EXTRACTOR_PATH).run()
    SDBSPageScraper(DATABASE_PATH).run()
    SpectraMod().run()
    os.chdir('.\\files')
    subprocess.check_call(['npm', 'start'], shell=True)
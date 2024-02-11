from sdbs_data_extractor import SDBSDataExtractor
from sdbs_page_scraper import SDBSPageScraper
from specta_mod import SpectraMod
import subprocess

#Change according to your path
DATABASE_PATH = '..\\IR_spectral_data\\comp_sdbs_no.csv'
TESSERACT_PATH = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

if __name__ == "__main__":
    is_manual = input('Use the manual extraction? (y/n): ')
    if is_manual == 'y':
        SDBSDataExtractor(DATABASE_PATH, TESSERACT_PATH).run()
    SDBSPageScraper(DATABASE_PATH).run()
    SpectraMod().run()
    subprocess.check_call(['npm', 'start'], shell=True)
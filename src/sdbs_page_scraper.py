from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
import re
from safeloader import Loader

#TODO: implement paralelism.

class SDBSPageScraper:

    def __init__(self, database_path: str) -> None:

        # Chrome arguments can be further modified.
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('log-level=2')
        chrome_options.add_argument("start-maximized")
        chrome_options.set_capability("browserVersion", "117") # New versions of chrome for some reason dont remove dev logs.
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # Removes annoying dev logs.
        
        self.wd = webdriver.Chrome(options=chrome_options)
        self.database_path = database_path
        current_dir = os.path.dirname(__file__)
        self.spectral_path = os.path.join(current_dir, '..', 'IR_spectral_data', 'img_data')
        self.spectral_path = os.path.normpath(self.spectral_path)
        self.base_url_img = "https://sdbs.db.aist.go.jp/sdbs/cgi-bin/IMG.cgi?imgdir=ir&amp;fname=NIDA"
        self.base_url = "https://sdbs.db.aist.go.jp/sdbs/cgi-bin/landingpage?sdbsno="
        self.agree_clicked = False
        self.page_scraper_loader = Loader(desc='Downloading images')

    def _get_nida(self, wd: webdriver) -> str | None:
        try:
            ir_elements = WebDriverWait(wd, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(), 'IR')]")))
            for element in ir_elements:
                match = re.search(r'NIDA-(\d+)', element.text)
                if match:
                    nida_number = re.sub(r'^0+', '', str(match.group(1)))
                    return nida_number
            return None
        except Exception as e:
            print(f"Error in get_nida: {e}")
            return None
        
    def _capture_screenshot(self, name: str, nida_val: str) -> str | None:
        url_img = self.base_url_img + str(nida_val)
        self.wd.get(url_img)
        file_path = os.path.join(self.spectral_path, f"{name}.png")
        try:
            image_element = WebDriverWait(self.wd, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            ActionChains(self.wd).move_to_element(image_element).perform()
            WebDriverWait(self.wd, 10).until(lambda d: image_element.get_attribute('complete'))
            image_element.screenshot(file_path)
            return 'complete'
        except Exception as e:
            print(f"Error capturing screenshot for {name}: {e}")
            return None
        
    def _navigate_and_agree(self, url: str) -> None:
        self.wd.get(url)
        if not self.agree_clicked:
            try:
                agree_button = WebDriverWait(self.wd, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "agree_button")))
                agree_button.click()
                self.agree_clicked = True
                self.wd.get(url)
            except Exception as e:
                print(f"Could not find or click agree button: {e}")

    def _scrape_info(self, row) -> str | None:
        number, name, is_complete = row['number'], '_' + re.sub(r'[-.,]', '_', row['comp_name']), row['completion']
        files_from_folder = [file_name[:-4] for file_name in os.listdir(self.spectral_path)]
        if is_complete == "incomplete" and name not in files_from_folder:
            url = self.base_url + str(number)
            self._navigate_and_agree(url)
            nida_val = self._get_nida(self.wd)
            if nida_val:
                return self._capture_screenshot(name, nida_val)
            else:
                print(f"NIDA value not found for {name}")
                return None
        return 'complete'

    def _set_database_link(self) -> None:
        database_df = pd.read_csv(self.database_path, delimiter=';')
        database_df['completion'] = database_df.apply(self._scrape_info, axis=1)
        database_df.to_csv(self.database_path, sep=';', index=False)

    def run(self) -> None:
        self.page_scraper_loader.start()
        self._set_database_link()
        self.wd.quit()
        self.page_scraper_loader.stop()
    

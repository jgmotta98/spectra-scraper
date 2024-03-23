import logging
import os
import re
from typing import List, Callable, Union

import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from safeloader import Loader
from src.scrape_logger import Logger

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class SDBSPageScraper:

    def __init__(self, database_path: str, chrome_instances: int, logger_config: Logger):
        self.logger_config = logger_config
        self.database_path = database_path
        current_dir = os.path.dirname(__file__)
        self.spectral_path = os.path.join(current_dir, '..', 'IR_spectral_data', 'img_data')
        self.spectral_path = os.path.normpath(self.spectral_path)
        self.base_url_img = "https://sdbs.db.aist.go.jp/sdbs/cgi-bin/IMG.cgi?imgdir=ir&amp;fname=NIDA"
        self.base_url = "https://sdbs.db.aist.go.jp/sdbs/cgi-bin/landingpage?sdbsno="
        self.agree_clicked = False
        self.chrome_instances = chrome_instances
        self.page_scraper_loader = Loader(desc='Downloading images')

    def _get_nida(self, wd: ChromeWebDriver) -> Union[str, None]:
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
        
    def _capture_screenshot(self, name: str, nida_val: str, wd: ChromeWebDriver) -> None:
        url_img = self.base_url_img + str(nida_val)
        wd.get(url_img)
        file_path = os.path.join(self.spectral_path, f"{name}.png")
        try:
            image_element = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            ActionChains(wd).move_to_element(image_element).perform()
            WebDriverWait(wd, 10).until(lambda d: image_element.get_attribute('complete'))
            image_element.screenshot(file_path)
        except Exception as e:
            print(f"Error capturing screenshot for {name}: {e}")
        
    def _navigate_and_agree(self, url: str, wd: ChromeWebDriver) -> None:
        wd.get(url)
        if not self.agree_clicked:
            try:
                agree_button = WebDriverWait(wd, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "agree_button")))
                agree_button.click()
                self.agree_clicked = True
                wd.get(url)
            except Exception as e:
                print(f"Could not find or click agree button: {e}")

    def _scrape_info(self, row: pd.Series, wd: ChromeWebDriver) -> None:
        number, name = row['number'], row['comp_name']
        files_from_folder = [file_name[:-4] for file_name in os.listdir(self.spectral_path)]
        if name not in files_from_folder:
            url = self.base_url + str(number)
            self._navigate_and_agree(url, wd)
            nida_val = self._get_nida(wd)
            if nida_val:
                self._capture_screenshot(f'[{number}]{name}', nida_val, wd)
            else:
                print(f"NIDA value not found for {name}")

    @staticmethod
    def _open_browser(scrape_function: Callable[[pd.Series, ChromeWebDriver], None], dataframe: pd.DataFrame) -> None:
        # Chrome arguments can be further modified.
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('log-level=2')
        chrome_options.add_argument("start-maximized")
        chrome_options.set_capability("browserVersion", "117") # New versions of chrome for some reason dont remove dev logs.
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # Removes annoying dev logs.
        wd = webdriver.Chrome(options=chrome_options)
        dataframe = dataframe.apply(scrape_function, args=(wd,) , axis=1)
        wd.quit()

    def _database_search(self, database_list: List[pd.DataFrame]) -> None:

        with ThreadPoolExecutor(max_workers=self.chrome_instances) as executor:
            futures = [executor.submit(self._open_browser, self._scrape_info, df) for df in database_list[:self.chrome_instances]]

            for future in futures:
                future.result()

    def _check_for_saved_files(self, row: pd.Series) -> pd.Series:

        if f'[{row['number']}]{row['comp_name']}.png' in os.listdir(self.spectral_path):
            row['number'], row['comp_name'] = None, None
        return row

    def _open_and_divide_instances(self) -> List[pd.DataFrame]:
        database_df = pd.read_csv(self.database_path, delimiter=';')

        database_df = database_df.apply(self._check_for_saved_files, axis=1)
        database_df = database_df.dropna()
        database_df.reset_index(drop=True, inplace=True)
        if not database_df.empty:
            database_df['number'] = database_df['number'].astype(int)

        num_rows = len(database_df)
        if num_rows < self.chrome_instances:
            self.chrome_instances = num_rows
        
        if not self.chrome_instances:
            self.page_scraper_loader.fail_artificially()
            self.logger_config.log("All images have been downloaded already!", logging.ERROR)
            quit()

        num_rows_per_part = num_rows // self.chrome_instances

        parts = [database_df.iloc[i*num_rows_per_part:(i+1)*num_rows_per_part] for i in range(self.chrome_instances)]

        remainder = num_rows % self.chrome_instances

        if remainder > 0:
            remainder_rows = database_df.iloc[-remainder:]
            for i in range(remainder):
                parts[i] = pd.concat([parts[i], remainder_rows.iloc[[i]]])

        return parts
    
    def run(self) -> None:
        self.page_scraper_loader.start()
        df_parts = self._open_and_divide_instances()
        self._database_search(df_parts)
        self.page_scraper_loader.stop()
    
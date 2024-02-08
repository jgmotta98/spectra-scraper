from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import os
import re

#TODO: diminuir o tempo de espera de algumas partes da extração.

wd = webdriver.Chrome()
DATABASE_PATH = r'..\IR_spectral_data\comp_sdbs_no.csv'
BASE_URL_IMG = "https://sdbs.db.aist.go.jp/sdbs/cgi-bin/IMG.cgi?imgdir=ir&amp;fname=NIDA"
BASE_URL = "https://sdbs.db.aist.go.jp/sdbs/cgi-bin/landingpage?sdbsno="
SPECTRAL_PATH = r'..\IR_spectral_data\img_data'

def scrape_info(row):
    if not hasattr(scrape_info, "agree_clicked"):
        scrape_info.agree_clicked = False 

    def get_nida():
        wait = WebDriverWait(wd, 1)
        ir_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(), 'IR')]")))
        for element in ir_elements:
            match = re.search(r'NIDA-(\d+)', element.text)
            if not match:
                return None
            nida_number = re.sub(r'^0+', '', str(match.group(1)))
            return nida_number
        
    index = row.name
    number, name, is_complete = row['number'], row['comp_name'], row['completion']  # Assuming 'number' and 'name' are column names
    if is_complete == "incomplete":
        try:
            print(name, number)
            url = BASE_URL + str(number)
            wd.get(url)
            if not scrape_info.agree_clicked:
                wait = WebDriverWait(wd, 1)
                agree_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "agree_button")))
                agree_button.click()
                scrape_info.agree_clicked = True

                url = BASE_URL + str(number)
                wd.get(url)

                nida_val = get_nida()

                if not nida_val:
                    return None

                url_img = BASE_URL_IMG + str(nida_val)
                wd.get(url_img)
                file_path = os.path.join(SPECTRAL_PATH, str(name) + '.png')
                image_element = WebDriverWait(wd, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "img"))
                )
                ActionChains(wd).move_to_element(image_element).perform()
                WebDriverWait(wd, 5).until(lambda d: image_element.get_attribute('complete'))
                image_element.screenshot(file_path)
            else:
                nida_val = get_nida()

                if not nida_val:
                    return None

                url_img = BASE_URL_IMG + str(nida_val)
                wd.get(url_img)
                file_path = os.path.join(SPECTRAL_PATH, str(name) + '.png')
                image_element = WebDriverWait(wd, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "img"))
                )
                ActionChains(wd).move_to_element(image_element).perform()
                WebDriverWait(wd, 5).until(lambda d: image_element.get_attribute('complete'))
                image_element.screenshot(file_path)
            return 'complete'
        except Exception as e:
            print(e)


def set_database_link():
    database_df = pd.read_csv(DATABASE_PATH, delimiter=';')
    col_names = list(database_df.columns)
    new_first_row = pd.DataFrame([col_names], columns=col_names)
    database_df.reset_index(drop=True, inplace=True)
    database_df = pd.concat([new_first_row, database_df], ignore_index=True)
    database_df.columns = ['number', 'comp_name', 'completion']

    duplicates_all_columns = database_df[database_df.duplicated(keep=False)]
    duplicates_all_columns.reset_index(drop=True, inplace=True)

    database_df['completion'] = database_df.apply(scrape_info, axis=1)

def main():
    set_database_link()
    wd.quit()

if __name__ == "__main__":
    main()
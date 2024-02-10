from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import os
import re
from PIL import Image, ImageDraw

#TODO: implementar paralelismo.

class SDBSPageScraper:

    def __init__(self):
        self.wd = webdriver.Chrome()
        self.database_path = r'..\IR_spectral_data\comp_sdbs_no.csv'
        self.base_url_img = "https://sdbs.db.aist.go.jp/sdbs/cgi-bin/IMG.cgi?imgdir=ir&amp;fname=NIDA"
        self.base_url = "https://sdbs.db.aist.go.jp/sdbs/cgi-bin/landingpage?sdbsno="
        self.spectral_path = r'..\IR_spectral_data\img_data'
        self.agree_clicked = False

    def _get_nida(self, wd):
        try:
            wait = WebDriverWait(wd, 1)
            ir_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(), 'IR')]")))
            for element in ir_elements:
                match = re.search(r'NIDA-(\d+)', element.text)
                if match:
                    nida_number = re.sub(r'^0+', '', str(match.group(1)))
                    return nida_number
            return None
        except Exception as e:
            print(f"Error in get_nida: {e}")
            return None
        
    def _capture_screenshot(self, name, nida_val):
        url_img = self.base_url_img + str(nida_val)
        self.wd.get(url_img)
        file_path = os.path.join(self.spectral_path, f"{name}.png")
        try:
            image_element = WebDriverWait(self.wd, 2).until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            ActionChains(self.wd).move_to_element(image_element).perform()
            WebDriverWait(self.wd, 2).until(lambda d: image_element.get_attribute('complete'))
            image_element.screenshot(file_path)
            return 'complete'
        except Exception as e:
            print(f"Error capturing screenshot for {name}: {e}")
            return None
        
    def _navigate_and_agree(self, url):
        self.wd.get(url)
        if not self.agree_clicked:
            try:
                wait = WebDriverWait(self.wd, 5)
                agree_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "agree_button")))
                agree_button.click()
                self.agree_clicked = True
                self.wd.get(url)
            except Exception as e:
                print(f"Could not find or click agree button: {e}")

    def _scrape_info(self, row):
        number, name, is_complete = row['number'], row['comp_name'], row['completion']
        if is_complete == "incomplete":
            url = self.base_url + str(number)
            self._navigate_and_agree(url)
            nida_val = self._get_nida(self.wd)
            if nida_val:
                return self._capture_screenshot(name, nida_val)
            else:
                print(f"NIDA value not found for {name}")
                return None
        return is_complete

    def _set_database_link(self):
        database_df = pd.read_csv(self.database_path, delimiter=';')
        database_df['completion'] = database_df.apply(self._scrape_info, axis=1)

    def run(self):
        self._set_database_link()
        self.wd.quit()

class SpectraMod:

    def __init__(self):
        self.cropped_path = r'..\IR_spectral_data\mod_img_data'
        self.imgs_path = r'..\IR_spectral_data\img_Data'

    def _main_img_mod(self):
        img_list = []
        for img in os.listdir(self.imgs_path):
            file_path = os.path.join(self.imgs_path, img)
            if img.endswith('.gif'):
                self._convert_gif_to_png(file_path)
                os.remove(file_path)
                file_path = file_path[:-3] + 'png'
                img_list.append(file_path)
            else:
                img_list.append(file_path)
            self._modify_spectra(file_path)
        return img_list

    @staticmethod
    def _convert_gif_to_png(file_path):
        img = Image.open(file_path)
        img.save(file_path[:-3] + 'png')

    def _modify_spectra(self, img_path):
        with Image.open(img_path).convert("RGBA") as base:
            shape = [(29, 96), (714, 417)] 
            area = (23, 90, 715, 424)

            paint_guide = [[(29, 417), (29, 422)], [(24, 417), (29, 417)],
                        [(24, 96), (29, 96)], [(714, 417), (714, 422)]]
            
            erase_square = [[(30, 418), (713, 423)], [(24, 97), (28, 416)]]

            draw = ImageDraw.Draw(base)

            for shape_guide in paint_guide:
                draw.line(shape_guide, fill="red")

            for erase in erase_square:
                draw.rectangle(erase, fill="white", outline="white")

            draw.rectangle(shape, outline="red")
            cropped_img = base.crop(area)
            cropped_img.save(os.path.join(self.cropped_path, os.path.basename(img_path)))

    def _check_img_existence(self, images_list):
        for cropped_image_name in os.listdir(self.cropped_path):
            possible_image_name_path = os.path.join(self.imgs_path, cropped_image_name)
            true_image_name_path = os.path.join(self.cropped_path, cropped_image_name)
            if possible_image_name_path not in images_list:
                os.remove(true_image_name_path)

    def run(self):
        imgs_list = self._main_img_mod()
        self._check_img_existence(imgs_list)

if __name__ == "__main__":
    sbds_page_scraper = SDBSPageScraper()
    sbds_page_scraper.run()
    spectra_mod = SpectraMod()
    spectra_mod.run()
import pytesseract
from PIL import Image, ImageEnhance
import pyautogui
import os
import csv
from pynput import mouse

class SDBSDataExtractor:
    def __init__(self):
        self.temp_path = '..\\temp_files'
        self.comp_data_path = '..\\IR_spectral_data\\comp_sdbs_no.csv'
        self.click_positions = []
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.click_positions.append((x, y))
            labels = [
                "top-left for SDBS No",
                "bottom-right for SDBS No",
                "top-left for Compound Name",
                "bottom-right for Compound Name"
            ]
            
            current_label = labels[len(self.click_positions) - 1] if len(self.click_positions) <= len(labels) else ""
            
            print(f"Clicked on {current_label}")

            if len(self.click_positions) == 4:
                return False

    @staticmethod
    def get_sdbs_no_value(sdbs_img_path):
        custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789'
        list_name = pytesseract.image_to_string(sdbs_img_path,
                                                config=custom_config).strip().split()
        return list_name
    
    @staticmethod
    def get_sdbs_name_value(sdbs_img_path):
        custom_config = r'--oem 3 --psm 3'
        chemical_names = pytesseract.image_to_string(sdbs_img_path,
                                                config=custom_config)
        list_name = [name.replace(" ", "_") for name in chemical_names.strip().split("\n")]
        list_name = [name for name in list_name if name]
        return list_name
    
    @staticmethod
    def img_save(coord, temp_img_path, temp_img_name):
        sdbs_no = pyautogui.screenshot(region=coord)
        sdbs_img_path = os.path.join(temp_img_path, temp_img_name + ".png")
        sdbs_no.save(sdbs_img_path)

        sdbs_img = Image.open(sdbs_img_path)
        gray_image = sdbs_img.convert('L')
        enhancer = ImageEnhance.Contrast(gray_image)
        enhanced_gray_image = enhancer.enhance(2.0) 
        enhanced_gray_image.save(sdbs_img_path)
        return sdbs_img_path

    def get_sbds_no(self, coord_to_save):
        sdbs_img_path = self.img_save(coord_to_save, self.temp_path, 'temp_img')
        list_name = self.get_sdbs_no_value(sdbs_img_path)
        return list_name
    
    def get_sdbs_name(self, coord_to_save):
        sdbs_img_path = self.img_save(coord_to_save, self.temp_path, 'temp_img_name')
        list_name = self.get_sdbs_name_value(sdbs_img_path)
        return list_name
    
    @staticmethod
    def read_existing_data(file_path):
        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                existing_data = [tuple(row) for row in reader]
                return existing_data
        except FileNotFoundError:
            with open(file_path, mode='w', newline='', encoding='utf-8'):
                pass
            return []

    def append_to_csv(self, list1, list2):
        if os.path.exists(self.comp_data_path) and os.path.getsize(self.comp_data_path) <= 2:
            open(self.comp_data_path, 'w').close()

        existing_data = self.read_existing_data(self.comp_data_path)
        with open(self.comp_data_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            
            if not existing_data:
                column_names = ['number', 'comp_name', 'completion']
                writer.writerow(column_names)
            
            for item1, item2 in zip(list1, list2):
                row = (item1, item2, "incomplete")
                row_temp = (item1, item2, "complete")
                if not (row in existing_data or row_temp in existing_data):
                    writer.writerow(row)

    def capture_clicks(self):
        print('Listening for mouse clicks. Complete four clicks to proceed.')
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()


    def get_click_regions(self):
        regions = [
            (self.click_positions[0][0], self.click_positions[0][1], 
             self.click_positions[1][0] - self.click_positions[0][0], 
             self.click_positions[1][1] - self.click_positions[0][1]),
            (self.click_positions[2][0], self.click_positions[2][1], 
             self.click_positions[3][0] - self.click_positions[2][0], 
             self.click_positions[3][1] - self.click_positions[2][1])
        ]
        return regions
    
    def process_clicks(self):
        regions = self.get_click_regions()
        name_list = self.get_sbds_no(regions[0])
        name_comp_list = self.get_sdbs_name(regions[1])
        return name_list, name_comp_list

    def run(self):
        while True:
            self.click_positions.clear()
            while True:
                try:
                    self.capture_clicks()
                    name_list, name_comp_list = self.process_clicks()

                    do_retry = input('Retry the clicks? (y/n): ')
                    if do_retry != 'y':
                        break
                    else:
                        self.click_positions.clear()
                except Exception as e:
                    print('An error occurred. Retrying the clicks...')
                    self.click_positions.clear()
            
            self.append_to_csv(name_list, name_comp_list)
            do_continue = input('Continue capturing? (y/n): ')
            if do_continue != 'y':
                break  

if __name__ == "__main__":
    sdbs = SDBSDataExtractor()
    sdbs.run()
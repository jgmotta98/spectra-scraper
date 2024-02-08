import pytesseract
from PIL import Image, ImageEnhance
import pyautogui
import os
import csv
from pynput import mouse

#pyautogui.displayMousePosition()
TEMP_PATH = r'..\temp_files'
COMP_DATA_PATH = r'..\IR_spectral_data'
FIXED_URL = 'https://sdbs.db.aist.go.jp/sdbs/cgi-bin/cre_frame_disp.cgi?spectrum_type=ir&amp;sdbsno='
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#TODO: consertar o lance dos dados repetidos, não está funcionando.
#TODO: botar nomes de colunas nos arquivos csv.

def get_sbds_no(coord_to_save):
    sdbs_no = pyautogui.screenshot(region=coord_to_save)
    sdbs_img_path = os.path.join(TEMP_PATH, "temp_img.png")
    sdbs_no.save(sdbs_img_path)

    sdbs_img = Image.open(sdbs_img_path)
    gray_image = sdbs_img.convert('L')
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_gray_image = enhancer.enhance(2.0) 
    enhanced_gray_image.save(sdbs_img_path)
    list_name, csv_path = get_sdbs_no_value(sdbs_img_path)
    return list_name, csv_path

def get_sdbs_no_value(sdbs_img_path):
    custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789'
    list_name = pytesseract.image_to_string(sdbs_img_path,
                                            config=custom_config).strip().split()
    csv_path = os.path.join(COMP_DATA_PATH, 'comp_sdbs_no.csv')
    #os.remove(sdbs_img_path)
    return list_name, csv_path

def get_sdbs_name_value(sdbs_img_path):
    custom_config = r'--oem 3 --psm 3'
    chemical_names = pytesseract.image_to_string(sdbs_img_path,
                                            config=custom_config)
    list_name = [name.replace(" ", "_") for name in chemical_names.strip().split("\n")]
    list_name = [name for name in list_name if name]
    #os.remove(sdbs_img_path)
    return list_name

def read_existing_data(file_path):
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')  # Use semicolon as delimiter
            existing_data = [tuple(row) for row in reader]  # Store each row as a tuple
            return existing_data
    except FileNotFoundError:
        return []

def append_to_csv(file_path, list1, list2):
    existing_data = read_existing_data(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        for item1, item2 in zip(list1, list2):
            row = (item1, item2, "incomplete")  # Combine items into a tuple for comparison
            row_temp = (item1, item2, "complete")
            if not (row in existing_data or row_temp in existing_data):
                writer.writerow(row)  # Write both items in separate columns on the same row

def name_test_ocr(coord_to_save):
    sdbs_no = pyautogui.screenshot(region=coord_to_save)
    sdbs_img_path = os.path.join(TEMP_PATH, "temp_img_name.png")
    sdbs_no.save(sdbs_img_path)

    sdbs_img = Image.open(sdbs_img_path)
    gray_image = sdbs_img.convert('L')
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_gray_image = enhancer.enhance(2.0) 
    enhanced_gray_image.save(sdbs_img_path)
    list_name = get_sdbs_name_value(sdbs_img_path)
    return list_name

click_positions = []
def on_click(x, y, button, pressed):
    if pressed:
        click_position = (x, y)
        click_positions.append(click_position)
        print(f"Click at {click_position}")
        
        if len(click_positions) == 4:
            return False

def main():
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    merged_as_specified = [
    (click_positions[0][0], click_positions[0][1], click_positions[1][0] - click_positions[0][0], click_positions[1][1] - click_positions[0][1]),
    (click_positions[2][0], click_positions[2][1], click_positions[3][0] - click_positions[2][0], click_positions[3][1] - click_positions[2][1])]
    name_list, csv_file_path = get_sbds_no(merged_as_specified[0])
    name_comp_list = name_test_ocr(merged_as_specified[1])
    append_to_csv(csv_file_path, name_list, name_comp_list)

if __name__ == "__main__":
    main()

from PIL import Image, ImageDraw
import os
import pytesseract
import re

CROPPED_PATH = r'..\IR_spectral_data\mod_img_data'
IMGS_PATH = r'..\IR_spectral_data\img_Data'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def check_for_gif(ir_files_path):
    img_list = []
    for img in os.listdir(ir_files_path):
        file_path = os.path.join(ir_files_path, img)
        if img.endswith('.gif'):
            convert_gif_to_png(file_path)
            os.remove(file_path)
            file_path = file_path[:-3] + 'png'
            img_list.append(file_path)
        else:
            img_list.append(file_path)
        modify_spectra(file_path)
    return img_list

def convert_gif_to_png(file_path):
    img = Image.open(file_path)
    img.save(file_path[:-3] + 'png')

def modify_spectra(img_path):
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
        cropped_img.save(os.path.join(CROPPED_PATH, os.path.basename(img_path)[:-4] + '.png'))

def check_img_and_erase(cropped_images_path, images_list):
    for cropped_image_name in os.listdir(cropped_images_path):
        image_name = re.sub('.png', '', cropped_image_name)
        possible_image_name_path = os.path.join(IMGS_PATH, image_name + '.png')
        true_image_name_path = os.path.join(cropped_images_path, cropped_image_name)
        if possible_image_name_path not in images_list:
            os.remove(true_image_name_path)

def main():
    imgs_list = check_for_gif(IMGS_PATH)
    check_img_and_erase(CROPPED_PATH, imgs_list)

if __name__ == "__main__":
    main()

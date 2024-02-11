from PIL import Image, ImageDraw
from safeloader import Loader
import os

class SpectraMod:

    def __init__(self):
        self.spectra_mod_loader = Loader(desc='Modding images')
        self.cropped_path = '..\\IR_spectral_data\\mod_img_data'
        self.imgs_path = '..\\IR_spectral_data\\img_Data'

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
        self.spectra_mod_loader.start()
        imgs_list = self._main_img_mod()
        self._check_img_existence(imgs_list)
        self.spectra_mod_loader.stop()
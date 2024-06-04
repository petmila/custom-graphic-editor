import numpy as np
import enum
from PyQt5.QtGui import QImage

import classes.convert_color_space as cs
import classes.gamma_correction as gc


class Channel(enum.Enum):
    All = 0
    first = 1
    second = 2
    third = 3


class DataImage:
    def __init__(self):
        self.curr_colormap = np.zeros(0)
        self.curr_format = ''
        self.width = 0
        self.height = 0
        self.color_space = cs.ColorSpace.RGB
        self.color_space_converter = cs.ColorSpaceConverter()
        self.gamma_correction = gc.GammaCorrection()
        self.curr_channel = Channel.All
        self.gamma_curr = 0
        self.gamma_ass = 0  # sRGB

    def set_data(self, height, width, colormap, format_, gamma):
        self.curr_format = format_
        self.width = width
        self.height = height
        self.gamma_curr = gamma
        self.curr_colormap = self.unnormalize_data(colormap)

    def copy(self):
        data_image = DataImage()
        data_image.curr_colormap = self.curr_colormap.copy()
        data_image.curr_format = self.curr_format
        data_image.width = self.width
        data_image.height = self.height
        data_image.color_space = self.color_space
        data_image.color_space_converter = cs.ColorSpaceConverter()
        data_image.gamma_correction = gc.GammaCorrection()
        data_image.curr_channel = self.curr_channel
        data_image.gamma_curr = self.gamma_curr
        data_image.gamma_ass = self.gamma_ass
        return data_image

    # перевести данные в пространство [0-1] для хранения/обработки
    def unnormalize_data(self, data):
        colormap = data.copy()
        colormap = colormap.astype("float")
        colormap = colormap / 255
        return colormap

    # данные переводятся обратно в [0-255] перед сохранением/отрисовкой
    def normalize_data(self, data):
        normalized_colormap = data.copy()
        normalized_colormap = (normalized_colormap * 255)
        normalized_colormap = np.round(normalized_colormap)
        normalized_colormap[normalized_colormap > 255] = 255
        normalized_colormap[normalized_colormap < 0] = 0
        normalized_colormap = normalized_colormap.astype("uint8")
        return normalized_colormap

    def get_data(self):
        colormap = self.curr_colormap.copy()
        if self.curr_channel == Channel.first:
            colormap[:, :, :] = colormap[:, :, 0:1]
        elif self.curr_channel == Channel.second:
            colormap[:, :, :] = colormap[:, :, 1:2]
        elif self.curr_channel == Channel.third:
            colormap[:, :, :] = colormap[:, :, 2:3]
        return self.curr_format, self.normalize_data(colormap)

    def get_data_float(self):
        colormap = self.curr_colormap.copy()
        if self.curr_channel == Channel.first:
            colormap[:, :, :] = colormap[:, :, 0:1]
        elif self.curr_channel == Channel.second:
            colormap[:, :, :] = colormap[:, :, 1:2]
        elif self.curr_channel == Channel.third:
            colormap[:, :, :] = colormap[:, :, 2:3]
        return self.curr_format, colormap*255

    def get_qimage(self):
        # переводим в RGB только в трехканальном режиме
        qimage_colormap = self.curr_colormap.copy()
        qimage_colormap = self.change_gamma(qimage_colormap)

        if self.curr_channel == Channel.All:
            qimage_colormap = self.color_space_converter.to_rgb(qimage_colormap, self.color_space)
        elif self.curr_channel == Channel.first:
            qimage_colormap[:, :, :] = qimage_colormap[:, :, 0:1]
        elif self.curr_channel == Channel.second:
            qimage_colormap[:, :, :] = qimage_colormap[:, :, 1:2]
        elif self.curr_channel == Channel.third:
            qimage_colormap[:, :, :] = qimage_colormap[:, :, 2:3]
        # нормализуем
        qimage_colormap = self.normalize_data(qimage_colormap)
        return QImage(qimage_colormap, self.width,
                      self.height, 3 * self.width, QImage.Format_RGB888)

    # Назначаем новое значение гаммы для вывода изображений
    def assign_gamma(self, gamma):
        self.gamma_ass = gamma

    # Преобразовать текущий colormap по assigned gamma, теперь assigned gamma = current gamma
    def convert_to_gamma(self, gamma):
        old_gamma = self.gamma_ass
        self.gamma_ass = gamma
        if self.curr_colormap.size != 0:
            self.curr_colormap = self.change_gamma(self.curr_colormap)
        self.gamma_curr = self.gamma_ass
        self.gamma_ass = old_gamma

    # Преобразовать переданный colormap из current gamma в assigned gamma и вернуть новый colormap
    def change_gamma(self, colormap):
        new_colormap = colormap.copy()
        if self.gamma_curr != self.gamma_ass:
            if self.color_space != cs.ColorSpace.RGB:
                new_colormap = self.color_space_converter.to_rgb(new_colormap, self.color_space)
                new_colormap = self.gamma_correction.gamma_correction(new_colormap, self.gamma_curr,
                                                                      self.gamma_ass)
                new_colormap = self.color_space_converter.from_rgb(new_colormap, self.color_space)
            else:
                new_colormap = self.gamma_correction.gamma_correction(new_colormap, self.gamma_curr,
                                                                      self.gamma_ass)
        return new_colormap

    def convert_to_hsl(self):
        data = self.color_space_converter.to_rgb(self.curr_colormap, self.color_space)
        self.curr_colormap = self.color_space_converter.from_rgb(data, cs.ColorSpace.HSL)
        self.color_space = cs.ColorSpace.HSL

    def convert_to_hsv(self):
        data = self.color_space_converter.to_rgb(self.curr_colormap, self.color_space)
        self.curr_colormap = self.color_space_converter.from_rgb(data, cs.ColorSpace.HSV)
        self.color_space = cs.ColorSpace.HSV

    def convert_to_cmy(self):
        data = self.color_space_converter.to_rgb(self.curr_colormap, self.color_space)
        self.curr_colormap = self.color_space_converter.from_rgb(data, cs.ColorSpace.CMY)
        self.color_space = cs.ColorSpace.CMY

    def convert_to_rgb(self):
        data = self.color_space_converter.to_rgb(self.curr_colormap, self.color_space)
        self.curr_colormap = self.color_space_converter.from_rgb(data, cs.ColorSpace.RGB)
        self.color_space = cs.ColorSpace.RGB

    def convert_to_ycbcr601(self):
        data = self.color_space_converter.to_rgb(self.curr_colormap, self.color_space)
        self.curr_colormap = self.color_space_converter.from_rgb(data, cs.ColorSpace.YCbCr601)
        self.color_space = cs.ColorSpace.YCbCr601

    def convert_to_ycbcr709(self):
        data = self.color_space_converter.to_rgb(self.curr_colormap, self.color_space)
        self.curr_colormap = self.color_space_converter.from_rgb(data, cs.ColorSpace.YCbCr709)
        self.color_space = cs.ColorSpace.YCbCr709

    def convert_to_ycocg(self):
        data = self.color_space_converter.to_rgb(self.curr_colormap, self.color_space)
        self.curr_colormap = self.color_space_converter.from_rgb(data, cs.ColorSpace.YCoCg)
        self.color_space = cs.ColorSpace.YCoCg

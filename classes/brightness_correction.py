import numpy as np
import matplotlib.pyplot as plt
import scripts.utilities as util

from classes.convert_color_space import ColorSpaceConverter
from classes.convert_color_space import ColorSpace
from classes.data_image import Channel


class BrightnessCorrection:
    FILE_PATH = "./images/BrightnessCorrection.jpg"

    def __init__(self):
        self.ignoring_coefficient = 0

    def make_hist_picture_without_coef(self, colormap, color_space, channel) -> str:
        coef = self.ignoring_coefficient
        self.ignoring_coefficient = 0
        self.brightness_correction(colormap, color_space, channel)
        self.ignoring_coefficient = coef
        return self.FILE_PATH

    def make_hist_picture(self, colormap, color_space, channel) -> str:
        self.brightness_correction(colormap, color_space, channel)
        return self.FILE_PATH

    def brightness_correction(self, colormap, color_space, channel):
        if color_space == ColorSpace.RGB:
            return self.rgb_brightness_correction(colormap, channel)
        elif color_space == ColorSpace.HSL or color_space == ColorSpace.HSV:
            colormap = util.unnormalize_data(colormap)
            csc = ColorSpaceConverter()
            colormap = util.normalize_data(csc.to_rgb(colormap, color_space))
            colormap = self.rgb_brightness_correction(colormap, channel)
            colormap = util.unnormalize_data(colormap)
            colormap = util.normalize_data(csc.from_rgb(colormap, color_space))
            return colormap
        elif color_space == ColorSpace.CMY:
            return self.cmy_brightness_correction(colormap, channel)
        elif color_space == ColorSpace.YCbCr601 or color_space == ColorSpace.YCbCr709 or color_space == ColorSpace.YCoCg:
            return self.y_brightness_correction(colormap, channel)

    def get_min_amd_max(self, array, amount):
        number_of_cut_px = amount * self.ignoring_coefficient
        min_num = 0
        max_num = 255
        counter = number_of_cut_px
        for i in range(len(array)):
            counter -= array[i]
            if counter < 0:
                break
            min_num = i

        counter = number_of_cut_px
        for i in range(len(array) - 1, 0, -1):
            counter -= array[i]
            if counter < 0:
                break
            max_num = i
        return min_num, max_num

    def counter_every_pixels_value(self, colormap):
        first_arr = np.zeros(256)
        second_arr = np.zeros(256)
        third_arr = np.zeros(256)
        for i in range(np.shape(colormap)[0]):
            for j in range(np.shape(colormap)[1]):
                first_arr[int(colormap[i, j, 0])] += 1
                second_arr[int(colormap[i, j, 1])] += 1
                third_arr[int(colormap[i, j, 2])] += 1
        return first_arr, second_arr, third_arr

    def rgb_brightness_correction(self, colormap, channel):
        numbers = np.arange(256, dtype=int)
        red_px, green_px, blue_px = self.counter_every_pixels_value(colormap)

        if self.ignoring_coefficient != 0:
            min_r, max_r = self.get_min_amd_max(red_px, colormap.size)
            min_g, max_g = self.get_min_amd_max(green_px, colormap.size)
            min_b, max_b = self.get_min_amd_max(blue_px, colormap.size)
            min_val = min(min_r, min_g, min_b)
            max_val = max(max_r, max_g, max_b)
            new_colormap = np.copy(colormap)
            new_colormap = new_colormap.astype("int")
            new_colormap = (new_colormap - min_val) * 255 / (max_val - min_val)

            new_colormap = np.where(new_colormap < 0, 0, new_colormap)
            new_colormap = np.where(new_colormap > 255, 255, new_colormap)
            colormap = new_colormap

            red_px, green_px, blue_px = self.counter_every_pixels_value(colormap)
        if channel == Channel.All:
            fig, axs = plt.subplots(3, 1, figsize=(8, 6))
            axs[0].bar(numbers, red_px, width=1, color='red', label='red')
            axs[0].legend()
            axs[1].bar(numbers, green_px, width=1, color='green', label='green')
            axs[1].legend()
            axs[2].bar(numbers, blue_px, width=1, color='blue', label='blue')
            axs[2].legend()
        elif channel == Channel.first:
            fig, axs = plt.subplots(1, 1, figsize=(8, 6))
            axs.bar(numbers, red_px, width=1, color='red', label='red')
            axs.legend()
        elif channel == Channel.second:
            fig, axs = plt.subplots(1, 1, figsize=(8, 6))
            axs.bar(numbers, green_px, width=1, color='green', label='green')
            axs.legend()
        elif channel == Channel.third:
            fig, axs = plt.subplots(1, 1, figsize=(8, 6))
            axs.bar(numbers, blue_px, width=1, color='blue', label='blue')
            axs.legend()
        plt.savefig(self.FILE_PATH)
        return colormap

    def cmy_brightness_correction(self, colormap, channel):
        numbers = np.arange(256, dtype=int)
        c_px, m_px, y_px = self.counter_every_pixels_value(colormap)

        if self.ignoring_coefficient != 0:
            min_c, max_c = self.get_min_amd_max(c_px, colormap.size)
            min_m, max_m = self.get_min_amd_max(m_px, colormap.size)
            min_y, max_y = self.get_min_amd_max(y_px, colormap.size)
            min_val = min(min_c, min_m, min_y)
            max_val = max(max_c, max_m, max_y)
            new_colormap = np.copy(colormap)
            new_colormap = new_colormap.astype("int")
            new_colormap = (new_colormap - min_val) * 255 / (max_val - min_val)

            new_colormap = np.where(new_colormap < 0, 0, new_colormap)
            new_colormap = np.where(new_colormap > 255, 255, new_colormap)
            colormap = new_colormap

            c_px, m_px, y_px = self.counter_every_pixels_value(colormap)

        if channel == Channel.All:
            fig, axs = plt.subplots(3, 1, figsize=(8, 6))
            axs[0].bar(numbers, c_px, width=1, color='cyan', label='cyan')
            axs[0].legend()
            axs[1].bar(numbers, m_px, width=1, color='magenta', label='magenta')
            axs[1].legend()
            axs[2].bar(numbers, y_px, width=1, color='yellow', label='yellow')
            axs[2].legend()
        elif channel == Channel.first:
            fig, axs = plt.subplots(1, 1, figsize=(8, 6))
            axs.bar(numbers, c_px, width=1, color='cyan', label='cyan')
            axs.legend()
        elif channel == Channel.second:
            fig, axs = plt.subplots(1, 1, figsize=(8, 6))
            axs.bar(numbers, m_px, width=1, color='magenta', label='magenta')
            axs.legend()
        elif channel == Channel.third:
            fig, axs = plt.subplots(1, 1, figsize=(8, 6))
            axs.bar(numbers, y_px, width=1, color='yellow', label='yellow')
            axs.legend()
        plt.savefig(self.FILE_PATH)
        return colormap

    def y_brightness_correction(self, colormap, channel):
        numbers = np.arange(256, dtype=int)
        y_px, c1, c2 = self.counter_every_pixels_value(colormap)

        if self.ignoring_coefficient != 0:
            min_y, max_y = self.get_min_amd_max(y_px, colormap.size)
            new_colormap = np.copy(colormap)
            new_colormap = new_colormap.astype("int")
            new_colormap[:, :, 0] = (new_colormap[:, :, 0] - min_y) * 255 / (max_y - min_y)

            new_colormap = np.where(new_colormap < 0, 0, new_colormap)
            new_colormap = np.where(new_colormap > 255, 255, new_colormap)
            colormap = new_colormap

            y_px, c1, c2 = self.counter_every_pixels_value(colormap)
        if channel == Channel.All or channel == Channel.first:
            fig, axs = plt.subplots(1, 1, figsize=(8, 6))
            axs.bar(numbers, y_px, width=1, color='grey', label='luma')
            axs.legend()
        plt.savefig(self.FILE_PATH)
        return colormap

import math
from random import uniform

import numpy as np
import classes.gamma_correction as gc


def gradient(height, width):
    colormap = np.empty((height, width, 3), dtype=float)
    gamma_cor = gc.GammaCorrection()
    for i in range(height):
        for j in range(width):
            colormap[i, j] = float(j/(width - 1))
    return colormap * 255


def convert_bit_depth(value: float, bt, gamma: float):
    max_value = pow(2, bt) - 1
    un_value = value * max_value
    error = 0
    new_value = 0
    if un_value <= max_value:
        if un_value >= 0:
            new_value = float(round(un_value) / max_value)
            error = difference_in_gamma(value, new_value, gamma)

        else:
            new_value = 0
            error = difference_in_gamma(new_value, (-1)*value, gamma)
    else:
        print("YES")
        new_value = 1
        error = difference_in_gamma(0, value - 1, gamma)
    return new_value, error


def difference_in_gamma(val1: float, val2: float, gamma: float):
    gamma_correction = gc.GammaCorrection()
    linear_val1 = gamma_correction.one_value_to_linear(val1, gamma)
    linear_val2 = gamma_correction.one_value_to_linear(val2, gamma)
    error = linear_val1 - linear_val2
    return error


def get_borders(bt):
    max_value = pow(2, bt) - 1
    list_borders = []
    for i in range(max_value + 1):
        list_borders.append(float(i/max_value))
    return list_borders


def get_value_between_borders_gamma_rand(border1: float, border2: float, gamma: float, value: float):
    gamma_correction = gc.GammaCorrection()
    linear_border1 = gamma_correction.one_value_to_linear(border1, gamma)
    linear_border2 = gamma_correction.one_value_to_linear(border2, gamma)
    linear_value = gamma_correction.one_value_to_linear(value, gamma)
    random_num = uniform(linear_border1, linear_border2)
    if linear_value <= random_num:
        return linear_border1
    else:
        return linear_border2


def get_value_between_borders_table(border1: float, border2: float, gamma: float, value: float, table_num: float):
    gamma_correction = gc.GammaCorrection()
    linear_border1 = gamma_correction.one_value_to_linear(border1, gamma)
    linear_border2 = gamma_correction.one_value_to_linear(border2, gamma)
    linear_value = gamma_correction.one_value_to_linear(value, gamma)
    table_num = gamma_correction.one_value_to_linear(value, gamma)
    random_num = uniform(linear_border1, linear_border2)
    if linear_value <= random_num:
        return linear_border1
    else:
        return linear_border2


def sum_in_gamma(val1: float, error: float, gamma: float):
    gamma_correction = gc.GammaCorrection()
    if val1 < 0:
        linear_val1 = -gamma_correction.one_value_to_linear(-val1, gamma)
    else:
        linear_val1 = gamma_correction.one_value_to_linear(val1, gamma)

    sum_val = linear_val1 + error
    if sum_val < 0:
        return -gamma_correction.one_value_from_linear(-sum_val, gamma)
    if sum_val > 1:
        return gamma_correction.one_value_from_linear(1, gamma)
    return gamma_correction.one_value_from_linear(sum_val, gamma)


def comparison_in_gamma(val1: float, data_in_gamma: float, gamma: float):
    gamma_correction = gc.GammaCorrection()
    linear_val1 = gamma_correction.one_value_to_linear(val1, gamma)
    if linear_val1 < data_in_gamma or math.isclose(linear_val1, data_in_gamma):
        return True
    else:
        return False


def get_bayer_matrix():
    bayer_matrix = [
        [0, 32, 8, 40, 2, 34, 10, 42],
        [48, 16, 56, 24, 50, 18, 58, 26],
        [12, 44, 4, 36, 14, 46, 6, 38],
        [60, 28, 52, 20, 62, 30, 54, 22],
        [3, 35, 11, 43, 1, 33, 9, 41],
        [51, 19, 59, 27, 49, 17, 57, 25],
        [15, 47, 7, 39, 13, 45, 5, 37],
        [63, 31, 55, 23, 61, 29, 53, 21]
    ]
    return bayer_matrix


def random_alg(data_image, bt, channels):
    colormap = data_image.curr_colormap
    height = data_image.height
    width = data_image.width
    max_value = pow(2, bt) - 1
    list_borders = get_borders(bt)
    gamma_correction = gc.GammaCorrection()
    for y in range(height):
        for x in range(width):
            for channel in range(channels):
                old_value = colormap[y, x, channel]
                if old_value > 1:
                    old_value = 1
                num = 0
                for item in range(len(list_borders)):
                    num = item
                    if item + 1 < len(list_borders) and (old_value < list_borders[item + 1] or math.isclose(old_value, list_borders[item + 1])):
                        break
                colormap[y, x, channel] = gamma_correction.one_value_from_linear(get_value_between_borders_gamma_rand(list_borders[num], list_borders[num + 1], data_image.gamma_curr, old_value), 0)

    if channels == 1:
        colormap[:, :, :] = colormap[:, :, 0:1]
    data_image.curr_colormap = colormap
    return data_image


def ordered(data_image, bt, channels):
    colormap = data_image.curr_colormap
    height = data_image.height
    width = data_image.width
    max_value = pow(2, bt) - 1
    list_borders = get_borders(bt)
    bayer_matrix = get_bayer_matrix()
    gamma_correction = gc.GammaCorrection()
    for y in range(height):
        for x in range(width):
            for channel in range(channels):
                old_value = colormap[y, x, channel]
                if old_value > 1:
                    old_value = 1
                num = 0
                for item in range(len(list_borders)):
                    num = item
                    if item + 1 < len(list_borders) and (old_value < list_borders[item + 1] or math.isclose(old_value, list_borders[item + 1])):
                        break
                table_num = (bayer_matrix[y % 8][x % 8] / 64)
                if old_value <= table_num:
                    colormap[y, x, channel] = list_borders[num]
                else:
                    colormap[y, x, channel] = list_borders[num+1]

    if channels == 1:
        colormap[:, :, :] = colormap[:, :, 0:1]
    data_image.curr_colormap = colormap
    return data_image


def floyd_steinberg(data_image, bt, channels):
    colormap = data_image.curr_colormap
    height = data_image.height
    width = data_image.width
    for y in range(height):
        for x in range(width):
            for channel in range(channels):
                old_value = colormap[y, x, channel]
                new_value, error = convert_bit_depth(old_value, bt, data_image.gamma_curr)
                colormap[y, x, channel] = new_value
                if x + 1 < width:
                    colormap[y, x + 1, channel] = sum_in_gamma(colormap[y, x + 1, channel], error * 7 / 16, data_image.gamma_curr)
                if x + 1 < width and y + 1 < height:
                    colormap[y + 1, x + 1, channel] = sum_in_gamma(colormap[y + 1, x + 1, channel], error * 1 / 16, data_image.gamma_curr)
                if y + 1 < height:
                    colormap[y + 1, x, channel] = sum_in_gamma(colormap[y + 1, x, channel], error * 5 / 16, data_image.gamma_curr)
                if y + 1 < height and x > 0:
                    colormap[y + 1, x - 1, channel] = sum_in_gamma(colormap[y + 1, x - 1, channel], error * 3 / 16, data_image.gamma_curr)
    if channels == 1:
        colormap[:, :, :] = colormap[:, :, 0:1]
    data_image.curr_colormap = colormap
    return data_image


def atkinson(data_image, bt, channels):
    colormap = data_image.curr_colormap
    height = data_image.height
    width = data_image.width
    for y in range(height):
        for x in range(width):
            for channel in range(channels):
                old_value = colormap[y, x, channel]
                new_value, error = convert_bit_depth(old_value, bt, data_image.gamma_curr)
                colormap[y, x, channel] = new_value
                if x + 1 < width:
                    colormap[y, x + 1, channel] = sum_in_gamma(colormap[y, x + 1, channel], error * 1 / 8,
                                                               data_image.gamma_curr)
                if x + 1 < width and y + 1 < height:
                    colormap[y + 1, x + 1, channel] = sum_in_gamma(colormap[y + 1, x + 1, channel], error * 1 / 8,
                                                                   data_image.gamma_curr)
                if y + 1 < height:
                    colormap[y + 1, x, channel] = sum_in_gamma(colormap[y + 1, x, channel], error * 1 / 8,
                                                               data_image.gamma_curr)
                if y + 1 < height and x > 0:
                    colormap[y + 1, x - 1, channel] = sum_in_gamma(colormap[y + 1, x - 1, channel], error * 1 / 8,
                                                                   data_image.gamma_curr)
                if x + 2 < width:
                    colormap[y, x + 2, channel] = sum_in_gamma(colormap[y, x + 2, channel], error * 1 / 8,
                                                               data_image.gamma_curr)
                if y + 2 < height:
                    colormap[y + 2, x, channel] = sum_in_gamma(colormap[y + 2, x, channel], error * 1 / 8,
                                                               data_image.gamma_curr)
    if channels == 1:
        colormap[:, :, :] = colormap[:, :, 0:1]
    data_image.curr_colormap = colormap
    return data_image

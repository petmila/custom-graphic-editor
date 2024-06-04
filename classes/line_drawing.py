import math

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from classes.convert_color_space import ColorSpace


class LineDrawing:
    def __init__(self, data_image):
        self.width = 1
        self.transparency = 0.0
        self.color = QColor(Qt.black)
        self.array_color = [1.1, 2.2, 3.3]
        self.data_image = data_image
        self._linear_colormap = np.zeros(0)

    def get_color_array(self):
    # Переводит заданный цвет в текущее цветовое пр-во
        colors_rgb = [self.color.red() / 255, self.color.green() / 255, self.color.blue() / 255]

        if self.data_image.color_space == ColorSpace.HSL:
            self.array_color[0], self.array_color[1], self.array_color[2] = \
                self.data_image.color_space_converter.toHSL(colors_rgb[0], colors_rgb[1], colors_rgb[2])
        elif self.data_image.color_space == ColorSpace.HSV:
            self.array_color[0], self.array_color[1], self.array_color[2] = \
                self.data_image.color_space_converter.toHSV(colors_rgb[0], colors_rgb[1], colors_rgb[2])
        elif self.data_image.color_space == ColorSpace.CMY:
            self.array_color[0], self.array_color[1], self.array_color[2] = \
                self.data_image.color_space_converter.toCMY(colors_rgb[0], colors_rgb[1], colors_rgb[2])
        elif self.data_image.color_space == ColorSpace.YCbCr601:
            self.array_color[0], self.array_color[1], self.array_color[2] = \
                self.data_image.color_space_converter.toYCbCr601(colors_rgb[0], colors_rgb[1], colors_rgb[2])
        elif self.data_image.color_space == ColorSpace.YCbCr709:
            self.array_color[0], self.array_color[1], self.array_color[2] = \
                self.data_image.color_space_converter.toYCbCr709(colors_rgb[0], colors_rgb[1], colors_rgb[2])
        elif self.data_image.color_space == ColorSpace.YCoCg:
            self.array_color[0], self.array_color[1], self.array_color[2] = \
                self.data_image.color_space_converter.toYCoCg(colors_rgb[0], colors_rgb[1], colors_rgb[2])
        else:
            self.array_color[0], self.array_color[1], self.array_color[2] = colors_rgb[0], colors_rgb[1], colors_rgb[2]

    def draw(self, x1, y1, x2, y2):
        self.get_color_array()
        self._linear_colormap = self.data_image.gamma_correction.to_linear(self.data_image.curr_colormap,
                                                                           self.data_image.gamma_curr)
        try:
            self.thick_line_algorithm(x1, y1, x2, y2)
        except BaseException as ex:
            print(ex.__str__())
            return 'no drawing'
        self.data_image.curr_colormap = self.data_image.gamma_correction.from_linear(self._linear_colormap,
                                                                                     self.data_image.gamma_curr)
        return 'ok'

    def draw_point(self, point, alpha):
        x, y = point
        self._linear_colormap[y, x, 0] = float(
            self._transparency(self._linear_colormap[y, x, 0], self.array_color[0], alpha))
        self._linear_colormap[y, x, 1] = float(
            self._transparency(self._linear_colormap[y, x, 1], self.array_color[1], alpha))
        self._linear_colormap[y, x, 2] = float(
            self._transparency(self._linear_colormap[y, x, 2], self.array_color[2], alpha))

    def thick_line_algorithm(self, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        steep = abs(dy) > abs(dx)
        length = math.sqrt(dx ** 2 + dy ** 2)
        if steep:
            x1, y1, x2, y2, dx, dy = y1, x1, y2, x2, dy, dx
        if x1 > x2:
            x1, x2, y1, y2 = x2, x1, y2, y1
        border_dict = {}

        sin_alpha = (y2 - y1) / length
        cos_alpha = (x2 - x1) / length

        delta_x = abs((sin_alpha * self.width / 2))
        delta_y = abs((cos_alpha * self.width / 2))

        border_dict = {}

        # Сортировка точек
        if y2 > y1:
            point1 = self._switch_if_Oy(x1 + delta_x, y1 - delta_y, steep)
            point2 = self._switch_if_Oy(x2 + delta_x, y2 - delta_y, steep)
            point3 = self._switch_if_Oy(x1 - delta_x, y1 + delta_y, steep)
            point4 = self._switch_if_Oy(x2 - delta_x, y2 + delta_y, steep)

        else:
            point1 = self._switch_if_Oy(x1 - delta_x, y1 - delta_y, steep)
            point2 = self._switch_if_Oy(x2 - delta_x, y2 - delta_y, steep)
            point3 = self._switch_if_Oy(x1 + delta_x, y1 + delta_y, steep)
            point4 = self._switch_if_Oy(x2 + delta_x, y2 + delta_y, steep)

        if self.width >= 1.8:
            border_dict = self.wu_line_algorithm(point4, point2, True, border_dict, 2, 1)
            border_dict = self.wu_line_algorithm(point1, point3, False, border_dict, 4, 1)
            border_dict = self.wu_line_algorithm(point3, point4, True, border_dict, 3, 1)
            border_dict = self.wu_line_algorithm(point1, point2, False, border_dict, 1, 1)
            self.fill_area(point1, point2, point3, point4, border_dict)
        else:
            point1 = self._switch_if_Oy(x1, y1, steep)
            point2 = self._switch_if_Oy(x2, y2, steep)
            self.wu_line_algorithm(point1, point2, True, border_dict, 1, self.width)

    def fill_area(self, point1, point2, point3, point4, border_dict):
    # Заливка области
        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = point3
        x4, y4 = point4

        x_min = round(min(x1, x2, x3, x4))
        x_max = round(max(x1, x2, x3, x4))
        y_min = round(min(y1, y2, y3, y4))
        y_max = round(max(y1, y2, y3, y4))

        for x in range(x_min, x_max+1):
            # Флаги нужны просто чтобы отметить что мы посмотрели элемент на границе и теперь можно красить, например
            flag = 0
            flag2 = 0
            first_free_space = -1
            last_border = -1
            # В первом цикле for по y мы ищем координаты той области, которую нужно закрасить для рассматриваемого x
            for y in range(y_min-5, y_max+5):
                if (x, y) in border_dict:
                    if flag2 == 0:
                        last_border = (x, y)
                        flag2 = 1
                    if flag == 0:
                        flag = 1
                    continue
                if flag == 1:
                    first_free_space = (x, y)
                    flag = 2
                    continue
                flag2 = 0
            flag = 0
            if first_free_space >= last_border:
                continue
            # В этом цикле мы непосредственно закрашиваем график
            for y in range(y_min - 2, y_max):
                if (x, y) == first_free_space:
                    flag = 1
                if (x, y) == last_border:
                    break
                if flag == 1:
                    self.draw_point((x, y), 1)

    def wu_line_algorithm(self, point1, point2, border_after_body: bool, border_dict: dict, line_number: int, percent: float):
        x1, y1 = point1
        x2, y2 = point2
        dx, dy = x2 - x1, y2 - y1
        steep = abs(dy) > abs(dx)
        if steep:
            x1, y1, x2, y2, dx, dy = y1, x1, y2, x2, dy, dx
        if x1 > x2:
            x1, x2, y1, y2 = x2, x1, y2, y1

        gradient = 1 if dx == 0 else dy / dx

        distance = y1 + gradient * (round(x1) - x1)
        x_start, y_start = (round(x1)), y1 + gradient * (round(x1) - x1)
        x_end, y_end = (round(x2)), y2 + gradient * (round(x2) - x2)

        if x_start > x_end:
            x_start, x_end = x_end, x_start
            y_start, y_end = y_end, y_start

        # Рисую уголки только для двух линий, 2й и 4й
        if line_number % 2 == 0:
            self.draw_point(self._switch_if_Oy(int(x_start), int(y_start), steep),
                            (1 - self._float(y_start)) * (1 - self._float(x1 + 0.5)))

            self.draw_point(self._switch_if_Oy(int(x_start), int(y_start) + 1, steep),
                            self._float(y_start) * (1 - self._float(x1 + 0.5)))

            self.draw_point(self._switch_if_Oy(int(x_end), int(y_end), steep),
                            (1 - self._float(y_end)) * (1 - self._float(x2 + 0.5)))


            self.draw_point(self._switch_if_Oy(int(x_end), int(y_end) + 1, steep),
                            self._float(y_end) * (1 - self._float(x2 + 0.5)))

        if border_after_body:
            border_dict[self._switch_if_Oy(int(x_start), int(y_start) + 1, steep)] = line_number
            border_dict[self._switch_if_Oy(int(x_end), int(y_end) + 1, steep)] = line_number
        else:
            border_dict[self._switch_if_Oy(int(x_start), int(y_start), steep)] = line_number
            border_dict[self._switch_if_Oy(int(x_end), int(y_end), steep)] = line_number

        for x in range(x_start+1, x_end+1):
            distance += gradient
            y = int(distance)

            self.draw_point(self._switch_if_Oy(x, y, steep), (1 - self._float(distance))*percent)
            self.draw_point(self._switch_if_Oy(x, y + 1, steep), self._float(distance)*percent)

            if border_after_body:
                if not(self._switch_if_Oy(x, y+1, steep) in border_dict):
                    border_dict[self._switch_if_Oy(x, y + 1, steep)] = line_number
            else:
                if not(self._switch_if_Oy(x, y, steep) in border_dict):
                    border_dict[self._switch_if_Oy(x, y, steep)] = line_number
        return border_dict
    # вспомогательные функции
    def _float(self, a):
        return a - int(a)

    def _switch_if_Oy(self, x, y, steep):
        return (y, x) if steep else (x, y)

    def _transparency(self, image_color, line_color, alpha):
        alpha_final = (1 - self.transparency) * alpha
        return alpha_final * line_color + (1 - alpha_final) * image_color

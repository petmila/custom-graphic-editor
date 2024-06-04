import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QAction, qApp, QFileDialog, QLabel, QScrollArea, \
    QMessageBox, QColorDialog, QInputDialog, QComboBox, QDockWidget, QWidget, QLineEdit, QPushButton, QMenu
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator, QDoubleValidator

import scripts.read as read
import scripts.write as write
import scripts.exceptions as ex
import classes.data_image as di
import classes.dithering as d
import classes.line_drawing as ld
import classes.brightness_correction as bc
from classes.resampling import Resampling


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # глобальные переменные
        self.setMouseTracking(True)
        self.last_x, self.last_y = None, None

        self.color_dialog = QColorDialog(self)
        self.data_image: di.DataImage = di.DataImage()
        self.label = QLabel()
        self.scroll_area = QScrollArea()
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.brightness_correction = bc.BrightnessCorrection()
        self.brightness_hist_window = QDockWidget('Brightness hist', self)

        self.resampling = QDockWidget('Resampling', self)
        self.resampling_algorithm_name = "Nearest_neighbor"
        dock_widget = QWidget(self)
        dock_layout = QVBoxLayout(self)

        algorithm_label = QLabel('Select the resampling algorithm:')
        dock_layout.addWidget(algorithm_label)

        combo_algorithm = QComboBox()
        combo_algorithm.resize(200, 25)

        combo_algorithm.addItems(["Nearest_neighbor", "Bilinear_interpolation", "Lanczos3", "BC-Splines"])
        combo_algorithm.activated[str].connect(self.resampling_algorithm)
        dock_layout.addWidget(combo_algorithm)

        self.resampling_width_line = QLineEdit()
        self.resampling_width_line.setPlaceholderText('New width')
        self.resampling_width_line.setValidator(QIntValidator(1, 10000))
        self.resampling_height_line = QLineEdit()
        self.resampling_height_line.setPlaceholderText('New height')
        self.resampling_height_line.setValidator(QIntValidator(1, 10000))
        dock_layout.addWidget(self.resampling_height_line)
        dock_layout.addWidget(self.resampling_width_line)

        self.resampling_x = QLineEdit()
        self.resampling_x.setPlaceholderText('x')
        self.resampling_x.setValidator(QDoubleValidator(-5000, 5000, 3))
        dock_layout.addWidget(self.resampling_x)
        self.resampling_y = QLineEdit()
        self.resampling_y.setPlaceholderText('y')
        self.resampling_y.setValidator(QDoubleValidator(-5000, 5000, 3))
        dock_layout.addWidget(self.resampling_y)

        resample_button = QPushButton('Resample')
        resample_button.setStyleSheet('background-color: white')
        resample_button.clicked.connect(self.resample)
        dock_layout.addWidget(resample_button)

        dock_widget.setLayout(dock_layout)

        self.resampling.setWidget(dock_widget)
        self.resampling.setFloating(False)

        self.statusbar = self.statusBar()
        self.line_drawing = ld.LineDrawing(self.data_image)

        self.selected_color_label = QLabel()
        self.selected_color_label.setPixmap(QPixmap(20, 20))
        self.selected_color_label.pixmap().fill(self.line_drawing.color)

        self.statusbar.addPermanentWidget(self.selected_color_label)

        self.color_space_label = QLabel(f"{self.data_image.color_space}")
        self.statusbar.addPermanentWidget(self.color_space_label, 10)

        self.exit_action = QAction('&Exit', self)
        self.open_action = QAction('&Open', self)
        self.save_pnm_action = QAction('& .pnm', self)
        self.save_png_action = QAction('& .png', self)

        self.rgb_action = QAction('&RGB', self)
        self.hsl_action = QAction('&HSL', self)
        self.hsv_action = QAction('&HSV', self)
        self.ycbcr601_action = QAction('&YCbCr.601', self)
        self.ycbcr709_action = QAction('&YCbCr.709', self)
        self.ycocg_action = QAction('&YCoCg', self)
        self.cmy_action = QAction('&CMY', self)

        self.first_channel_action = QAction('&Red', self)
        self.second_channel_action = QAction('&Green', self)
        self.third_channel_action = QAction('&Blue', self)
        self.all_channel_action = QAction('&All channels', self)

        self.pick_color_action = QAction('&Pick Color', self)
        self.pen_width_action = QAction('&Pen Width', self)
        self.set_transparency_action = QAction('&Transparency', self)

        self.assign_gamma_action = QAction('&Assign Ɣ', self)
        self.convert_gamma_action = QAction('&Convert Ɣ', self)

        self.show_hist_action = QAction('&Show hist', self)
        self.show_hist_coef_action = QAction('&Show hist with ignoring coefficient', self)
        self.assign_coef_action = QAction('&Assign ignoring coefficient', self)
        self.perform_correction_action = QAction('&Perform correction', self)

        self.dithering_action = QAction('&Set parameters', self)
        self.menubar = self.menuBar()
        self.init()

    def init(self):
        # создание выпадающего меню
        file_menu = self.menubar.addMenu('&File')
        file_menu.addAction(self.open_action)
        save_menu = QMenu('&Save', file_menu)
        file_menu.addMenu(save_menu)
        save_menu.addAction(self.save_png_action)
        save_menu.addAction(self.save_pnm_action)
        file_menu.addAction(self.exit_action)

        draw_menu = self.menubar.addMenu('&Draw')
        draw_menu.addAction(self.pick_color_action)
        draw_menu.addAction(self.pen_width_action)
        draw_menu.addAction(self.set_transparency_action)

        dithering_menu = self.menubar.addMenu('&Dithering')
        dithering_menu.addAction(self.dithering_action)
        self.dithering_action.triggered.connect(self.dithering_window)

        resampling_menu = self.menubar.addMenu('&Resampling')
        self.resampling_action = QAction('&Set resampling parameters', self)
        resampling_menu.addAction(self.resampling_action)
        self.resampling_action.triggered.connect(self.show_resampling_menu)

        gamma_menu = self.menubar.addMenu('&Ɣ-correction')
        gamma_menu.addAction(self.assign_gamma_action)
        gamma_menu.addAction(self.convert_gamma_action)
        self.assign_gamma_action.triggered.connect(self.assign_gamma_dialog)
        self.convert_gamma_action.triggered.connect(self.convert_gamma_dialog)

        color_plan_menu = self.menubar.addMenu('&Color Space')
        color_plan_menu.addAction(self.rgb_action)
        color_plan_menu.addAction(self.hsl_action)
        color_plan_menu.addAction(self.hsv_action)
        color_plan_menu.addAction(self.ycbcr601_action)
        color_plan_menu.addAction(self.ycbcr709_action)
        color_plan_menu.addAction(self.ycocg_action)
        color_plan_menu.addAction(self.cmy_action)

        self.channel_menu = self.menubar.addMenu('&Channels')
        self.channel_menu.addAction(self.first_channel_action)
        self.channel_menu.addAction(self.second_channel_action)
        self.channel_menu.addAction(self.third_channel_action)
        self.channel_menu.addAction(self.all_channel_action)

        brightness_menu = self.menubar.addMenu('&Brightness correction')
        brightness_menu.addAction(self.show_hist_action)
        brightness_menu.addAction(self.show_hist_coef_action)
        brightness_menu.addAction(self.assign_coef_action)
        brightness_menu.addAction(self.perform_correction_action)

        self.show_hist_action.triggered.connect(self.show_hist)
        self.show_hist_coef_action.triggered.connect(self.show_hist_coef)
        self.assign_coef_action.triggered.connect(self.assign_coef)
        self.perform_correction_action.triggered.connect(self.perform_correction)

        self.scroll_area.setWidget(self.label)
        self.scroll_area.setWidgetResizable(True)

        self.setCentralWidget(self.scroll_area)

        self.exit_action.setStatusTip('Exit application')
        self.exit_action.triggered.connect(qApp.quit)

        self.open_action.setStatusTip('Open file')
        self.open_action.triggered.connect(self.open_file)

        self.save_pnm_action.setStatusTip('.pnm file')
        self.save_pnm_action.triggered.connect(self.save_pnm_file)
        self.save_png_action.setStatusTip('.png file')
        self.save_png_action.triggered.connect(self.save_png_file)

        self.pick_color_action.setStatusTip('Pick color')
        self.pick_color_action.triggered.connect(self.color_picker)
        self.pen_width_action.triggered.connect(self.pen_width_dialog)
        self.set_transparency_action.triggered.connect(self.transparency_dialog)

        self.rgb_action.triggered.connect(self.convert_to_rgb)
        self.hsl_action.triggered.connect(self.convert_to_hsl)
        self.hsv_action.triggered.connect(self.convert_to_hsv)
        self.cmy_action.triggered.connect(self.convert_to_cmy)
        self.ycbcr601_action.triggered.connect(self.convert_to_ycbcr601)
        self.ycocg_action.triggered.connect(self.convert_to_ycocg)
        self.ycbcr709_action.triggered.connect(self.convert_to_ycbcr709)

        self.first_channel_action.triggered.connect(self.first_channel_show)
        self.second_channel_action.triggered.connect(self.second_channel_show)
        self.third_channel_action.triggered.connect(self.third_channel_show)
        self.all_channel_action.triggered.connect(self.all_channel_show)

        # располагаем окно в левом верхнем углу экрана
        self.setGeometry(0, 0, 1000, 500)
        self.setWindowTitle('PetPixel')
        self.setWindowIcon(QIcon('images/icon.png'))
        self.show()

    def first_channel_show(self):
        self.data_image.curr_channel = di.Channel.first
        self.display_image()

    def second_channel_show(self):
        self.data_image.curr_channel = di.Channel.second
        self.display_image()

    def third_channel_show(self):
        self.data_image.curr_channel = di.Channel.third
        self.display_image()

    def all_channel_show(self):
        self.data_image.curr_channel = di.Channel.All
        self.display_image()

    def show_resampling_menu(self):
        self.addDockWidget(Qt.BottomDockWidgetArea, self.resampling)

    def resampling_algorithm(self, text):
        self.resampling_algorithm_name = text

    def resample(self):
        width = self.resampling_width_line.text()
        height = self.resampling_height_line.text()
        x = self.resampling_x.text()
        y = self.resampling_y.text()

        if width == '' or height == '' or x == '' or y == '':
            pass
        else:
            b, c = 0.0, 0.5
            offset_x, offset_y = float(x.replace(',', '.')), float(y.replace(',', '.'))
            if self.resampling_algorithm_name == "BC-Splines":
                text, ok = QInputDialog.getText(self, '',
                                                'Enter b and c with a space between:')
                if ok:
                    b, c = map(float, map(lambda i: i.replace(',', '.'), text.split(' ')))

            width, height = int(width), int(height)
            print(width, height, self.resampling_algorithm_name)
            res = Resampling()
            self.data_image.height, self.data_image.width, self.data_image.curr_colormap = res.resample(
                self.data_image.curr_colormap, height, width, self.resampling_algorithm_name, offset_x, offset_y, b, c)
            self.display_image()

    def show_hist(self):
        self.brightness_hist_window.setVisible(True)
        hist_filename = self.brightness_correction.make_hist_picture_without_coef(
            self.data_image.normalize_data(self.data_image.curr_colormap),
            self.data_image.color_space, self.data_image.curr_channel)
        label = QLabel()
        pixmap = QPixmap()
        pixmap.load(hist_filename)
        label.setPixmap(pixmap)
        self.brightness_hist_window.setWidget(label)
        self.addDockWidget(Qt.RightDockWidgetArea, self.brightness_hist_window)

    def show_hist_coef(self):
        self.brightness_hist_window.setVisible(True)
        hist_filename = self.brightness_correction.make_hist_picture(
            self.data_image.normalize_data(self.data_image.curr_colormap),
            self.data_image.color_space, self.data_image.curr_channel)
        label = QLabel()
        pixmap = QPixmap()
        pixmap.load(hist_filename)
        label.setPixmap(pixmap)
        self.brightness_hist_window.setWidget(label)
        self.addDockWidget(Qt.RightDockWidgetArea, self.brightness_hist_window)

    def assign_coef(self):
        text, ok = QInputDialog.getDouble(self, 'Brightness correction',
                                          'Enter ignoring coefficient:',
                                          min=0.0, max=0.5, value=0.0, decimals=8)
        if ok:
            self.brightness_correction.ignoring_coefficient = float(text)

    def perform_correction(self):
        new_colormap = self.brightness_correction.brightness_correction(
            self.data_image.normalize_data(self.data_image.curr_colormap),
            self.data_image.color_space, self.data_image.curr_channel)
        self.data_image.curr_colormap = self.data_image.unnormalize_data(new_colormap)
        self.brightness_hist_window.setVisible(False)
        self.display_image()

    def pen_width_dialog(self):

        text, ok = QInputDialog.getDouble(self, 'Pen Width',
                                          'Select the width for the pen in px:',
                                          min=0.01, max=200, value=0.0, decimals=2)
        if ok:
            self.line_drawing.width = float(text)

    def transparency_dialog(self):
        text, ok = QInputDialog.getDouble(self, 'Transparency',
                                          'Select the degree of transparency for the pen in %:',
                                          min=0, max=1, value=0.0, decimals=3)
        if ok:
            self.line_drawing.transparency = float(text)

    def mousePressEvent(self, event):
        if self.last_x is None:
            self.last_x = event.x() + self.scroll_area.horizontalScrollBar().value()
            self.last_y = event.y() + self.scroll_area.verticalScrollBar().value()
            return
        # еще нет открытого файла -> не на чем рисовать
        if self.label.pixmap() is None:
            return

        # игнорируем все клики за пределами canvas
        if event.pos() not in self.label.pixmap().rect():
            return

        _, _, _, menu_width = self.menubar.geometry().getCoords()
        # учитываем координаты прокруток
        new_x = event.x() + self.scroll_area.horizontalScrollBar().value()
        new_y = event.y() + self.scroll_area.verticalScrollBar().value()
        self.line_drawing.draw(self.last_x, self.last_y - menu_width, new_x, new_y - menu_width)

        self.last_x = None
        self.last_y = None

        self.display_image()

    def assign_gamma_dialog(self):
        value, ok = QInputDialog.getDouble(self, 'Assign Ɣ',
                                           'Input the value of Ɣ:', value=0.0, min=0, max=100, decimals=3)
        if ok:
            self.data_image.assign_gamma(value)
            self.display_image()

    def convert_gamma_dialog(self):
        value, ok = QInputDialog.getDouble(self, 'Convert to Ɣ',
                                           'Input the value of Ɣ:', value=0.0, min=0, max=100, decimals=3)
        if ok:
            self.data_image.convert_to_gamma(value)
            if self.data_image.curr_colormap.size != 0:
                self.display_image()

    def color_picker(self):
        self.color_dialog.exec_()
        self.line_drawing.color = self.color_dialog.selectedColor()
        self.selected_color_label.pixmap().fill(self.line_drawing.color)

    def dithering_window(self):
        self.dithering_window = d.DitheringWindow(self.data_image.copy())

    def change_color_space(self):
        self.statusbar.removeWidget(self.color_space_label)
        self.color_space_label = QLabel(f"{self.data_image.color_space}")
        self.statusbar.addPermanentWidget(self.color_space_label, 10)

    def convert_to_rgb(self):
        self.data_image.convert_to_rgb()
        self.change_color_space()

        self.first_channel_action.setText('&Red')
        self.second_channel_action.setText('&Green')
        self.third_channel_action.setText('&Blue')

        self.display_image()

    def convert_to_hsl(self):
        self.data_image.convert_to_hsl()
        self.change_color_space()

        self.first_channel_action.setText('&Hue')
        self.second_channel_action.setText('&Saturation')
        self.third_channel_action.setText('&Lightness')

        self.display_image()

    def convert_to_hsv(self):
        self.data_image.convert_to_hsv()
        self.change_color_space()

        self.first_channel_action.setText('&Hue')
        self.second_channel_action.setText('&Saturation')
        self.third_channel_action.setText('&Value')

        self.display_image()

    def convert_to_cmy(self):
        self.data_image.convert_to_cmy()
        self.change_color_space()

        self.first_channel_action.setText('&Cyan')
        self.second_channel_action.setText('&Magenta')
        self.third_channel_action.setText('&Yellow')

        self.display_image()

    def convert_to_ycbcr601(self):
        self.data_image.convert_to_ycbcr601()
        self.change_color_space()

        self.first_channel_action.setText('&Y')
        self.second_channel_action.setText('&Cb')
        self.third_channel_action.setText('&Cr')

        self.display_image()

    def convert_to_ycbcr709(self):
        self.data_image.convert_to_ycbcr709()
        self.change_color_space()

        self.first_channel_action.setText('&Y')
        self.second_channel_action.setText('&Cb')
        self.third_channel_action.setText('&Cr')

        self.display_image()

    def convert_to_ycocg(self):
        self.data_image.convert_to_ycocg()
        self.change_color_space()

        self.first_channel_action.setText('&Y')
        self.second_channel_action.setText('&Co')
        self.third_channel_action.setText('&Cg')

        self.display_image()

    def display_image(self):
        self.canvas = QPixmap(self.data_image.get_qimage())
        self.label.setPixmap(self.canvas)

    def open_file(self):
        file_path = QFileDialog.getOpenFileName()[0]
        try:
            self.data_image.set_data(*read.reading(file_path))
            self.display_image()
        except OSError:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("File does not exist")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        except (ValueError, ex.InvalidFileStructureException):
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("The file structure is incorrect, the file may be damaged.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def save_file(self, file_format):
        file_path = QFileDialog.getSaveFileName()[0]
        self.data_image.curr_format = file_format
        try:
            write.save_data(file_path, *self.data_image.get_data())
        except ex.InvalidFileFormatException:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("File format is not supported")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def save_png_file(self):
        self.save_file('PNG')

    def save_pnm_file(self):
        self.save_file("P6\n")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyle('Fusion')
    main = MainWindow()
    # запуск приложения пока пользователь не закроет окно
    sys.exit(app.exec_())

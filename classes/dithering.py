from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout, QGridLayout, QPushButton, QMessageBox, QFileDialog, \
    QInputDialog, QScrollArea

import scripts.exceptions as ex
from scripts import write, dithering_algorithms as da


class DitheringWindow(QWidget):
    def __init__(self, data_image):
        super().__init__()

        # глобальные переменные
        self.label = QLabel('image on canvas')
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setWidgetResizable(True)
        self.algorithm = "Floyd-Steinberg"
        self.bits = 1
        self.data_image = data_image
        self.channels = 3
        self.init()

    def init(self):
        vlayout = QVBoxLayout()
        vlayout.addStretch(1)

        algorithm_label = QLabel('Select the dithering algorithm:')
        vlayout.addWidget(algorithm_label)

        combo_algorithm = QComboBox()
        combo_algorithm.resize(200, 25)
        combo_algorithm.addItems(["Floyd-Steinberg", "Random", "Ordered(8x8)", "Atkinson"])
        combo_algorithm.activated[str].connect(self.on_activated_algorithm)

        vlayout.addWidget(combo_algorithm)

        bits_label = QLabel('Select the number of bits per channel:')
        vlayout.addWidget(bits_label)

        combo_bits = QComboBox()
        combo_bits.resize(200, 25)
        combo_bits.addItems(['1', '2', '3', '4', '5', '6', '7', '8'])
        combo_bits.activated[str].connect(self.on_activated_bits)

        vlayout.addWidget(combo_bits)

        perform_button = QPushButton('Perform dithering')
        perform_button.setStyleSheet('background-color: white')
        perform_button.clicked.connect(self.perform_dithering)
        vlayout.addWidget(perform_button)

        save_button = QPushButton('Save')
        save_button.setStyleSheet('background-color: white')
        save_button.clicked.connect(self.save)
        vlayout.addWidget(save_button)

        layout = QGridLayout()
        layout.addWidget(self.scroll_area, 0, 1)
        layout.addLayout(vlayout, 0, 0, alignment=QtCore.Qt.AlignmentFlag(1))
        self.setLayout(layout)

        self.setGeometry(50, 50, 1300, 700)
        self.setWindowIcon(QIcon('../images/icon.png'))
        self.setWindowTitle('Dithering')

        if self.data_image.curr_colormap.size == 0:
            self.display_gradient()

        self.display_image()
        self.show()

    def display_image(self):
        self.canvas = QPixmap(self.data_image.get_qimage())
        self.label.setPixmap(self.canvas)

    def perform_dithering(self):
        if self.algorithm == 'Floyd-Steinberg':
            self.data_image = da.floyd_steinberg(self.data_image, self.bits, self.channels)
            self.display_image()
        elif self.algorithm == 'Atkinson':
            self.data_image = da.atkinson(self.data_image, self.bits, self.channels)
            self.display_image()
        elif self.algorithm == 'Ordered(8x8)':
            self.data_image = da.ordered(self.data_image, self.bits, self.channels)
            self.display_image()
        elif self.algorithm == 'Random':
            self.data_image = da.random_alg(self.data_image, self.bits, self.channels)
            self.display_image()

    def save(self):
        file_path = QFileDialog.getSaveFileName()[0]
        try:
            write.save_data(file_path, *self.data_image.get_data())
        except ex.InvalidFileFormatException:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("File format is not supported")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        self.close()

    def on_activated_algorithm(self, text):
        self.algorithm = text

    def on_activated_bits(self, text):
        self.bits = int(text)

    def display_gradient(self):
        text, ok = QInputDialog.getText(self, 'Size of gradient', 'Enter height and width with a space between:')
        if ok:
            height, width = map(int, text.split(' '))
        else:
            height, width = 500, 500

        format_ = "P6\n"
        self.channels = 1
        self.data_image.set_data(height, width, da.gradient(height, width), format_)


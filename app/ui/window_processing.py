# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""
from typing import Callable

import cv2
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QGroupBox, QLabel, QPushButton, QProgressBar, QFileDialog
import numpy as np
from k_util import Region
from k_vision import visual, text

from logic.transfer_net import TransferNet
from ui.window import Window

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


K_IMAGE_PREVIEW_SIZE = 258


class WindowProcessing(Window):

    def __init__(self, on_press_back: Callable):
        super().__init__()

        self.on_press_back = on_press_back

        self.content_image = None
        self.style_image = None

        self.progress = 0
        self.progress_bar = None
        self.preview_label = None
        self.layout = None
        self.process_active = True
        self.net = TransferNet()

    def begin_style_transfer(self, content_image, style_image):
        print(content_image, style_image)
        self.content_image = content_image
        self.style_image = style_image
        self.process_active = True
        self.net.prepare_network(content_image, style_image)

    def render(self, parent: QMainWindow):
        super().render(parent)

        # Set a good widget size.
        parent.setFixedWidth(340)
        parent.setMinimumHeight(300)

        # Create the group box.
        self.main_layout.setContentsMargins(self.PADDING, 0, self.PADDING, self.PADDING)
        self.layout = layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        group_box = QGroupBox(self.main_widget)
        group_box.setAlignment(QtCore.Qt.AlignCenter)
        group_box.setLayout(layout)
        self.add_widget(group_box)

        # Create the preview image.
        preview_image = np.zeros((K_IMAGE_PREVIEW_SIZE, K_IMAGE_PREVIEW_SIZE, 3), dtype=np.uint8)
        preview_image[:, :] = (255, 255, 0)
        self.preview_label = QLabel()
        # self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.render_image(preview_image, self.preview_label)
        layout.addWidget(self.preview_label)

        self.show_transfer_ui()
        self.show_window(parent)
        self.process()

    def back(self):
        self.process_active = False
        self.on_press_back()

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def show_transfer_ui(self):
        self.clear_layout()
        self.layout.addWidget(self.preview_label)

        # Set the widget label/title.
        label = QLabel("Transferring Style")
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(label)

        # Set up the progress bar.
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(258)
        self.layout.addWidget(self.progress_bar)

        # Create the confirmation button.
        self.add_button("Cancel", self.back)

    def add_button(self, text: str, action: Callable):
        """ Add a button to the scene. """
        button = QPushButton(text)
        button.setFixedWidth(258)
        button.clicked.connect(action)
        self.layout.addWidget(button)

    def show_completed_ui(self):
        self.clear_layout()
        self.layout.addWidget(self.preview_label)

        # Set the widget label/title.
        label = QLabel("Complete")
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(label)

        # Create the confirmation button.
        self.add_button("Save Image", self.save_target)
        self.add_button("Save Grid", self.save_grid)
        self.add_button("Back", self.back)

    def render_image(self, image: np.ndarray, target_label: QLabel):
        """ Render this CV2 Image into the label. """
        height, width, color = image.shape
        byte_value = color * width
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        q_image = QImage(image, width, height, byte_value, QImage.Format_RGB888)
        q_pix_map = QPixmap.fromImage(q_image)
        target_label.setAlignment(QtCore.Qt.AlignCenter)
        target_label.setPixmap(q_pix_map)

    def save_target(self):
        file_name = self.open_save_dialog()
        if file_name is not None:
            cv2.imwrite(file_name, self.net.get_current_target_image())

    def save_grid(self):
        file_name = self.open_save_dialog()

        image_size = 360
        pad = 20
        width = (image_size + pad) * 3 + pad
        height = image_size + 2 * pad
        text_height = 32

        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        images = [self.content_image, self.style_image, self.net.get_current_target_image()]
        labels = ["Content", "Style", "Result"]

        for i in range(3):
            image_i = images[i]
            image_i = cv2.resize(image_i, (image_size, image_size))
            lanel_i = labels[i]
            x = i * (image_size + pad) + pad
            y = pad
            r = Region(x, x + image_size, y, y + image_size)
            canvas = visual.safe_implant_with_region(canvas, image_i, r)
            text_region = Region(x, x + image_size, height - pad - text_height, height - pad)
            canvas = text.write_into_region(
                canvas,
                lanel_i.upper(),
                text_region,
                bg_opacity=0.5,
                bg_color=(0, 0, 0))

        if file_name is not None:
            cv2.imwrite(file_name, canvas)

    def open_save_dialog(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            parent=self.parent,
            filter="Images (*.png, *.jpg)")
        if file_name:
            print(file_name)
        return file_name

    def process(self):
        # Update the progress bar.

        if not self.process_active:
            return

        print("processing")
        progress = self.net.step()
        # self.progress += 0.01
        # progress = self.progress
        progress = min(100, int(progress * 100))
        self.progress_bar.setValue(progress)

        target_image = self.net.get_current_target_image()
        target_image = cv2.resize(target_image, (K_IMAGE_PREVIEW_SIZE, K_IMAGE_PREVIEW_SIZE))
        self.render_image(target_image, self.preview_label)

        # Recurse if we are not done.
        if progress < 100 and self.process_active:
            QtCore.QTimer.singleShot(1, self.process)
        else:
            self.show_completed_ui()
            self.process_active = False


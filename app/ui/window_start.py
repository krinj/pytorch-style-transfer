# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

import os
from typing import Callable, List

import cv2
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QGroupBox, QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget, \
    QFileDialog
import numpy as np

from ui.window import Window

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


K_IMAGE_PREVIEW_SIZE = 258


class SelectionBoxInfo:
    def __init__(self, name: str, image_update_function):
        self.image: np.ndarray = None
        self.image_path: str = None
        self.name = name
        self.image_preview_label: QLabel = None
        self.image_path_label: QLabel = None
        self.image_update_function = image_update_function

    def update(self, image_path: str):
        self.image_path = image_path
        if self.image_path is not None:
            self.image = cv2.imread(image_path)

            # Ratio Lock
            # Find the longest size.
            image_width = self.image.shape[0]
            image_height = self.image.shape[1]

            short_size = min(image_width, image_height)
            long_size = max(image_width, image_height)
            c_start = (long_size - short_size) // 2
            c_end = c_start + short_size

            if image_width > image_height:
                self.image = self.image[c_start:c_end, :]
            elif image_width < image_height:
                self.image = self.image[:, c_start:c_end]

            self.image = cv2.resize(self.image, (K_IMAGE_PREVIEW_SIZE, K_IMAGE_PREVIEW_SIZE))
            self.image_path_label.setText(image_path)
            self.image_update_function(self.image, self.image_preview_label)
        else:
            self.image = None


class WindowStart(Window):

    def __init__(self, on_process_start: Callable):
        super().__init__()
        self.on_process_start = on_process_start

        # Selection Boxes.
        self.selection_boxes: List[SelectionBoxInfo] = [
            SelectionBoxInfo("Content Image", self.render_image),
            SelectionBoxInfo("Style Image", self.render_image)
        ]

    def on_press(self, i: int):
        file_path = self.open_file_dialog()
        selection_box_info = self.selection_boxes[i]
        selection_box_info.update(file_path)

    def on_press_start(self):
        """ Begin the style transfer operation. """
        content_image = self.selection_boxes[0].image
        style_image = self.selection_boxes[1].image
        self.on_process_start(content_image, style_image)
        print("Begin the style transfer.")

    def render(self, parent: QMainWindow):
        super().render(parent)

        # Set a good widget size.
        parent.setFixedWidth(920)
        parent.setFixedHeight(420)

        # Create the image selection boxes.
        image_selection_layout = QHBoxLayout()
        selector_widget = QWidget()
        self.add_widget(selector_widget)
        selector_widget.setLayout(image_selection_layout)

        # Create the content and style image selector.
        content_selector = self.render_selection_box(0)
        style_selector = self.render_selection_box(1)
        image_selection_layout.addWidget(content_selector)
        image_selection_layout.addWidget(style_selector)

        settings_box = self.render_settings_box()
        image_selection_layout.addWidget(settings_box)

        # Create the Settings Box
        # settings_layout = QHBoxLayout()
        # settings_widget = QWidget()
        # self.add_widget(settings_widget)
        # settings_widget.setLayout(settings_layout)
        #
        # settings_layout.addWidget(settings_box)

        self.show_window(parent)

    def render_selection_box(self, i: int):
        """ The single box to select and preview an image. """

        selector_box: SelectionBoxInfo = self.selection_boxes[i]

        single_selection_layout = QVBoxLayout()
        single_selection_layout.setAlignment(QtCore.Qt.AlignCenter)

        group_box = QGroupBox(selector_box.name)
        single_selection_layout.setAlignment(QtCore.Qt.AlignCenter)
        group_box.setLayout(single_selection_layout)

        # Create the preview avatar.
        preview_image = np.zeros((K_IMAGE_PREVIEW_SIZE, K_IMAGE_PREVIEW_SIZE, 3), dtype=np.uint8)
        preview_image[:, :] = (255, 255, 0)
        preview_label = QLabel()

        self.render_image(preview_image, preview_label)
        single_selection_layout.addWidget(preview_label)

        # Create the confirmation button.
        label = QLabel("No Image Selected")
        label.setFixedWidth(256)
        label.setAlignment(QtCore.Qt.AlignCenter)
        single_selection_layout.addWidget(label)

        # Set the references so we can update the label.
        selector_box.image_preview_label = preview_label
        selector_box.image_path_label = label

        # Create the confirmation button.
        button = QPushButton("Select Image")
        button.setFixedWidth(256)
        button.clicked.connect(lambda _: self.on_press(i))
        single_selection_layout.addWidget(button)

        return group_box

    def render_settings_box(self):
        """ The single box to select and preview an image. """
        single_selection_layout = QVBoxLayout()
        group_box = QGroupBox("Settings")
        single_selection_layout.setContentsMargins(0, 0, 0, 0)
        group_box.setLayout(single_selection_layout)

        top_widget = QWidget()
        top_layout = QVBoxLayout()
        top_widget.setLayout(top_layout)
        top_layout.setAlignment(QtCore.Qt.AlignTop)
        single_selection_layout.addWidget(top_widget)

        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_widget.setLayout(bottom_layout)
        bottom_layout.setAlignment(QtCore.Qt.AlignBottom)
        single_selection_layout.addWidget(bottom_widget)

        # Create field.
        button = QPushButton("Settings")
        top_layout.addWidget(button)
        button.clicked.connect(self.open_save_dialog)

        # Create the confirmation button.
        button = QPushButton("Start")
        button.clicked.connect(self.on_press_start)
        bottom_layout.addWidget(button)

        return group_box

    def render_image(self, image: np.ndarray, target_label: QLabel):
        """ Render this CV2 Image into the label. """
        height, width, color = image.shape
        byte_value = color * width
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        q_image = QImage(image, width, height, byte_value, QImage.Format_RGB888)
        q_pix_map = QPixmap.fromImage(q_image)
        target_label.setAlignment(QtCore.Qt.AlignCenter)
        target_label.setPixmap(q_pix_map)

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(parent=self.parent, filter="Images (*.png, *.jpg)")
        return file_name

    def open_save_dialog(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            parent=self.parent,
            filter="Images (*.png, *.jpg)")
        if file_name:
            print(file_name)
        return file_name


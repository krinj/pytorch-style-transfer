# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

import os
from typing import Callable
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QGroupBox, QLabel, QComboBox, QPushButton, QHBoxLayout, QWidget

from ui.window import Window

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class WindowStart(Window):

    def __init__(self):
        super().__init__()
        self.selected_project: str = None

    def style_choice(self, text: str):
        print("Combo Choose", text)
        self.selected_project = text

    def on_press(self):
        print(f"Button Press: {self.selected_project}")
        # self.on_project_selected(self.selected_project)

    def render(self, parent: QMainWindow):
        super().render(parent)

        # Set a good widget size.
        parent.setMinimumWidth(800)
        parent.setMinimumHeight(600)

        # Create the image selection boxes.
        image_selection_layout = QHBoxLayout()
        selector_widget = QWidget()
        self.add_widget(selector_widget)
        selector_widget.setLayout(image_selection_layout)

        # Create the content and style image selector.
        content_selector = self.render_selection_box()
        style_selector = self.render_selection_box()
        image_selection_layout.addWidget(content_selector)
        image_selection_layout.addWidget(style_selector)

        # Create the Settings Box
        settings_layout = QHBoxLayout()
        settings_widget = QWidget()
        self.add_widget(settings_widget)
        settings_widget.setLayout(settings_layout)
        settings_box = self.render_settings_box()
        settings_layout.addWidget(settings_box)

        self.show_window(parent)

    def render_selection_box(self):
        """ The single box to select and preview an image. """
        single_selection_layout = QVBoxLayout()
        single_selection_layout.setAlignment(QtCore.Qt.AlignCenter)

        group_box = QGroupBox("Content Image")
        group_box.setAlignment(QtCore.Qt.AlignCenter)
        group_box.setLayout(single_selection_layout)

        # Create the confirmation button.
        label = QLabel("No Image Selected")
        label.setFixedWidth(300)
        label.setAlignment(QtCore.Qt.AlignCenter)
        single_selection_layout.addWidget(label)

        # Create the confirmation button.
        button = QPushButton("Select Image")
        button.setFixedWidth(300)
        button.clicked.connect(self.on_press)
        single_selection_layout.addWidget(button)

        return group_box

    def render_settings_box(self):
        """ The single box to select and preview an image. """
        single_selection_layout = QVBoxLayout()
        group_box = QGroupBox("Settings")
        group_box.setAlignment(QtCore.Qt.AlignCenter)
        group_box.setLayout(single_selection_layout)
        return group_box
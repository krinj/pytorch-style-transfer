# -*- coding: utf-8 -*-

"""
This is the base class for rendering a sub-window within my app.
"""

from abc import abstractmethod
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget

__author__ = "Jakrin Juangbhanich"
__copyright__ = "Copyright 2018, GenVis Pty Ltd."
__email__ = "krinj@genvis.co"


class Window:

    PADDING: int = 20

    def __init__(self):
        self.parent: QMainWindow = None
        self.main_layout: QVBoxLayout = None
        self.main_widget: QWidget = None

    @abstractmethod
    def render(self, parent: QMainWindow):
        """ Create the main widget window and layout. Everything should be drawn into the main_layout object. """
        self.parent = parent
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(self.PADDING, self.PADDING, self.PADDING, self.PADDING)
        self.main_widget = QWidget(parent)
        self.main_widget.setLayout(self.main_layout)

    def show_window(self, parent: QMainWindow):
        """ Render the main window screen with respect to the parent/master window. """
        parent.setCentralWidget(self.main_widget)
        parent.show()

    def add_widget(self, widget: QWidget):
        """ Shortcut function to add a widget to the main layout object. """
        self.main_layout.addWidget(widget)

    def on_resize(self, event: QResizeEvent):
        pass


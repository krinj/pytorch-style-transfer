# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""
from PyQt5 import QtCore
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QMainWindow, QAction, QMenuBar, QDesktopWidget

from ui.window import Window
from ui.window_start import WindowStart

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Editor(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Clustering GT Editor'
        self.setWindowTitle(self.title)
        self.initialize_menu_bar()
        self.window_splash = WindowStart()
        self.window_editor = WindowStart()
        self.current_window: Window = None
        self.show_splash()

    def initialize_menu_bar(self):

        action_exit = QAction('&Exit', self)
        action_exit.setShortcut('Ctrl+Q')
        action_exit.setStatusTip('Exit application')
        action_exit.triggered.connect(self.close)

        menu: QMenuBar = self.menuBar()
        menu.setNativeMenuBar(False)
        menu.setContentsMargins(20, 20, 20, 20)
        file_menu = menu.addMenu('&File')
        file_menu.addAction(action_exit)

    def show_window(self, window: Window):
        self.current_window = window
        window.render(self)
        self.center_screen()

    def show_splash(self):
        self.show_window(self.window_splash)
    #
    # def on_project_selected(self, project_name: str):
    #     print(f"Main Project Selected {project_name}")
    #     self.window_editor.set_project(project_name)
    #     self.show_window(self.window_editor)

    def center_screen(self):
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == QtCore.Qt.Key_Escape:
            print("Escape Pressed")

    def resizeEvent(self, event):
        print("Screen Resized")
        self.current_window.on_resize(event)
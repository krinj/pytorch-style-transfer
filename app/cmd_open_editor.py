#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Open the desktop GUI for style transfer.
"""

from k_util.logger import Logger
from PyQt5.QtWidgets import QApplication
from ui.editor import Editor

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


if __name__ == "__main__":
    Logger.header("Running cmd_run_data_editor")

    app = QApplication([])
    app.setStyle('Fusion')

    editor = Editor()
    app.exec()

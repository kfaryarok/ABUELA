#!/usr/bin/env python
# coding: utf-8

"""
ABUELA

A Big, Useful, & Efficient LaTeX Application
"""

# Import modules and classes
from atexit import register

from PyQt5.QtWidgets import QApplication
from gui import App
from utility import Utility

if __name__ == "__main__":
    # Register the clearCache function as a pre-exit function,
    # ergo disk space will be saved upon exit.
    utils = Utility()
    register(utils.clearCache)

    # Start the app
    app = QApplication([])
    ex = App()
    app.exec_()

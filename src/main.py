#!/usr/bin/env python
# coding: utf-8

"""
ABUELA

A Big, Useful, & Efficient LaTeX Application
"""

# Import modules and classes
from PyQt5.QtWidgets import QApplication
from gui import App

if __name__ == "__main__":
    # Start the app
    app = QApplication([])
    ex = App()
    app.exec_()

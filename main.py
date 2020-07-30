#!/usr/bin/env python
# coding: utf-8

"""
ABUELA

A Big, Useful, & Efficient LaTeX Application
"""

# Import modules and classes
from PyQt5.QtWidgets import QApplication
from gui import App

# Start the app
app = QApplication([])
ex = App()
app.exec_()

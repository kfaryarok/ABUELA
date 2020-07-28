#!/usr/bin/env python
# coding: utf-8

# Import modules and classes
from PyQt5.QtWidgets import QApplication
from frontend import App

# Start the app
app = QApplication([])
ex = App()
app.exec_()

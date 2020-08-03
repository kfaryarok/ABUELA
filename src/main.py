#!/usr/bin/env python
# coding: utf-8

"""
ABUELA

A Big, Useful, & Efficient LaTeX Application
"""

# Import modules and classes
from atexit import register

from compile import Compile
from gui import App
from PyQt5.QtWidgets import QApplication
from utility import Utility

if __name__ == "__main__":
	# Create the exitClear function, and register it.
	# Register the clearCache function as a pre-exit function,
	# ergo disk space will be saved upon exit.
	def exitClear():
		"""
		This function should utilize all of the existing cache
		cleaning methods available to optimize disk space.
		"""
		utils = Utility()
		utils.clearCache()
		comp = Compile()
		comp.clean()

	register(exitClear)

	# Start the app
	app = QApplication([])
	ex = App()
	app.exec_()

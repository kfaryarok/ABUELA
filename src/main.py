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
		This function is the exit-function of the program.
		Just before the program terminates, it will run this function once.

		This function should utilize all of the existing cache
		cleaning methods available to optimize disk space.

		This function should also make sure to save a snapshot or
		save any other data necessary to be saved on termination.
		"""
		# Clear the cache
		utils = Utility(False)
		utils.clear_cache()
		# Try to save settings
		try:
			utils.set_settings(ex.settings)
		except NameError:
			pass
		# Clean the compile cache
		comp = Compile(False)
		comp.clean()

	# Register the exit function
	register(exitClear)

	# Loop until the non-default exit code is returned
	while True:
		# Start the app
		app = QApplication([])
		ex = App()
		exit_code = app.exec_()

		# If the exit code is the restart exit code, then restart the app
		if exit_code == ex.restart_code:
			# Save memory space and banish pointer to class
			if app:
				del app
			if ex:
				del ex
			if exit_code:
				del exit_code
		# Otherwise, terminate the program
		else:
			break

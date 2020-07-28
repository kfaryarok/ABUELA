#!/usr/bin/env python
# coding: utf-8

# Imports
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QPushButton
from win32api import GetSystemMetrics
from utility import Utility


# Initialize class
class App(QWidget):
	# Resize PyQT signal
	resized = pyqtSignal()

	# Pull settings
	settings = Utility.getSettings()

	# Constructor
	def __init__(self):
		super().__init__()

		# Get screen data
		self.screenWidth = Utility.getSettings()[0]
		self.screenHeight = Utility.getSettings()[1]

		# # Resize connection
		# # Due to the resize function, all positioning in this
		# # constructor method will be set to (0, 0), and will
		# # rely on the initial showing of the window to trigger
		# # the resize function to move all the elements in to place.
		# self.resized.connect(self.resizeElements)

		# Set min size
		self.setMinimumSize(int(self.screenWidth * self.settings["minRatio"]),
		                    int(self.screenHeight * self.settings["minRatio"]))

		# # Set icon
		# self.setWindowIcon(QtGui.QIcon("resources\\logos.png"))

		# Title
		self.title = self.settings["windowTitle"]

		# Screen coordinate initialization
		self.left = self.settings["initX"]
		self.top = self.settings["initY"]

		# Calculate gui size
		self.width = int(self.screenWidth * self.settings["screenRatio"])
		self.height = int(self.screenHeight * self.settings["screenRatio"])

		# # Initialize elements
		# self.initElements()
		# Call GUI creation
		self.initUI()

		# # Display slide
		# self.setSlide(self.curSlide)
		# self.resizeElements()

	def initUI(self):
		# Set the title
		self.setWindowTitle(self.title)
		# Set the GUI size
		self.setGeometry(self.left, self.top, self.width, self.height)
		# Show the GUI
		self.showGUI()

	def makeText(self, xPos, yPos, width, height):
		textBox = QLineEdit(self)
		textBox.move(xPos, yPos)
		textBox.resize(width, height)
		return textBox

	def makePic(self, fileName, xPos, yPos, width, height):
		label = QLabel(self)
		pixelMap = QPixmap(fileName)
		label.setPixmap(pixelMap)
		label.setScaledContents(True)
		label.move(xPos, yPos)
		label.resize(width, height)
		return label

	def makeButton(self, text, xPos, yPos, width, height):
		button = QPushButton(text, self)
		button.move(xPos, yPos)
		button.resize(width, height)
		return button

	def showGUI(self):
		# Show the GUI
		self.show()

	def hideGUI(self):
		# Show the GUI
		self.hide()

#!/usr/bin/env python
# coding: utf-8

# Imports
from PyQt5.QtCore import pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QPushButton, QPlainTextEdit
from keyboard import is_pressed as isKeyPressed
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
		self.screenWidth = Utility.getScreen()[0]
		self.screenHeight = Utility.getScreen()[1]

		# # Resize connection
		# # Due to the resize function, all positioning in this
		# # constructor method will be set to (0, 0), and will
		# # rely on the initial showing of the window to trigger
		# # the resize function to move all the elements in to place.
		# self.resized.connect(self.resizeElements)

		# Set min size
		self.setMinimumSize(int(self.screenWidth * self.settings["minRatio"]),
		                    int(self.screenHeight * self.settings["minRatio"]))

		# Set icon
		self.setWindowIcon(QIcon("resources\\logo.jpg"))

		# Title
		self.title = self.settings["windowTitle"]

		# Screen coordinate initialization
		self.left = self.settings["initX"]
		self.top = self.settings["initY"]

		# Calculate gui size
		self.width = int(self.screenWidth * self.settings["screenRatio"])
		self.height = int(self.screenHeight * self.settings["screenRatio"])

		# Initialize elements
		# Default parameter values are all 0 because self.resizeElements
		# will update the positioning and size of each element regardless
		self.editorBox = self.makeTextBox()
		self.editorBox.setFont(QFont(self.settings["editorFont"], self.settings["editorSize"]))
		self.editorBox.setCursorWidth(self.settings["cursorWidth"])
		self.editorBox.installEventFilter(self)

		# Call GUI creation
		self.initUI()

		# Display slide
		# Later, if more screens are added, 'slides' are implemented-
		# A slide is basically a function or some algorithm that
		# changes and updates all elements to the latest 'slide'.
		# (A slide being the latest UI interface that needs to be drawn)
		self.showEditor()
		self.resizeElements()

	def eventFilter(self, obj, event):
		if obj is self.editorBox and event.type() == QEvent.KeyPress:
			if event.key() in (Qt.Key_Return, Qt.Key_Enter) and isKeyPressed("shift"):
				self.editorBox.insertPlainText(" \\\\\n")
				return True
		return super(App, self).eventFilter(obj, event)

	def initUI(self):
		# Set the title
		self.setWindowTitle(self.title)
		# Set the GUI size
		self.setGeometry(self.left, self.top, self.width, self.height)
		# Show the GUI
		self.showGUI()

	def makeText(self, xPos=0, yPos=0, width=0, height=0):
		textBox = QLineEdit(self)
		textBox.move(xPos, yPos)
		textBox.resize(width, height)
		return textBox

	def makeTextBox(self, xPos=0, yPos=0, width=0, height=0):
		textBox = QPlainTextEdit(self)
		textBox.move(xPos, yPos)
		textBox.resize(width, height)
		return textBox

	def makePic(self, fileName, xPos=0, yPos=0, width=0, height=0):
		label = QLabel(self)
		pixelMap = QPixmap(fileName)
		label.setPixmap(pixelMap)
		label.setScaledContents(True)
		label.move(xPos, yPos)
		label.resize(width, height)
		return label

	def makeButton(self, text, xPos=0, yPos=0, width=0, height=0):
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

	def showEditor(self):
		self.editorBox.show()
		return self.resizeElements()

	def resizeElements(self):
		# Update window size variables
		self.width = self.frameGeometry().width()
		self.height = self.frameGeometry().height()

		# Update each element
		self.editorBox.move(0, 0)
		self.editorBox.resize(self.width / 2, self.height)

#!/usr/bin/env python
# coding: utf-8

# Imports
from random import randint
from threading import Thread
from time import sleep, time
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QPushButton, QPlainTextEdit
from keyboard import is_pressed as isKeyPressed
from compile import compileToImage
from project import Project
from utility import Utility


# Initialize class
class App(QWidget):
	# Create instance of Utility for later usage
	utils = Utility()

	# Pull settings
	settings = utils.getSettings()

	# Clear cache
	utils.clearCache()

	# Open new project (remove this part and integrate Open File, when the Open File features is ready)
	project = Project("../project/current.tex")

	# Set default compiler live identifier number
	live = 0

	# Constructor
	def __init__(self):
		super().__init__()

		# Get screen data
		self.screenWidth = self.utils.getScreen()[0]
		self.screenHeight = self.utils.getScreen()[1]

		# Set min size
		minWidth = int(self.screenWidth * self.settings["minRatio"])
		minHeight = int(self.screenHeight * self.settings["minRatio"])
		self.setMinimumSize(minWidth, minHeight)

		# Set icon
		self.setWindowIcon(QIcon("../resources/logo.jpg"))

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

		self.editorCompiled = self.makePic("../resources/canvas.jpg")

		# Call GUI creation
		self.initUI()
		self.resizeEvent()

	def eventFilter(self, obj, event):
		"""
		The event filter is the function called every time an event is generated.
		In most cases, an event is a keystroke.

		This is a function called on by the PyQt5 library during GUI
		interactions, it is not called within this code.

		This function is utilized for many usages:
		- Key Binds
		- Auto Save
		- Live Compile
		"""
		if obj is self.editorBox and event.type() == QEvent.KeyPress:
			# Key Binds
			# Shift + Return = Add / and newline
			if isKeyPressed("return") and isKeyPressed("shift"):
				self.editorBox.insertPlainText("\\\\\n")
				return True

			# Update project
			self.project.save(self.editorBox.toPlainText(), overwrite=True)

			# Compile
			# Set the current live ID and pass it to the function
			liveID = randint(0, 999999999999999)
			self.live = liveID
			# Set the time at which to call the live update
			liveUpdate = time() + self.settings["liveUpdate"]
			# Initialize the process
			p = Thread(target=self.updateLive, args=[liveID, liveUpdate])
			p.setDaemon(True)
			p.start()
		return super(App, self).eventFilter(obj, event)

	def updateLive(self, liveID, liveUpdate):
		"""
		This function is used to compile and update the image
		displaying the live version of the LaTeX source code.

		:param liveID: An ID which is passed just before called. If the global live ID is not equal to this function's
		live ID, then this function will terminate (another key was pressed, therefore this function is old and the
		new function should compile together the new LaTeX source code)

		:param liveUpdate: The timestamp to wait until to start execution of the function. This is used so that
		if the user is typing a word or line, the next key the user presses will generate a new live ID, and
		therefore within the time frame set by the update time, the new function will overwrite
		ths current function's execution.

		This function doesn't return any data, it calls directly on the editorCompiled attribute and updates the image.
		"""
		# Wait until it's time to update the live
		while time() < liveUpdate:
			sleep(0.1)
		# Check if the liveID is this function's ID
		if self.live != liveID:
			return
		# If the ID is equal, then continue...
		pageIndex = 1  # TO DO (ADD SCROLL ELEMENT WHICH ALTERS THIS VALUE & MAKE THIS VALUE AN ATTRIBUTE)
		compiledReturnData = compileToImage(self.settings["liveQuality"])
		if compiledReturnData[0]:
			fileName = "{path}{index}.jpg".format(path=compiledReturnData[0], index=pageIndex)
			pixelMap = QPixmap(fileName)
			self.editorCompiled.setPixmap(pixelMap)
			self.editorCompiled.setScaledContents(True)
		else:
			# If there is a compilation error... (otherwise, the second
			# item would be returned as false from the compileToImage function)
			if compiledReturnData[1]:
				# Do something with compiledReturnData[1] to display the error message
				pass

	def initUI(self):
		"""
		A function which sets the basics of the window- title, size, and displaying it.
		"""
		# Set the title
		self.setWindowTitle(self.title)
		# Set the GUI size
		self.setGeometry(self.left, self.top, self.width, self.height)
		# Show the GUI
		self.showGUI()

	def makeText(self, xPos=0, yPos=0, width=0, height=0):
		"""
		A function to create a new single line edit box.

		:param xPos: The left-top x position of the box.
		:param yPos: The left-top y position of the box.
		:param width: The width of the box.
		:param height: The height of the box.
		:return: Returns the created element.
		"""
		textBox = QLineEdit(self)
		textBox.move(xPos, yPos)
		textBox.resize(width, height)
		return textBox

	def makeTextBox(self, xPos=0, yPos=0, width=0, height=0):
		"""
		A function to create a new multi line edit box.

		:param xPos: The left-top x position of the box.
		:param yPos: The left-top y position of the box.
		:param width: The width of the box.
		:param height: The height of the box.
		:return: Returns the created element.
		"""
		textBox = QPlainTextEdit(self)
		textBox.move(xPos, yPos)
		textBox.resize(width, height)
		return textBox

	def makePic(self, fileName, xPos=0, yPos=0, width=0, height=0):
		"""
		A function to create a new picture element.

		:param fileName: The path to the file to display.
		:param xPos: The left-top x position of the box.
		:param yPos: The left-top y position of the box.
		:param width: The width of the box.
		:param height: The height of the box.
		:return: Returns the created element.
		"""
		label = QLabel(self)
		pixelMap = QPixmap(fileName)
		label.setPixmap(pixelMap)
		label.setScaledContents(True)
		label.move(xPos, yPos)
		label.resize(width, height)
		return label

	def makeButton(self, text, xPos=0, yPos=0, width=0, height=0):
		"""
		A function to create a new button element.

		:param text: The text that should be displayed on the button.
		:param xPos: The left-top x position of the box.
		:param yPos: The left-top y position of the box.
		:param width: The width of the box.
		:param height: The height of the box.
		:return: Returns the created element.
		"""
		button = QPushButton(text, self)
		button.move(xPos, yPos)
		button.resize(width, height)
		return button

	def showGUI(self):
		"""
		A function to display the GUI.
		"""
		# Show the GUI
		self.show()

	def hideGUI(self):
		"""
		A function to hide the GUI.
		"""
		# Show the GUI
		self.hide()

	def resizeEvent(self, event=None):
		"""
		Resize and move all elements to their new places, and calculate
		their positions based on the new resolution of the GUI window.
		"""
		# Update window size variables
		self.width = self.frameGeometry().width()
		self.height = self.frameGeometry().height()

		# Update each element
		self.editorBox.move(0, 0)
		self.editorBox.resize(self.width / 2, self.height)

		self.editorCompiled.move(self.width / 2, 0)
		self.editorCompiled.resize(self.width / 2, self.height)

#!/usr/bin/env python
# coding: utf-8

# Imports
from random import randint

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QPushButton, QPlainTextEdit, QMainWindow, QAction
from PyQt5.uic.properties import QtWidgets
from keyboard import is_pressed as isKeyPressed
from utility import Utility


# Initialize class
class App(QMainWindow):
	# Pull settings
	settings = Utility.getSettings()

	# Constructor
	def __init__(self):
		super().__init__()

		# Get screen data
		self.screenWidth = Utility.getScreen()[0]
		self.screenHeight = Utility.getScreen()[1]

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
		self.editorBox.move(0, 100)
		self.label = QLabel(self)

		for i in range(12):
			self.label.setText(str(i))
			self.label.show()
			self.label.move(100, 100)

		self.mainMenu = self.makeMenu()
		self.mainMenu.setFont(QFont(self.settings["menuBarFont"], 10))
		self.statusBar = self.makeStatusBar()
		# Call GUI creation
		self.initUI()

		# Display slide
		# Later, if more screens are added, 'slides' are implemented-
		# A slide is basically a function or some algorithm that
		# changes and updates all elements to the latest 'slide'.
		# (A slide being the latest UI interface that needs to be drawn)
		self.showEditor()
		self.resizeEvent()

	def eventFilter(self, obj, event):

		if obj is self.editorBox and event.type() == QEvent.KeyPress:
			#Word count
			self.statusBar.clearMessage()
			text = self.editorBox.toPlainText();
			words = text.split(" ");
			num = len(words)
			print(len(words))
			# label = QLabel(self)
			# label.setText(len(words))
			# label.show()
			# label.move(100, 100)

			#self.statusBar.showMessage("Word count: " + num)
			# Key Binds
			if isKeyPressed("return") and isKeyPressed("shift"):
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
		textBox.setStyleSheet("border: 1px solid rgb(30, 30, 30); background-color: rgb(30, 30, 30); color: white")
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

	def makeMenu(self):
		mainMenu = self.menuBar()
		mainMenu.setStyleSheet("QMenuBar {background-color: rgb(50, 50, 50); color: white; spacing: 3px;} QMenuBar::item:selected { background: #a8a8a8;}")

		fileMenu = mainMenu.addMenu('File')
		newAction = QAction('&New', self)
		newAction.setShortcut('Ctrl+Q')
		openAction = QAction('&Open')
		openAction.setShortcut('Ctrl+O')
		saveAction = QAction('&Save', self)
		saveAction.setShortcut('Ctrl+S')
		saveAsAction = QAction('&Save As', self)
		fileMenu.addAction(newAction)
		fileMenu.addAction(openAction)
		fileMenu.addAction(saveAction)
		fileMenu.addAction(saveAsAction)

		editMenu = mainMenu.addMenu('Edit')
		insertMenu = mainMenu.addMenu('Insert')
		viewMenu = mainMenu.addMenu('View')

		optionsMenu = mainMenu.addMenu('Options')
		settingsAction = QAction('&Settings', self)
		pluginsAction = QAction('&Plugins', self)
		packagesAction = QAction('&Packages', self)
		optionsMenu.addAction(settingsAction)
		optionsMenu.addAction(pluginsAction)
		optionsMenu.addAction(packagesAction)

		toolsMenu = mainMenu.addMenu('Tools')

		helpMenu = mainMenu.addMenu('Help')
		aboutAction = QAction('&About', self)
		updatesAction = QAction('&Check for updates', self)
		helpMenu.addAction(aboutAction)
		helpMenu.addAction(updatesAction)

		return mainMenu

	def makeStatusBar(self):
		statusBar = self.statusBar()
		statusBar.setStyleSheet("QStatusBar {background: rgb(50, 50, 50); color: white}QStatusBar::item {border: 4px solid red; border-radius: 4px; }")
		return statusBar

	def showGUI(self):
		# Show the GUI
		self.show()

	def hideGUI(self):
		# Show the GUI
		self.hide()

	def showEditor(self):
		self.editorBox.show()
		return self.resizeEvent()

	def resizeEvent(self, event=None):
		# Update window size variables
		self.width = self.frameGeometry().width()
		self.height = self.frameGeometry().height()

		# Update each element
		self.editorBox.move(0, self.mainMenu.height())
		self.editorBox.resize(self.width / 2, self.height)

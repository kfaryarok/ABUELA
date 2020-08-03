from random import randint
from threading import Thread
from time import sleep, time

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QPlainTextEdit, QMainWindow, QAction
from keyboard import is_pressed as is_key_pressed

from compile import compileToImage
from project import Project
from utility import Utility


# Initialize class
class App(QMainWindow):
	# Create instance of Utility for later usage
	utils = Utility()

	# Verify that file system is intact
	utils.verifySystem()

	# Pull settings
	settings = utils.getSettings()

	# Clear cache
	utils.clearCache()

	# Load the theme
	theme = utils.loadTheme(settings)

	# Open new project (remove this part and integrate Open File, when the Open File features is ready)
	project = Project("../project/current.tex")

	# Set default compiler live identifier number
	live = 0
	liveUpdate = 0

	# Constructor
	def __init__(self):
		"""
		The initializer / constructor method of the GUI class.
		Here, elements (and other small things for the GUI) are initialized and set.
		"""
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
		# The editor box which code is written in
		self.editorBox = self.makeTextBox()
		self.editorBox.ensureCursorVisible()
		self.editorBox.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.editorBox.setFont(QFont(self.settings["editorFont"], self.settings["editorSize"]))
		self.editorBox.setCursorWidth(self.settings["cursorWidth"])
		self.editorBox.installEventFilter(self)

		# The live-compile renderer element
		self.editorCompiled = self.makePic("../resources/canvas.jpg")

		# MAKE SURE THAT MENU BAR AND STATUS BAR ARE THE LAST 2 ELEMENTS TO BE INITIALIZED
		# If not, the next element to be created will
		# overlap the menu bar / status bar
		# and will cause an unfortunate rendering bug.
		# The menu bar element
		self.menuBarElement = self.menuBar()
		self.menuBarElement.setFixedHeight(self.height / 30)
		self.menuBarElement.setStyleSheet(self.formatStyle())
		self.menuBarElement.setFont(QFont(self.settings["menuBarFont"], self.settings["menuBarSize"]))

		# Create a new menu
		self.subMenu = self.menuBarElement.addMenu("File")

		# Set the submenus and their key binds
		self.makeMenuAction('&New', 'Ctrl+Q')
		self.makeMenuAction('&Open', 'Ctrl+O')
		self.makeMenuAction('&Save', 'Ctrl+S')
		self.makeMenuAction('&Save As', 'Ctrl+Shift+S')

		# Create a new menu
		self.subMenu = self.menuBarElement.addMenu('Edit')
		# Set the submenus and their key binds
		self.makeMenuAction('Insert')
		self.makeMenuAction('View')

		# Create a new menu
		self.subMenu = self.menuBarElement.addMenu('Options')
		# Set the submenus and their key binds
		self.makeMenuAction('&Settings')
		self.makeMenuAction('&Plugins')
		self.makeMenuAction('&Packages')

		# Create a new menu
		self.subMenu = self.menuBarElement.addMenu('Tools')

		# Create a new menu
		self.subMenu = self.menuBarElement.addMenu('Help')
		# Set the submenus and their key binds
		self.makeMenuAction('&About')
		self.makeMenuAction('&Check for updates')

		# The status bar element
		self.statusBar = self.statusBar()
		self.statusBar.setStyleSheet(self.formatStyle())

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
			if is_key_pressed("return") and is_key_pressed("shift"):
				self.editorBox.insertPlainText("\\\\\n")
				return True

			# Compile
			# Set the current live ID and pass it to the function
			liveID = randint(0, 999999999999999)
			self.live = liveID
			# Set the time at which to call the live update
			self.liveUpdate = time() + self.settings["liveUpdate"]

			# Initialize the process
			p = Thread(target=self.updateLive, args=[liveID])
			p.setDaemon(True)
			p.start()
		return super(App, self).eventFilter(obj, event)

	def updateLive(self, liveID):
		"""
		This function is used to compile and update the image
		displaying the live version of the LaTeX source code.

		:param liveID: An ID which is passed just before called. If the global live ID is not equal to this function's
		live ID, then this function will terminate (another key was pressed, therefore this function is old and the
		new function should compile together the new LaTeX source code)

		This function doesn't return any data, it calls directly on the editorCompiled attribute and updates the image.
		"""
		# Wait until it's time to update the live
		while time() < self.liveUpdate:
			if self.live != liveID:
				return
			sleep(self.settings["liveThreadRefresh"])
		# Check if the liveID is this function's ID
		if self.live != liveID:
			return

		# If the ID is equal, then continue.
		# From this point on, the actual compiler will run.
		# That is to say, the above code is only a check
		# that there are not multiple threads attempting
		# to compile at the same time, and that only after
		# a delay will the compiler threads attempt to compile.

		# Update project
		self.project.save(self.editorBox.toPlainText(), overwrite=True)

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

	def makeMenuAction(self, action_name, key_bind="False"):
		"""
		A method to make menu generation more streamlined and sleek.
		Generates an action (menu / submenu) and sets it to a shortcut.
		Sets the action to the most recently created menu tab.

		:param action_name: The name of the submenu (e.g. &New File)
		:param key_bind: The key bind to set the shortcut to (e.g. Ctrl+Shift+N)
		"""
		# Create the action and initialize it with a name (e.g. &Open)
		newAction = QAction(action_name, self)
		if key_bind != "False":
			# Set shortcut method (e.g. Ctrl+O)
			newAction.setShortcut(key_bind)
		# Set the action to the current menu element
		self.subMenu.addAction(newAction)

	def formatStyle(self):
		"""
		A function that takes the currently loaded theme and formats it into QtCSS.

		Returns the QtCSS as a string.
		"""
		return """
		
		QMenuBar {{
			background-color: #{QMenuBarBGColor};
			color: #{QMenuBarColor};
			spacing: {QMenuBarSpacing}px;
		}}

		QMenuBar::item:selected {{
			background: #{QMenuBarItemSelected};
		}}
		
		QStatusBar {{
			background: #{QMenuBarBGColor};
			color: #{QMenuBarColor}
		}}
		
		QStatusBar::item {{
			border: 4px solid red;
			border-radius: 4px;
		}}
		
		""".strip().format(
			QMenuBarBGColor=self.theme["QMenuBar"]["background-color"],
			QMenuBarColor=self.theme["QMenuBar"]["color"],
			QMenuBarSpacing=self.theme["QMenuBar"]["spacing"],
			QMenuBarItemSelected=self.theme["QMenuBar"]["selected"]
		)

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
		self.editorBox.move(0, self.menuBarElement.height())
		self.editorBox.resize(int(self.width / 2), self.height - self.menuBarElement.height() - 2.5 * self.statusBar.height())

		self.editorCompiled.move(int(self.width / 2), self.menuBarElement.height())
		self.editorCompiled.resize(int(self.width / 2), self.height - self.menuBarElement.height() - 2.5 * self.statusBar.height())

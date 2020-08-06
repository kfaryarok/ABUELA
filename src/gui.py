"""
The GUI file, reserved for all interactions
GUI-wise and some others that fit within the
category or are critical / necessary for the GUI to run.
"""

from random import randint
from threading import Thread
from time import sleep, time

from PyQt5 import QtGui
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QLabel, QPlainTextEdit, QMainWindow, QAction
from keyboard import is_pressed as is_key_pressed
from compile import compile_to_image
from menu import Menu, Status
from project import Project
from utility import Utility


# Initialize class
class App(QMainWindow):
	"""
	The App class, for everything-GUI.
	Actually executed by main.py, though.
	"""

	# Create instance of Utility for later usage
	utils = Utility()

	# Verify that file system is intact
	utils.verify_system()

	# Pull settings
	settings = utils.get_settings()

	# Clear cache
	utils.clear_cache()

	# Load the theme
	theme = utils.load_theme(settings)

	# Open new project (remove this part and integrate Open File, when the Open File features is ready)
	project = Project("../project/current.tex")

	# Set default compiler live identifier number
	live = 0
	live_update = 0
	live_compile = "../resources/canvas.jpg"

	# Constructor
	def __init__(self):
		"""
		The initializer / constructor method of the GUI class.
		Here, elements (and other small things for the GUI) are initialized and set.
		"""
		super().__init__()

		# Get screen data
		self.screen_width = self.utils.get_screen()[0]
		self.screen_height = self.utils.get_screen()[1]

		# Set min size
		min_width = int(self.screen_width * self.settings["min_ratio"])
		min_height = int(self.screen_height * self.settings["min_ratio"])
		self.setMinimumSize(min_width, min_height)

		# Set icon
		self.setWindowIcon(QIcon("../resources/logo.jpg"))

		# Title
		self.title = self.settings["window_title"]

		# Screen coordinate initialization
		self.left = self.settings["init_x"]
		self.top = self.settings["init_y"]

		# Calculate gui size
		self.width = int(self.screen_width * self.settings["screen_ratio"])
		self.height = int(self.screen_height * self.settings["screen_ratio"])

		# Create instance of Menu and Status Bar classes
		# Initialize it here rather in the above 'attribute initialization section'
		# because you can't call the Status Bar updating function until
		self.menu_bar_instance = Menu()
		self.status_bar_instance = Status(lambda: self.set_status)

		# Initialize elements
		# Default parameter values are all 0 because self.resizeElements
		# will update the positioning and size of each element regardless
		# The editor box which code is written in
		self.editor_box = self.makeTextBox()
		self.editor_box.ensureCursorVisible()
		self.editor_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.editor_box.setFont(QFont(self.settings["editor_font"], self.settings["editor_size"]))
		self.editor_box.setCursorWidth(self.settings["cursor_width"])
		self.editor_box.installEventFilter(self)

		# The live-compile renderer element
		self.editor_compiled = self.makePic("../resources/canvas.jpg")

		# MAKE SURE THAT MENU BAR AND STATUS BAR ARE THE LAST 2 ELEMENTS TO BE INITIALIZED
		# If not, the next element to be created will
		# overlap the menu bar / status bar
		# and will cause an unfortunate rendering bug.
		# The menu bar element
		self.menu_bar_element = self.menuBar()
		self.menu_bar_element.setFixedHeight(int(self.height / 30))
		self.menu_bar_element.setStyleSheet(self.formatStyle())
		self.menu_bar_element.setFont(QFont(self.settings["menu_bar_font"], self.settings["menu_bar_size"]))

		# Initialize the menu data
		menu_data = {
			"File": [{"name": "&New", "shortcut": 'Ctrl+N'},
			         {"name": "&Open", "shortcut": 'Ctrl+O'},
			         {"name": "&Save As", "shortcut": 'Ctrl+Shift+S'}],
			"Edit": [{"name": "&Insert", "shortcut": 'Ctrl+I'}],
			'Options': [{"name": "&Settings", "shortcut": False},
			            {"name": "&Plugins", "shortcut": False},
			            {"name": "&Packages", "shortcut": False}],
			"Tools": [{"name": "&Copy Live", "shortcut": 'Ctrl+Shift+C',
			           "function": lambda: self.menu_bar_instance.copy_to_clipboard(lambda: self.get_live_compile)}],
			"Help": [{"name": "&About", "shortcut": False},
			         {"name": '&Check for Updates', "shortcut": False}]
		}

		# For each menu bar in the menu_data...
		for menu, data in menu_data.items():
			# Create a new menu
			self.subMenu = self.menu_bar_element.addMenu(menu)
			# For each submenu in the menu bar's data
			for submenu in data:
				# Set the submenus and their key binds
				if "function" in submenu:
					self.make_menu_action(submenu["name"], submenu["shortcut"], submenu["function"])
				else:
					self.make_menu_action(submenu["name"], submenu["shortcut"])

		# The status bar element
		self.status_bar_element = self.statusBar()
		self.status_bar_element.setStyleSheet(self.formatStyle())

		# Call GUI creation
		self.initUI()
		# Set the theme of the whole window
		self.setStyleSheet("""
		background-color: #{QMainWindowBGColor};
		""".strip().format(
			QMainWindowBGColor=self.theme["QMainWindow"]["background-color"]))
		# Resize the elements to the current window size
		self.resizeEvent()
		# Initialize the status bar
		self.status_bar_instance.init_status()

	def event(self, e):
		"""
		PyQt5 Built-in method called when an event occurs.
		This is a function called on by the PyQt5 library during GUI
		interactions, it is not called within this code.
		"""
		if e.type() == QEvent.StatusTip:
			if e.tip() == '':
				e = QtGui.QStatusTipEvent(self.status_bar_instance.status)
		return super().event(e)

	def eventFilter(self, obj, event):
		"""
		The event filter is the function called
		every time an event is generated in the editor_box.
		In most cases, an event is a keystroke.

		This function is utilized for many usages:
		- Key Binds
		- Auto Save
		- Live Compile
		"""
		if obj is self.editor_box and event.type() == QEvent.KeyPress:
			# Key Binds
			# Shift + Return = Add / and newline
			if is_key_pressed("return") and is_key_pressed("shift"):
				self.editor_box.insertPlainText("\\\\\n")
				return True

			# Compile
			# Set the current live ID and pass it to the function
			live_id = randint(0, 999999999999999)
			self.live = live_id
			# Set the time at which to call the live update
			self.live_update = time() + self.settings["live_update"]

			# Initialize the process
			p = Thread(target=self.updateLive, args=[live_id])
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

		This function doesn't return any data, it calls directly on the editor_compiled attribute and updates the image.
		"""
		# Wait until it's time to update the live
		while time() < self.live_update:
			if self.live != liveID:
				return
			sleep(self.settings["live_thread_refresh"])
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
		self.project.save(self.editor_box.toPlainText(), overwrite=True)

		# Update the status bar
		self.status_bar_instance.update_status({
			"Words": len([item for item in self.editor_box.toPlainText().split(" ") if item.strip() != ""]),
			"Characters": len(self.editor_box.toPlainText())
		})

		page_index = 1  # TO DO (ADD SCROLL ELEMENT WHICH ALTERS THIS VALUE & MAKE THIS VALUE AN ATTRIBUTE)
		compiled_return_data = compile_to_image(self.settings["live_quality"])
		if compiled_return_data[0]:
			self.live_compile = "{path}{index}.jpg".format(path=compiled_return_data[0], index=page_index)
			pixel_map = QPixmap(self.live_compile)
			self.editor_compiled.setPixmap(pixel_map)
			self.editor_compiled.setScaledContents(True)
		else:
			# If there is a compilation error... (otherwise, the second
			# item would be returned as false from the compileToImage function)
			if compiled_return_data[1]:
				# Do something with compiled_return_data[1] to display the error message
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

	def get_live_compile(self):
		"""
		Function to return the live_compile attribute.
		"""
		return self.live_compile

	def makeTextBox(self, xPos=0, yPos=0, width=0, height=0):
		"""
		A function to create a new multi line edit box.

		:param xPos: The left-top x position of the box.
		:param yPos: The left-top y position of the box.
		:param width: The width of the box.
		:param height: The height of the box.
		:return: Returns the created element.
		"""
		text_box = QPlainTextEdit(self)
		text_box.setStyleSheet(self.formatStyle())
		text_box.move(xPos, yPos)
		text_box.resize(width, height)
		return text_box

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
		pixel_map = QPixmap(fileName)
		label.setPixmap(pixel_map)
		label.setScaledContents(True)
		label.move(xPos, yPos)
		label.resize(width, height)
		return label

	def make_menu_action(self, action_name, shortcut="False", func=False):
		"""
		A method to make menu generation more streamlined and sleek.
		Generates an action (menu / submenu) and sets it to a shortcut.
		Sets the action to the most recently created menu tab.

		:param func: The function that should be called when the submenu button is clicked.
		:param action_name: The name of the submenu (e.g. &New File)
		:param shortcut: The key bind to set the shortcut to (e.g. Ctrl+Shift+N)
		"""
		# Create the action and initialize it with a name (e.g. &Open)
		new_action = QAction(action_name, self)
		if shortcut != "False":
			# Set shortcut method (e.g. Ctrl+O)
			new_action.setShortcut(shortcut)
		if func:
			# Connect the Action to a function
			new_action.triggered.connect(func)
		# Set the action to the current menu element
		self.subMenu.addAction(new_action)

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
		
		QMenu::item {{
			background-color: #{QMenuBarItemBGColor};
			color: #{QMenuBarItemColor};
			padding: {QMenuBarPadding}px;
		}}
		
		QMenu::item:selected {{
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
		
		QPlainTextEdit {{
			background-color: #{QPlainTextEditBGColor};
			border: 1px solid #{QPlainTextEditBorderColor};
			color: #{QPlainTextEditColor};
		}}
		
		""".strip().format(
			QMenuBarBGColor=self.theme["QMenuBar"]["background-color"],
			QMenuBarColor=self.theme["QMenuBar"]["color"],
			QMenuBarSpacing=self.theme["QMenuBar"]["spacing"],
			QMenuBarItemSelected=self.theme["QMenuBarItem"]["selected"],
			QMenuBarItemBGColor=self.theme["QMenuBarItem"]["background-color"],
			QMenuBarItemColor=self.theme["QMenuBarItem"]["color"],
			QMenuBarPadding=self.theme["QMenuBarItem"]["padding"],
			QPlainTextEditBGColor=self.theme["QPlainTextEdit"]["background-color"],
			QPlainTextEditBorderColor=self.theme["QPlainTextEdit"]["border"],
			QPlainTextEditColor=self.theme["QPlainTextEdit"]["color"]
		)

	def set_status(self, new_status):
		"""
		Method to update the Status bar to the inputted text.

		:param new_status: The new status to update to.
		"""
		self.status = new_status
		self.status_bar_element.showMessage(self.status)

	def showGUI(self):
		"""
		A function to display the GUI.
		"""
		# Show the GUI
		self.show()

	def resizeEvent(self, event=None):
		"""
		Resize and move all elements to their new places, and calculate
		their positions based on the new resolution of the GUI window.
		"""
		# Update window size variables
		self.width = self.frameGeometry().width()
		self.height = self.frameGeometry().height()

		# Update each element based on the live_fill setting
		if self.utils.stringify(self.settings["live_fill"]) in ["fill", "stretch"]:
			# Move the edit box
			self.editor_box.move(0, self.menu_bar_element.height())
			# Resize the edit box
			self.editor_box.resize(int(self.width / 2),
			                       self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height())
			# Move the live-render
			self.editor_compiled.move(int(self.width / 2), self.menu_bar_element.height())
			# Resize the live-render
			self.editor_compiled.resize(int(self.width / 2),
			                            self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height())

		elif self.utils.stringify(self.settings["live_fill"]) in ["split", "center"]:
			# Move the edit box
			self.editor_box.move(0, self.menu_bar_element.height())
			# Resize the edit box
			self.editor_box.resize(int(self.width / 2),
			                       self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height())
			# Move the live-render
			self.editor_compiled.move(int((self.width / 2) + (((self.width / 2) - (
					self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()) / (
					                                                   2 ** 0.5)) / 2)),
			                          self.menu_bar_element.height())
			# Resize the live-render
			self.editor_compiled.resize(
				int((self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()) / (
							2 ** 0.5)),
				self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height())

		else:
			# Move the edit box
			self.editor_box.move(0, self.menu_bar_element.height())
			# Resize the edit box
			self.editor_box.resize(int(
				self.width - (self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()) / (
						2 ** 0.5)),
				self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height())
			# Move the live-render
			self.editor_compiled.move(int(
				self.width - (self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()) / (
						2 ** 0.5)),
				self.menu_bar_element.height())
			# Resize the live-render
			self.editor_compiled.resize(
				int((self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()) / (
							2 ** 0.5)),
				self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height())

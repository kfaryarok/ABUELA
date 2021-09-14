"""
The GUI file, reserved for all interactions
GUI-wise and some others that fit within the
category or are critical / necessary for the GUI to run.
"""
from os import listdir
from random import randint
from threading import Thread
from time import sleep, time

from PyQt5 import QtGui
from PyQt5.QtCore import QEvent, Qt, QCoreApplication, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont, QTextCursor, QTextBlockFormat, QColor
from PyQt5.QtWidgets import QLabel, QPlainTextEdit, QMainWindow, QListWidget, QListWidgetItem, QGroupBox, QSpinBox
from keyboard import is_pressed as is_key_pressed

from compile import compile_to_image
from error import Error
from menu import Menu, Status
from project import Project
from updater import Updater
from utility import Utility


# Initialize class
# noinspection PyCompatibility,PyAttributeOutsideInit
class App(QMainWindow):
	"""
	The App class, for everything-GUI.
	Executed by the main.py file.
	"""

	# Constructor
	def __init__(self):
		"""
		The initializer / constructor method of the GUI class.
		Here, elements (and other small things for the GUI) are initialized and set.
		"""
		super().__init__()

		# Initialize exit codes (These are arbitrary values with no hidden meaning)
		self.restart_code = -54321

		# Create instance of Error class
		self.error_instance = Error()

		# Create instance of Utility for later usage
		self.utils = Utility(self)

		# Verify that file system is intact
		self.utils.verify_system()

		# Pull settings
		self.settings = self.utils.get_settings()

		# Clear cache
		self.utils.clear_cache()

		# Load the theme
		self.theme = self.utils.load_theme(self.settings)

		# Open new project (remove this part and integrate Open File, when the Open File features is ready)
		self.project = Project("../project/current.tex")
		self.project.new()
		self.projects = [self.project]
		self.projects_index = int()

		# Create an instance of the Updater class
		self.updater_instance = Updater()

		# Set default compiler live identifier number
		self.live = int()
		self.live_update = int()
		self.live_compile = str()

		# Other attributes
		self.last_data = str()
		self.last_update = time()
		self.status = str()
		self.settings_opened = False

		# Get screen data
		self.screen_width = self.utils.get_screen()[0]
		self.screen_height = self.utils.get_screen()[1]

		# Set min_spin size
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

		# Initialize elements
		# Default parameter values are all 0 because self.resizeElements
		# will update the positioning and size of each element regardless
		# The editor box which code is written in
		self.editor_box = self.make_text_box()
		self.editor_box.ensureCursorVisible()
		self.editor_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.editor_box.setFont(QFont(self.settings["editor_font"], self.settings["editor_size"]))
		self.editor_box.setCursorWidth(self.settings["cursor_width"])
		self.editor_box.installEventFilter(self)

		# The live-compile renderer element
		self.editor_compiled = self.make_pic(background=self.theme["Live"]["background-color"])

		# Create Settings list element
		self.settings_list = self.make_list(["Appearance", "Shortcuts", "Advanced"])
		self.settings_list.setFont(
			QFont(
				self.settings["menu_font"],
				self.width ** 0.5 * 0.5
			)
		)

		# Create groups for elements
		self.theme_group = QGroupBox(self)
		self.editor_group = QGroupBox(self)
		self.menu_group = QGroupBox(self)

		# Rename the group titles
		self.theme_group.setTitle("Theme")
		self.editor_group.setTitle("Editor")
		self.menu_group.setTitle("Menu")

		# For each theme file in the themes folder...
		theme_list = list()
		for file in listdir("../gui_themes"):
			if file.endswith(".yaml"):
				# Append it to the theme list
				theme_list.append(file[:-5])

		# Create the list widget with the themes
		self.theme_select_element = self.make_list(
			items=theme_list,
			parent=self.theme_group
		)

		# Specify the valid fonts
		font_list = ["Consolas", "Arial", "Comic Sans"]

		# Create the font selection elements
		self.font_select_element = self.make_list(
			items=font_list,
			parent=self.editor_group
		)

		self.menu_font_select_element = self.make_list(
			items=font_list,
			parent=self.editor_group
		)

		# Create the spinbox elements
		self.font_size_element = self.make_spinbox(
			min_spin=8,
			max_spin=22,
			step=2,
			parent=self.editor_group
		)

		self.cursor_size_element = self.make_spinbox(
			min_spin=1,
			max_spin=10,
			parent=self.editor_group
		)

		# Create the text elements
		self.font_size_label_element = self.make_text(
			text="Font Size",
			parent=self.editor_group
		)

		self.cursor_size_label_element = self.make_text(
			text="Cursor Size",
			parent=self.editor_group
		)

		self.editor_font_element = self.make_text(
			text="Editor Font",
			parent=self.editor_group
		)

		# Create the spinbox elements
		self.menu_bar_size_select_element = self.make_spinbox(
			min_spin=6,
			max_spin=14,
			parent=self.menu_group
		)

		self.status_bar_size_select_element = self.make_spinbox(
			min_spin=6,
			max_spin=14,
			parent=self.menu_group
		)

		self.status_bar_margin_select_element = self.make_spinbox(
			min_spin=1,
			max_spin=20,
			parent=self.menu_group
		)

		self.status_bar_spacing_select_element = self.make_spinbox(
			min_spin=1,
			max_spin=10,
			parent=self.menu_group
		)

		# Create the text elements
		self.menu_bar_size_element = self.make_text(
			text="Menu Bar Size",
			parent=self.menu_group
		)

		self.status_bar_size_element = self.make_text(
			text="Status Bar Size",
			parent=self.menu_group
		)

		self.menu_font_element = self.make_text(
			text="Menu Font",
			parent=self.menu_group
		)

		self.status_bar_margin_element = self.make_text(
			text="Status Bar Margin",
			parent=self.menu_group
		)

		self.status_bar_spacing_element = self.make_text(
			text="Status Bar Spacing",
			parent=self.menu_group
		)

		# Force disable scrolling
		self.theme_select_element.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.theme_select_element.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.font_select_element.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.font_select_element.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.menu_font_select_element.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.menu_font_select_element.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		# Set the order of how tabs jump through elements
		self.set_tab_order([
			self.theme_select_element,
			self.menu_font_select_element,
			self.menu_bar_size_select_element,
			self.status_bar_size_select_element,
			self.status_bar_margin_select_element,
			self.status_bar_spacing_select_element,
			self.font_select_element,
			self.font_size_element,
			self.cursor_size_element
		])

		# Create instance of Menu and Status Bar classes
		# Initialize it here rather in the above 'attribute initialization section'
		# because you can't call the Status Bar updating function until
		self.menu_bar_instance = Menu(self)
		self.status_bar_instance = Status(self)

		# MAKE SURE THAT MENU BAR AND STATUS BAR ARE THE LAST 2 ELEMENTS TO BE INITIALIZED
		# If not, the next element to be created will overlap the menu bar &
		# status bar and will cause an unfortunate rendering bug.
		# Initialize the menu bar
		self.menu_bar_instance.init()
		# Initialize the status bar
		self.status_bar_instance.init()
		# Initialize the status bar data
		self.status_bar_instance.init_status()

		# Set Project focus to current project
		self.switch_project()

		# Set a timer to constantly check for new edits
		self.update_timer = QTimer(self)
		self.update_timer.setInterval(self.settings["live_await"] * 1000)
		self.update_timer.timeout.connect(self.check_data_update)
		self.update_timer.start()

		# Default to Editor slide being displayed
		# Call this so that all non-editor elements are hidden
		self.show_editor()

		# Call GUI creation
		self.initUI()

		# Set the theme of the whole window
		self.setStyleSheet("background-color: {QMainWindowBGColor};".strip().format(
			QMainWindowBGColor=self.utils.hex_format(self.theme["GUI"]["QMainWindow"]["background-color"])
		))

		# Resize the elements to the current window size
		self.resizeEvent()

	# noinspection PyCompatibility
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
		"""
		if obj is self.editor_box and event.type() == QEvent.KeyPress:
			# Key Binds
			self.status_bar_instance.update_status({"Task": "Parsing binds..."})

			# Shift + Return = Add / and newline
			if is_key_pressed("return") and is_key_pressed("shift"):
				self.editor_box.insertPlainText("\\\\\n")
				return True

			self.status_bar_instance.update_status({"Task": "Idling"})
		return super(App, self).eventFilter(obj, event)

	def check_data_update(self):
		"""
		A function to check if the text from the editor
		box was updated. This function should be utilized
		by pairing it with a timer to constantly ping it.
		"""
		# Try finding a way to debunk the thread,
		# as to improve memory space and compiling
		# efficiency and speed.

		# If the text was updated...
		if self.last_data != self.editor_box.toPlainText():
			# Update the marker for the last data
			self.last_data = self.editor_box.toPlainText()

			# If there are characters in the window...
			if self.editor_box.toPlainText().strip():
				# If the code can't be 'debunked' and is ready
				# to compile, then call the compiler function.
				self.thread_compile()
			else:
				# If there are no characters, make sure there is no picture
				self.editor_compiled.setPixmap(QPixmap())

			self.status_bar_instance.update_status({"Task": "Idling"})

	def thread_compile(self):
		"""
		The method which starts a compiler thread.
		Written as a method as to be called easier.
		"""
		# Generate a random ID and pass it as a parameter to
		# the compiler thread. Set the ID as an attribute so that
		# the compiler thread can also access it. If the compiler thread
		# notices that its ID is not matching to the attribute ID,
		# then that means that the compiler thread is invalid,
		# and that a new thread is the latest thread which should run.

		# Update last edit time
		self.last_update = time()

		# Set the current live ID and pass it to the function
		live_id = randint(0, 999999999999999)
		self.live = live_id

		# Set the time at which to call the live update
		self.live_update = time() + self.settings["live_update"]

		# Initialize the process
		self.status_bar_instance.update_status({"Task": "Multiprocessing..."})
		p = Thread(target=self.updateLive, args=[live_id])
		p.setDaemon(True)
		p.start()

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
		self.status_bar_instance.update_status({"Task": "Saving..."})
		self.project.save(self.editor_box.toPlainText(), overwrite=True)

		# Update the status bar
		self.status_bar_instance.update_status({
			"Words": len([item for item in self.editor_box.toPlainText().split(" ") if item.strip()]),
			"Characters": len(self.editor_box.toPlainText())
		})

		# Compile the code to an image
		self.status_bar_instance.update_status({"Task": "Compiling..."})
		page_index = 1  # TO DO (ADD SCROLL ELEMENT WHICH ALTERS THIS VALUE & MAKE THIS VALUE AN ATTRIBUTE)
		compiled_return_data = compile_to_image(
			app_pointer=self,
			path=self.project.file_name,
			quality=self.settings["live_quality"]
		)
		# If the file was successfully compiled...
		if compiled_return_data[0]:
			# Update the live image element
			self.status_bar_instance.update_status({"Task": "Updating..."})
			self.live_compile = "{path}{index}.jpg".format(path=compiled_return_data[0], index=page_index)
			pixel_map = QPixmap(self.live_compile)
			self.editor_compiled.setPixmap(pixel_map)
			self.editor_compiled.setScaledContents(True)

			# Clear the error coloring
			self.status_bar_instance.update_status({"Task": "Clearing..."})
			# Get the cursor element and its position
			cursor_pos = self.editor_box.textCursor().position()
			# Reset the window by overwriting all text with itself
			self.editor_box.setPlainText(self.editor_box.toPlainText())
			# Set the block position again
			cursor = self.editor_box.textCursor()
			cursor.setPosition(cursor_pos)
			self.editor_box.setTextCursor(cursor)
		# Otherwise, if there was a compilation error,
		else:
			# If there is a compilation error... (otherwise, the second
			# item would be returned as false from the compileToImage function)
			if compiled_return_data[1]:
				# compiled_return_data[1] now holds the error message as a string
				# Make a formatter object which colors the background
				self.status_bar_instance.update_status({"Task": "Parsing..."})
				color_format = QTextBlockFormat()
				error_color = self.utils.hex_to_rgb(self.utils.hex_format(self.theme["Editor"]["error"]))
				color_format.setBackground(QColor(error_color[0], error_color[1], error_color[2]))
				# For each line which has an error...
				for line, message in self.utils.parse_errors(compiled_return_data[1]).items():
					# Set a cursor to the line number
					cursor = QTextCursor(self.editor_box.document().findBlockByNumber(line - 1))
					# Update the background color
					cursor.setBlockFormat(color_format)
		self.status_bar_instance.update_status({
			"Compile Time": round(time() - self.last_update, 2),
			"Task": "Idling"
		})

	def initUI(self):
		"""
		A function which sets the basics of the window- title, size, and displaying it.
		"""
		# Set the title
		self.setWindowTitle(self.title)
		# Set the GUI size
		self.setGeometry(self.left, self.top, self.width, self.height)
		# Show the GUI
		self.show()

	def show_editor(self):
		"""
		Launches the Editor GUI, and hides the Settings GUI.
		"""
		# Update the attribute
		self.settings_opened = False

		# Hide all existing elements
		self.settings_list.hide()
		self.editor_group.hide()
		self.menu_group.hide()
		self.theme_group.hide()

		# Show Editor elements
		self.menu_bar_instance.show()
		self.status_bar_instance.show()
		self.editor_box.show()
		self.editor_compiled.show()

		# Repaint elements
		self.resizeEvent()

	def show_settings(self):
		"""
		Launches the Settings GUI, and hides the Editor GUI.
		"""
		# Update the attribute
		self.settings_opened = True

		# Hide all existing elements
		self.menu_bar_instance.hide()
		self.status_bar_instance.hide()
		self.editor_box.hide()
		self.editor_compiled.hide()

		# Reveal Settings elements
		self.settings_list.show()
		self.settings_list.currentRowChanged['int'].connect(self.change_settings_slide)

		# Repaint elements
		self.resizeEvent()

	def hide_all_settings(self):
		"""
		Hides all settings elements
		"""
		self.editor_group.hide()
		self.menu_group.hide()
		self.theme_group.hide()

	def change_settings_slide(self):
		"""
		Updates the slide of elements in the Settings
		GUI to the currently selected list item.
		"""
		current_row = self.settings_list.currentRow()
		self.hide_all_settings()
		# Appearance
		if current_row == 0:
			self.editor_group.show()
			self.menu_group.show()
			self.theme_group.show()

	def close_project(self):
		"""
		Closes the the currently opened Project file.
		"""
		# If there are no other files left...
		if len(self.projects) == 1:
			# Then reload (recreate the current.tex file)
			self.restart_app()
			return
		# Otherwise...
		if len(self.projects) > self.projects_index + 1:
			# Go to the above index (if there is one)
			# Kill the current Project (by index)
			self.projects.pop(self.projects_index)
			# The Project at this index now will be the one above ours
			self.switch_project(self.projects_index)
			return
		# Otherwise, there must be a Project in the index below us, so go to it
		else:
			# Kill the current Project (by index)
			self.projects.pop(self.projects_index)
			# Go to the Project in the index below ours
			self.switch_project(self.projects_index - 1)
			return

	def switch_project(self, new_project_index=0):
		"""
		Changes the editor to focus on the new selected Project class.

		:param new_project_index: The index of self.projects to focus on.
		"""
		# Set the current project to the new index
		self.status_bar_instance.update_status({"Task": "Opening..."})
		self.projects_index = new_project_index
		self.project = self.projects[self.projects_index]

		# Unload all other projects to save memory
		for i in range(len(self.projects)):
			if i != self.projects_index:
				self.projects[i].unload()

		# Open it in the editor box
		self.editor_box.setPlainText(self.project.open())

		# Update the status bar to the current project
		self.status_bar_instance.update_status({"Project": self.project.name})

		# Update the menu data (Specifically, the Projects menu)
		self.status_bar_instance.update_status({"Task": "Updating menu..."})
		self.menu_bar_instance.set({
			"File": [{"name": "New", "bind": 'Ctrl+N'},
			         {"name": "Open", "bind": 'Ctrl+O', "func": self.utils.open_file},
			         {"name": "Save As", "bind": 'Ctrl+Shift+S', "func": self.utils.save_file},
			         {"name": "Close", "bind": 'Ctrl+W', "func": self.close_project},
			         {"name": "Reload", "bind": False, "func": self.restart_app},
			         {"name": "Exit", "bind": False, "func": self.exit_app}],
			"Edit": [{"name": "Insert", "bind": 'Ctrl+I'}],
			'Options': [{"name": "Settings", "bind": False},
			            {"name": "Plugins", "bind": False},
			            {"name": "Packages", "bind": False}],
			"View": [{"name": "Fit", "bind": False,
			          "func": lambda: self.update_fill("fit")},
			         {"name": "Fill", "bind": False,
			          "func": lambda: self.update_fill("fill")},
			         {"name": "Split", "bind": False,
			          "func": lambda: self.update_fill("split")}],
			"Tools": [{"name": "Copy Live", "bind": 'Ctrl+Shift+C',
			           "func": lambda: self.menu_bar_instance.copy_to_clipboard(self.live_compile)}],
			"Projects": [{"name": self.projects[i].name, "bind": False,
			              "func": lambda state, x=i: self.switch_project(x)} for i in range(len(self.projects))],
			"Help": [{"name": "About", "bind": False, "func": lambda: self.error_instance.dialogue(
				"../resources/logo.ico",
				"About",
				"<b><i>ABUELA</i></b>",
				"""<i>A Beautiful, Useful, & Elegant LaTeX Application.</i><br><br>
				
				Founded with love by @Xiddoc, @AvivHavivyan, & @RootAtKali.<br><br>
				
				Links:<br>
				• <a href="{base_url}">Github Repo</a><br>
				• <a href="{base_url}/blob/master/README.md">Documentation</a><br>
				• <a href="{base_url}/blob/master/LICENSE">License</a>""".format(
					base_url=self.updater_instance.get_url()
				))},
			         {"name": "Settings", "bind": False, "func": self.show_settings},
			         {"name": "Reset Settings", "bind": False, "func": self.utils.reset_system},
			         {"name": 'Check for Updates', "bind": False}]
		})

		self.status_bar_instance.update_status({"Task": "Idling"})

	def make_spinbox(self, min_spin=0, max_spin=0, step=1, xPos=0, yPos=0, width=0, height=0, parent=False):
		"""
		A method to create a list of items, one of which can be selected at a time.

		:param step: The step / change that the box will spin by.
		:param max_spin: The maximum value the box can spin to.
		:param min_spin: The minimum value the box can spin to.
		:param parent: The parent widget that the element should be placed into.
		:param xPos: The left-top x position of the element.
		:param yPos: The left-top y position of the element.
		:param width: The width of the element.
		:param height: The height of the element.
		:return: Returns the created element.
		"""
		# If there is a parent element, then set it to it
		if parent:
			spin_widget = QSpinBox(parent)
		# Otherwise, parent the list widget to the main window
		else:
			spin_widget = QSpinBox(self)
		# Set the stylesheet
		spin_widget.setStyleSheet(self.formatStyle())
		# Move the element
		spin_widget.move(xPos, yPos)
		# Resize it
		spin_widget.resize(width, height)
		# Update element data
		spin_widget.setMinimum(min_spin)
		spin_widget.setMaximum(max_spin)
		spin_widget.setSingleStep(step)
		# Return the element
		return spin_widget

	def make_text(self, text: str, xPos=0, yPos=0, width=0, height=0, parent=False) -> QLabel:
		"""
		A function to create a new multi line edit box.

		:param text: The text that should be displayed in the text label.
		:param parent: The parent widget that the element should be placed into.
		:param xPos: The left-top x position of the box.
		:param yPos: The left-top y position of the box.
		:param width: The width of the box.
		:param height: The height of the box.
		:return: Returns the created element.
		"""
		# If there is a parent element, then set it to it
		if parent:
			text_label = QLabel(parent)
		# Otherwise, parent the list widget to the main window
		else:
			text_label = QLabel(self)
		text_label.setText(text)
		text_label.setStyleSheet(self.formatStyle())
		text_label.move(xPos, yPos)
		text_label.resize(width, height)
		return text_label

	def make_list(self, items: list, xPos=0, yPos=0, width=0, height=0, parent=False):
		"""
		A method to create a list of items, one of which can be selected at a time.

		:param parent: The parent widget that the element should be placed into.
		:param items: A list of the names of the items.
		:param xPos: The left-top x position of the element.
		:param yPos: The left-top y position of the element.
		:param width: The width of the element.
		:param height: The height of the element.
		:return: Returns the created element.
		"""
		# If there is a parent element, then set it to it
		if parent:
			list_widget = QListWidget(parent)
		# Otherwise, parent the list widget to the main window
		else:
			list_widget = QListWidget(self)
		# Set the stylesheet
		list_widget.setStyleSheet(self.formatStyle())
		# Move the element
		list_widget.move(xPos, yPos)
		# Resize it
		list_widget.resize(width, height)
		# For each item in the items list
		for item in items:
			# Create an item widget for it and add it to the list widget
			current_item = QListWidgetItem()
			current_item.setText(item)
			list_widget.addItem(current_item)
		# Return the element
		return list_widget

	def make_text_box(self, xPos=0, yPos=0, width=0, height=0):
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

	def make_pic(self, file_name: str = False, background: str = False, x_pos=0, y_pos=0, width=0, height=0):
		"""
		A function to create a new picture element.

		:param background: The default background color of the picture element. Defaults to no background.
		:param file_name: The path to the file to display.
		:param x_pos: The left-top x position of the box.
		:param y_pos: The left-top y position of the box.
		:param width: The width of the box.
		:param height: The height of the box.
		:return: Returns the created element.
		"""
		label = QLabel(self)
		if file_name:
			pixel_map = QPixmap(file_name)
			label.setPixmap(pixel_map)
		if background:
			label.setStyleSheet(
				"background-color: {bgColor};".format(
					bgColor=self.utils.hex_format(background)
				)
			)
		label.setScaledContents(True)
		label.move(x_pos, y_pos)
		label.resize(width, height)
		return label

	def formatStyle(self):
		"""
		A function that takes the currently loaded theme and formats it into QtCSS.

		Returns the QtCSS as a string.
		"""
		# Initialize the string
		formatted_string = str()
		# For each element in the GUI data
		for element, data in self.theme["GUI"].items():
			# Split the identifiers
			split_element = element.split("-")
			# Add the base element
			formatted_string += split_element[0]
			# If there is a selector (e.g., item)
			if len(split_element) > 1:
				formatted_string += "::{selector}".format(
					selector=split_element[1]
				)
			# If there is a case selector (e.g., selected)
			if len(split_element) > 2:
				formatted_string += ":{case_selector}".format(
					case_selector=split_element[2]
				)

			# Start the element's data segment
			formatted_string += " {\n"
			# Loop over each attribute
			for attrib, value in data.items():
				# Format the attribute and its data
				formatted_string += "\t{attrib}: {value};\n".format(
					attrib=attrib,
					# If the value is a hex code, then update
					# it to the conventional hex code
					value=self.utils.hex_format(value)
				)
			# End the element's data segment
			formatted_string += "}\n\n"

		return formatted_string

	def update_fill(self, new_fill_type):
		"""
		Updates the fill type of the screen, used in the menu bar.

		:param new_fill_type: The new fill type to update to.
		"""
		self.settings["live_fill"] = new_fill_type
		self.resizeEvent()

	def resizeEvent(self, event=None):
		"""
		Resize and move all elements to their new places, and calculate
		their positions based on the new resolution of the GUI window.
		"""
		# Update window size variables
		self.width = self.frameGeometry().width()
		self.height = self.frameGeometry().height()

		# Only update relevant elements to improve efficiency
		# Settings elements
		if self.settings_opened:
			# Calculate margin values
			margin_w = int(self.width * 10 / 600)

			# Settings list sidebar
			self.settings_list.move(
				0,
				0
			)
			self.settings_list.resize(
				int(
					self.width * 0.3
				),
				self.height
			)

			# Appearance settings elements
			self.theme_group.move(
				int(
					self.width * 0.3 + margin_w
				),
				int(
					self.height * 10 / 600
				)
			)
			self.theme_group.resize(
				int(
					self.width * 0.7 - margin_w * 2
				),
				int(
					self.height * 110 / 600
				)
			)

			self.menu_group.move(
				int(
					self.width * 0.3 + margin_w
				),
				int(
					self.height * 130 / 600
				)
			)
			self.menu_group.resize(
				int(
					self.width * 0.7 - margin_w * 2
				),
				int(
					self.height * 270 / 600
				)
			)

			self.editor_group.move(
				int(
					self.width * 0.3 + margin_w
				),
				int(
					self.height * 410 / 600
				)
			)
			self.editor_group.resize(
				int(
					self.width * 0.7 - margin_w * 2
				),
				int(
					self.height * 150 / 600
				)
			)

			# Grouped elements
			self.theme_select_element.move(
				int(
					self.width * 0.3 + margin_w
				),
			)
			#
			# # Create the font selection elements
			# self.font_select_element = self.make_list(
			# 	items=font_list,
			# 	parent=self.editor_group
			# )
			#
			# self.menu_font_select_element = self.make_list(
			# 	items=font_list,
			# 	parent=self.editor_group
			# )
			#
			# # Create the spinbox elements
			# self.font_size_element = self.make_spinbox(
			# 	min_spin=8,
			# 	max_spin=22,
			# 	step=2,
			# 	parent=self.editor_group
			# )
			#
			# self.cursor_size_element = self.make_spinbox(
			# 	min_spin=1,
			# 	max_spin=10,
			# 	parent=self.editor_group
			# )
			#
			# # Create the text elements
			# self.font_size_label_element = self.make_text(
			# 	text="Font Size",
			# 	parent=self.editor_group
			# )
			#
			# self.cursor_size_label_element = self.make_text(
			# 	text="Cursor Size",
			# 	parent=self.editor_group
			# )
			#
			# self.editor_font_element = self.make_text(
			# 	text="Editor Font",
			# 	parent=self.editor_group
			# )
			#
			# # Create the spinbox elements
			# self.menu_bar_size_select_element = self.make_spinbox(
			# 	min_spin=6,
			# 	max_spin=14,
			# 	parent=self.menu_group
			# )
			#
			# self.status_bar_size_select_element = self.make_spinbox(
			# 	min_spin=6,
			# 	max_spin=14,
			# 	parent=self.menu_group
			# )
			#
			# self.status_bar_margin_select_element = self.make_spinbox(
			# 	min_spin=1,
			# 	max_spin=20,
			# 	parent=self.menu_group
			# )
			#
			# self.status_bar_spacing_select_element = self.make_spinbox(
			# 	min_spin=1,
			# 	max_spin=10,
			# 	parent=self.menu_group
			# )
			#
			# # Create the text elements
			# self.menu_bar_size_element = self.make_text(
			# 	text="Menu Bar Size",
			# 	parent=self.menu_group
			# )
			#
			# self.status_bar_size_element = self.make_text(
			# 	text="Status Bar Size",
			# 	parent=self.menu_group
			# )
			#
			# self.menu_font_element = self.make_text(
			# 	text="Menu Font",
			# 	parent=self.menu_group
			# )
			#
			# self.status_bar_margin_element = self.make_text(
			# 	text="Status Bar Margin",
			# 	parent=self.menu_group
			# )
			#
			# self.status_bar_spacing_element = self.make_text(
			# 	text="Status Bar Spacing",
			# 	parent=self.menu_group
			# )


		# Editor elements
		else:
			# Update each element based on the live_fill setting
			if self.utils.stringify(self.settings["live_fill"]) in ["fill", "stretch"]:
				# Move the edit box
				self.editor_box.move(
					0,
					self.menu_bar_element.height()
				)
				# Resize the edit box
				self.editor_box.resize(
					int(self.width / 2),
					self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()
				)
				# Move the live-render
				self.editor_compiled.move(
					int(self.width / 2),
					self.menu_bar_element.height()
				)
				# Resize the live-render
				self.editor_compiled.resize(
					int(self.width / 2),
					self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()
				)

			elif self.utils.stringify(self.settings["live_fill"]) in ["split", "center"]:
				# Move the edit box
				self.editor_box.move(
					0,
					self.menu_bar_element.height()
				)
				# Resize the edit box
				self.editor_box.resize(
					int(self.width / 2),
					self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()
				)
				# Move the live-render
				self.editor_compiled.move(
					int(
						(self.width / 2) +
						(((self.width / 2) -
						  (self.height - self.menu_bar_element.height() -
						   2.5 * self.status_bar_element.height()) / (2 ** 0.5)) / 2)
					),
					self.menu_bar_element.height()
				)
				# Resize the live-render
				self.editor_compiled.resize(
					int((
							  self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()
					      ) / (
							  2 ** 0.5
					      )),
					self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()
				)

			else:
				# Move the edit box
				self.editor_box.move(
					0,
					self.menu_bar_element.height()
				)
				# Resize the edit box
				self.editor_box.resize(
					int(
						self.width -
						(
							self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()
						) / (
							2 ** 0.5
						)
					),
					self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()
				)
				# Move the live-render
				self.editor_compiled.move(
					int(
						self.width - (
							self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()
						) / (
							2 ** 0.5
						)
					),
					self.menu_bar_element.height())
				# Resize the live-render
				self.editor_compiled.resize(
					int(
						(
							self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()
						) / (
							2 ** 0.5
						)
					),
					self.height - self.menu_bar_element.height() - 2.5 * self.status_bar_element.height()
				)

	def set_tab_order(self, *tab_order):
		"""
		A method to set the order of how pressing the
		'TAB' key affects the selected elements.

		:param tab_order: A list of the elements, the list order is the order that the tab key will pass by.
		"""
		# For each index in the tab list (starting from the index 1)
		for i in range(1, len(tab_order)):
			# Connect the previous tab to the current tab
			self.setTabOrder(tab_order[i - 1], tab_order[i])

	def restart_app(self):
		"""
		Restarts the application.
		The actual method only terminates, however
		the termination code is synchronized with
		main.py so that it will reopen after termination.
		"""
		QCoreApplication.exit(self.restart_code)

	@staticmethod
	def exit_app():
		"""
		Exits the application with no restart.
		"""
		QCoreApplication.exit()

"""
The Menu file.
Used to store the Status and Menu
classes, and other such objects
which are useful for the menu and status bars.
"""
from io import BytesIO

from PIL import Image
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QAction
from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardData, CloseClipboard, CF_DIB

from error import CatchError


class Status:
	"""
	Class to assist in the few functions and methods
	that are needed for the Status Bar to operate.
	"""

	def __init__(self, app_pointer):
		self.app_pointer = app_pointer
		self.padding = self.app_pointer.settings["status_padding"]
		self.spacing = self.app_pointer.settings["status_spacing"]
		self.status_dict = dict()
		self.status = str()

	def init_status(self):
		"""
		Initializes the status bar with default 0 amounts.
		This is optimal and is better than not displaying
		anything when the GUI is initialized.
		"""
		self.update_status({
			"Project": str(),
			"Words": int(),
			"Characters": int(),
			"Task": "Idling"
		})

	def refresh_status(self):
		"""
		Refreshes the status (does not change any of the data).
		Used in case the Status Bar disappears for whatever reason,
		or glitches / bugs out, and other reasons
		to force-paint the Status Bar again.
		"""
		self.set_status(self.status_dict)

	@CatchError
	def update_status(self, status_update):
		"""
		Updates an element (or multiple elements at
		the same time) from the Status Bar.

		:param status_update: A dictionary containing the Status Bar
								elements to update, and their new values.
		"""
		self.set_status({**self.status_dict, **status_update})

	@CatchError
	def set_status(self, status_dict: dict):
		"""
		Calls on the Status Bar updater function
		in order to repaint the text on the Status Bar.

		:param status_dict: A dictionary containing all the data to set the Status Bar to.
		"""
		# Initialize all statuses
		statuses = list()
		# For each status, create it's sector
		for status, data in status_dict.items():
			statuses.append("{status}:{spacing}{data}".format(
				status=status,
				spacing=self.spacing * " ",
				data=data
			))
		self.status_dict = status_dict
		self.status = self.padding * " " + str(self.padding * " " + "|" + self.padding * " ").join(statuses)
		self.app_pointer.status = self.status
		self.app_pointer.status_bar_element.showMessage(self.app_pointer.status)


class Menu:
	"""
	Class to assist with managing the functions,
	uses, and tools that the Menu Bar has to offer.
	"""

	def __init__(self, app_pointer):
		self.app_pointer = app_pointer
		self.sub_menu = False

	def init(self):
		"""
		Initializes the Menu bar element.
		"""
		self.app_pointer.menu_bar_element = self.app_pointer.menuBar()
		self.app_pointer.menu_bar_element.setFixedHeight(int(self.app_pointer.height / 30))
		self.app_pointer.menu_bar_element.setStyleSheet(self.app_pointer.formatStyle())
		self.app_pointer.menu_bar_element.setFont(
			QFont(self.app_pointer.settings["menu_bar_font"], self.app_pointer.settings["menu_bar_size"]))

	def clear(self):
		"""
		Clears the current Menu Bar element of all menus and all submenus.
		"""
		self.app_pointer.menu_bar_element.clear()

	@CatchError
	def set(self, menu_data):
		"""
		Sets the Menu Bar and all submenus to the inputted data.

		:param menu_data: A dictionary containing the data for the menu and submenus.
		"""
		self.clear()
		self.update(menu_data)

	@CatchError
	def update(self, menu_data):
		"""
		Updates the Menu Bar and all submenus.

		:param menu_data: A dictionary containing the data for the menu and submenus.
		"""
		# For each menu bar in the menu_data...
		for menu, data in menu_data.items():
			# Create a new menu
			self.sub_menu = self.app_pointer.menu_bar_element.addMenu(menu)
			# For each submenu in the menu bar's data
			for submenu in data:
				# Set the submenus and their key binds
				if "func" in submenu:
					self.make_menu_action(submenu["name"], submenu["bind"], submenu["func"])
				else:
					self.make_menu_action(submenu["name"], submenu["bind"])

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
		new_action = QAction(action_name, self.app_pointer)
		if shortcut != "False":
			# Set shortcut method (e.g. Ctrl+O)
			new_action.setShortcut(shortcut)
		if func:
			# Connect the Action to a function
			new_action.triggered.connect(func)
		# Set the action to the current menu element
		self.sub_menu.addAction(new_action)

	@staticmethod
	def copy_to_clipboard(live_compile_path):
		"""
		Copies the currently rendered live-compiled image to the clipboard.

		:param live_compile_path: The path to the currently rendered live-compiled image.
		"""
		# Use the Pillow library to open the image
		image = Image.open(live_compile_path)
		# Use the io stream to capture the after-header data (after first 14 for a BMP image)
		output = BytesIO()
		# Convert the image
		image.convert("RGB").save(output, "BMP")
		# Extract, after the header
		data = output.getvalue()[14:]
		output.close()
		OpenClipboard()
		EmptyClipboard()
		SetClipboardData(CF_DIB, data)
		CloseClipboard()

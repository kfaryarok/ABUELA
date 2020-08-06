"""
The Menu file.
Used to store the Status and Menu
classes, and other such objects
which are useful for the menu and status bars.
"""
from io import BytesIO
from PIL import Image
from win32clipboard import OpenClipboard, EmptyClipboard, SetClipboardData, CloseClipboard, CF_DIB


class Status:
	"""
	Class to assist in the few functions and methods
	that are needed for the Status Bar to operate.
	"""

	def __init__(self, update_func):
		self.update_func = update_func()
		self.padding = 10
		self.status_dict = {}
		self.status = ""

	def init_status(self):
		"""
		Initializes the status bar with default 0 amounts.
		This is optimal and is better than not displaying
		anything when the GUI is initialized.
		"""
		self.update_status({
			"Words": 0,
			"Characters": 0,
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

	def update_status(self, status_update):
		"""
		Updates an element (or multiple elements at
		the same time) from the Status Bar.

		:param status_update: A dictionary containing the Status Bar
								elements to udpate, and their new values.
		"""
		self.set_status({**self.status_dict, **status_update})

	def set_status(self, status_dict: dict):
		"""
		Calls on the Status Bar updater function
		in order to repaint the text on the Status Bar.

		:param status_dict: A dictionary containing all the data to set the Status Bar to.
		"""
		statuses = []
		for status, data in status_dict.items():
			statuses.append("{status}: {data}".format(
				status=status,
				data=data
			))
		self.status_dict = status_dict
		self.status = self.padding * " " + str(self.padding * " " + "|" + self.padding * " ").join(statuses)
		self.update_func(self.status)


class Menu:
	"""
	Class to assist with managing the functions,
	uses, and tools that the Menu Bar has to offer.
	"""

	def __init__(self):
		pass

	@staticmethod
	def copy_to_clipboard(liveCompileFunc):
		"""
		Copies the currently rendered live-compiled image to the clipboard.

		:param liveCompileFunc: A lambda, which calls a function, which returns
								the path to the currently rendered live-compiled image.
		"""
		# Use the Pillow library to open the image
		image = Image.open(liveCompileFunc()())
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

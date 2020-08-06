from os import mkdir
from os.path import exists, split
from random import randint
from shutil import rmtree, copyfile
from yaml import load, dump, SafeLoader

try:
	from win32api import GetSystemMetrics
except ImportError:
	pass


class Utility:
	"""
	All utilitarian, effectivity,
	and cleanup functions used
	to assist in small tasks or for
	file navigation / management.
	"""

	def __init__(self):
		pass

	@staticmethod
	def verify_system():
		"""
		Check if the file system is correctly ordered, and if there are missing items, add them.
		"""
		# List off all the directories which could be accidentally deleted
		# /tests/ is irrelevant to GUI runtime
		# /src/ is irrelevant because the file wouldn't be running if it was deleted
		system_paths = {"dir": ["../compile",
		                        "../project",
		                        "../resources",
		                        "../themes",
		                        "../defaults"],
		                "file": ["../themes/default.yaml",
		                         "../project/current.tex",
		                         "../resources/canvas.jpg",
		                         "../resources/logo.jpg",
		                         "../resources/version.txt",
		                         "../resources/settings.yaml"]}
		# For each folder...
		for folder in system_paths["dir"]:
			# Try to create it...
			try:
				mkdir(folder)
			# If it already exists, that's fine
			except FileExistsError:
				pass
		# For each file...
		for file in system_paths["file"]:
			# If the file doesn't exist...
			if not exists(file):
				# If there is a default file for it...
				default_path = "../defaults/{fileName}".format(fileName=str(split(file)[-1]))
				if exists(default_path):
					# Copy it to the file's original location
					copyfile(default_path, file)

	@staticmethod
	def clear_cache():
		"""
		Function which removes all files from the
		compile folder and other such small files
		which are not necessary after runtime.
		"""
		# Clear ../project/current.tex file
		try:
			file = open("../project/current.tex", "w")
			file.write("")
			file.close()
		except:
			pass

		# Remove all files from the ../compile folder by deleting and creating it again
		try:
			rmtree("../compile")
			mkdir("../compile")
		except:
			return

	@staticmethod
	def load_theme(settings):
		"""
		Takes the current configuration settings,
		and returns the color data on the currently selected theme.

		:param settings: The configuration data. Can be retrieved with .getSettings().

		Returns a dictionary of the selected theme's settings.
		"""
		# Create file pointer to current theme
		file = open("../themes/{theme}.yaml".format(theme=settings["theme"]), "r")
		# Read the data from the pointer and convert it to a dictionary
		theme_data = load(file.read(), Loader=SafeLoader)
		# Make sure to close the file pointer
		file.close()
		# Return the data
		return theme_data

	@staticmethod
	def get_settings():
		"""
		Reads the currently set configuration file.

		Returns a Python dictionary containing the configuration data.
		"""
		# Open a connection to the settings file
		filePointer = open("../resources/settings.yaml", "r")
		# Pull the data from the file and convert it to a Python dict
		settingData = load(filePointer.read(), Loader=SafeLoader)
		# Close the connection so it is over-writable / usable
		filePointer.close()
		# Return the configuration data
		return settingData

	@staticmethod
	def set_settings(newSettings):
		"""
		Overwrites the current settings / configuration file with

		:param newSettings: Python dictionary containing the new settings
		"""
		# Open a connection to the settings file
		file_pointer = open("../resources/settings.yaml", "w")
		# Convert and write new configuration data
		file_pointer.write(dump(newSettings))
		# Close the connection so it is over-writable / usable
		file_pointer.close()

	@staticmethod
	def stringify(string):
		"""
		A method to turn a string into a condition-stable string.
		This means that if I want to test if the user input I recieved equals to a string,
		I can make the verification check a lowercase and stripped version of the string,
		and use this function on the user input. Example:

		if stringify(input("Type a word: ")) == "apple"

		Returns a string which is lowercase and stripped of whitespace.
		"""
		return string.strip().lower()

	@staticmethod
	def get_screen():
		"""
		A method which returns the screen resolution.

		Returns an array, described like so: [screen_width, screen_height]
		"""
		return [GetSystemMetrics(0), GetSystemMetrics(1)]

	def get_file_id(self, ext, filePath="", prefix="compile"):
		"""
		This method is used to find a place to write a new file to.
		It checks if the path exists, and if not, returns the path.
		Otherwise, it uses recursion to loop again.

		:param ext: Extension of the file to be identified
		:param filePath: The directory path to the file (including last path separator)
		:param prefix: Optional file prefix
		:return: Full path to the file
		"""
		# Uses recursion until a file named [FILEPATH][PREFIX][RANDOM].[EXT] is not found (ergo can be used as a place to
		# write files to)
		# Example: get_file_id("txt", "../compile/", "compile")
		file_name = "{path}{pre}{num}.{ext}".format(path=filePath, pre=prefix, num=randint(0, 999999999999999), ext=ext)
		return file_name if not exists(file_name) else self.get_file_id(ext, filePath, prefix)

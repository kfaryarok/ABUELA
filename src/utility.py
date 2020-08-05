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
	def __init__(self):
		pass

	@staticmethod
	def verifySystem():
		"""
		Check if the file system is correctly ordered, and if there are missing items, add them.
		"""
		# List off all the directories which could be accidentally deleted
		# /tests/ is irrelevant to GUI runtime
		# /src/ is irrelevant because the file wouldn't be running if it was deleted
		systemPaths = {"dir": ["../compile",
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
		for folder in systemPaths["dir"]:
			# Try to create it...
			try:
				mkdir(folder)
			# If it already exists, that's fine
			except FileExistsError:
				pass
		# For each file...
		for file in systemPaths["file"]:
			# If the file doesn't exist...
			if not exists(file):
				# If there is a default file for it...
				defaultPath = "../defaults/{fileName}".format(fileName=str(split(file)[-1]))
				if exists(defaultPath):
					# Copy it to the file's original location
					copyfile(defaultPath, file)

	@staticmethod
	def clearCache():
		"""
		Function which removes all files from the compile folder.
		"""
		try:
			rmtree("../compile")
			mkdir("../compile")
		except:
			return

	@staticmethod
	def loadTheme(settings):
		"""
		Takes the current configuration settings,
		and returns the color data on the currently selected theme.

		:param settings: The configuration data. Can be retrieved with .getSettings().

		Returns a dictionary of the selected theme's settings.
		"""
		# Create file pointer to current theme
		file = open("../themes/{theme}.yaml".format(theme=settings["theme"]), "r")
		# Read the data from the pointer and convert it to a dictionary
		themeData = load(file.read(), Loader=SafeLoader)
		# Make sure to close the file pointer
		file.close()
		# Return the data
		return themeData

	@staticmethod
	def getSettings():
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
	def setSettings(newSettings):
		"""
		Overwrites the current settings / configuration file with

		:param newSettings: Python dictionary containing the new settings
		"""
		# Open a connection to the settings file
		filePointer = open("../resources/settings.yaml", "w")
		# Convert and write new configuration data
		filePointer.write(dump(newSettings))
		# Close the connection so it is over-writable / usable
		filePointer.close()

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
	def getScreen():
		"""
		A method which returns the screen resolution.

		Returns an array, described like so: [screenWidth, screenHeight]
		"""
		return [GetSystemMetrics(0), GetSystemMetrics(1)]

	def getFileID(self, ext, filePath="", prefix="compile"):
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
		# Example: getFileID("txt", "../compile/", "compile")
		fileName = "{path}{pre}{num}.{ext}".format(path=filePath, pre=prefix, num=randint(0, 999999999999999), ext=ext)
		return fileName if not exists(fileName) else self.getFileID(ext, filePath, prefix)

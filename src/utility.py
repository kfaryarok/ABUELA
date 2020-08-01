from os import mkdir
from os.path import exists
from random import randint
from shutil import rmtree

try:
	from win32api import GetSystemMetrics
except ImportError:
	pass
from yaml import load, dump, SafeLoader


# noinspection PyMethodMayBeStatic
class Utility:
	def __init__(self):
		pass

	def clearCache(self):
		"""
		Function which removes all files from the compile folder.
		"""
		try:
			rmtree("../compile")
			mkdir("../compile")
		except:
			return

	def loadTheme(self, settings):
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

	def getSettings(self):
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

	def setSettings(self, newSettings):
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

	def getScreen(self):
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

from win32api import GetSystemMetrics
from yaml import load, dump


class Utility:

	@staticmethod
	def getSettings():
		# Open a connection to the settings file
		filePointer = open("settings.yaml", "r")
		# Pull the data from the file and convert it to a Python dict
		settingData = load(filePointer.read())
		# Close the connection so it is over-writable / usable
		filePointer.close()
		# Return the configuration data
		return settingData

	@staticmethod
	def setSettings(newSettings):
		# Open a connection to the settings file
		filePointer = open("settings.yaml", "w")
		# Convert and write new configuration data
		filePointer.write(dump(newSettings))
		# Close the connection so it is over-writable / usable
		filePointer.close()

	@staticmethod
	def getScreen():
		return [GetSystemMetrics(0), GetSystemMetrics(1)]
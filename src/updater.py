"""
The Updater file.
Used to store the Updater class, along
with any small helpful variables or
functions to assist with updating.
"""
from os import startfile
from tempfile import gettempdir
from zipfile import ZipFile
from sys import exit as exit_app
from requests import get


class Updater:
	"""
	The Updater class is used for all the
	functions that assist in the program's updating.
	This ranges from checking for updates, to
	actually updating the software of the program.
	"""
	def __init__(self):
		pass

	@staticmethod
	def get_url():
		"""
		A function which gets the URL of the program's page.

		:return: The HTTPS URL to the website.
		"""
		# Point to the link file
		file = open("../link.txt", "r")
		# Read the file and retrieve the link
		link = file.read().strip()
		# Close the file
		file.close()
		# Return the link
		return link

	@staticmethod
	def check_updates():
		"""
		A function to check if there are updates for the software.

		Returns True if there are updates, False if there are none.
		"""
		# Download latest version as a text file from GitHub
		latest_version = get("https://raw.githubusercontent.com/kfaryarok/ABUELA/master/version.txt").text

		# Open the current version as the file in the resources folder
		file = open("../resources/version.txt", "r")
		current_version = file.read()
		file.close()

		# Make the comparison
		return latest_version > current_version

	def download_updates(self):
		"""
		Downloads the latest version of ABUELA to a temporary directory.

		Returns True if operation succeeded, returns False if not.
		"""
		try:
			# Create the file pointer for the zip
			file = open(str(gettempdir()) + "/ABUELA_UPDATE.zip", "wb")
			# Download the zip and dump its contents into the file
			file.write(get("{base_url}/archive/master.zip".format(
				base_url=self.get_url()
			)).content)
			# Close the file pointer
			file.close()
			return True
		except:
			return False

	def install_updates(self):
		"""
		This function is meant to install updates. It will,
		regardless of state, do a check for updates and will
		download them (even if they are already downloaded).

		Terminates the app and installs updates if
		successful, returns False if unsuccessful.
		"""
		# If there are updates...
		if self.check_updates():
			# If the updates were downloaded successfully...
			if self.download_updates():
				# Extract the folder from the zip file
				with ZipFile(str(gettempdir()) + "/ABUELA_UPDATE.zip") as zip_ref:
					zip_ref.extractall(str(gettempdir()))

				# Generate a batch file to install the folder
				file = open(str(gettempdir()) + "/ABUELA_UPDATER.bat", "w")
				file.write("""@echo off
title ABUELA_UPDATER
TIMEOUT /T 3 /NOBREAK >nul
xcopy /E /Y "ABUELA-master" "%1" """)
				file.close()

				# Generate a VBS file to silently execute the batch file
				file = open(str(gettempdir()) + "/ABUELA_UPDATER.vbs", "w")
				file.write("""Set WshShell = CreateObject("WScript.Shell") 
WshShell.Run chr(34) & "ABUELA_UPDATER.bat" & Chr(34), 0
Set WshShell = Nothing""")
				file.close()

				# Run the VBS file
				startfile("ABUELA_UPDATER.vbs")

				# Terminate the app
				exit_app(1)
			else:
				return False
		else:
			return False

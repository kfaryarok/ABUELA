"""
The Utility file, used mainly for the Utility class.
"""
from os import mkdir, remove, listdir, walk
from os.path import exists, split, splitext
from random import randint
from shutil import rmtree, copyfile

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QFileDialog
from yaml import load, dump, SafeLoader

from project import Project

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

	def __init__(self, app_pointer):
		self.app_pointer = app_pointer

	@staticmethod
	def safe_remove(file_name):
		"""
		A method to attempt deleting a file. Will not spurt errors.

		:return: True if a successful deletion was executed, False if not.
		"""
		try:
			remove(file_name)
			return True
		except:
			return False

	def reset_system(self):
		"""
		Reset all the settings and files to their default state.
		"""
		# Delete all currently 'installed' files
		for file in ["../gui_themes/default.yaml",
		             "../resources/canvas.jpg",
		             "../resources/logo.jpg",
		             "../resources/logo.ico",
		             "../resources/version.txt",
		             "../resources/settings.yaml"]:
			self.safe_remove(file)
		# Use the verify_system function to copy all defaults back to place
		self.verify_system()
		# Restart the GUI (themes and other settings will have changed)
		self.app_pointer.restart_app()

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
		                        "../gui_themes",
		                        "../defaults"],
		                "file": ["../gui_themes/default.yaml",
		                         "../project/current.tex",
		                         "../resources/canvas.jpg",
		                         "../resources/logo.jpg",
		                         "../resources/logo.ico",
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

	def clear_cache(self):
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

		# For each folder in the root directory
		for dir_name in [x[0] for x in walk("../")]:
			# Remove all files with the following extensions
			self.remove_by_ext(["aux", "log"], dir_name)

	def remove_by_ext(self, ext_list: list, dir_name: str):
		"""
		Walks down a directory and deletes all files with a given extension.

		:param ext_list: A list of all the extensions to eliminate.
		:param dir_name: The name of the root directory to walk down.
		"""
		# For each file in the current directory
		for file in listdir(dir_name):
			# For each extension loaded
			for ext in ext_list:
				# If the extension matches
				if file.endswith(".{ext}".format(
						ext=ext
				)):
					# Delete the file
					self.safe_remove("{dir}/{file}".format(
						dir=dir_name,
						file=file
					))

	@staticmethod
	def load_theme(settings):
		"""
		Takes the current configuration settings,
		and returns the color data on the currently selected theme.

		:param settings: The configuration data. Can be retrieved with .getSettings().

		Returns a dictionary of the selected theme's settings.
		"""
		# Create file pointer to current theme
		file = open("../gui_themes/{theme}.yaml".format(theme=settings["theme"]), "r")
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
		file_pointer = open("../resources/settings.yaml", "r")
		# Pull the data from the file and convert it to a Python dict
		setting_data = load(file_pointer.read(), Loader=SafeLoader)
		# Close the connection so it is over-writable / usable
		file_pointer.close()
		# Return the configuration data
		return setting_data

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
		This means that if I want to test if the user input I received equals to a string,
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

	@staticmethod
	def parse_errors(error_message):
		"""
		Parses the LaTeX compiler error message,and
		returns a dictionary of line to error messages.

		:param error_message: The full error message string
		:return: A dictionary containing the line of the error, and the message accompanying it
		"""
		errors = dict()
		for chunk in error_message.split("../project/current.tex:"):
			line = chunk.split(":")[0]
			message = ":".join(chunk.split(":")[1:]).strip()
			if line.strip().isnumeric():
				errors[int(line)] = message
		return errors

	@staticmethod
	def hex_to_rgb(value):
		"""
		Return an RGB Tuple from the given Hex string.

		:param value: A string which represents a 6 digit hex color
		:return: A tuple which contains the 3 values for R, G, B
		"""
		value = value.lstrip('#')
		lv = len(value)
		return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

	def open_file(self):
		"""
		A function to prompt the user for a file to open.

		:return: Returns the file path to the selected file.
		"""
		# Initialize a Dialog and prompt the user
		file_path = QFileDialog.getOpenFileName(parent=self.app_pointer,
		                                        caption="Open",
		                                        filter="Tex File (*.tex)")[0]

		# If the operation wasn't cancelled
		if file_path:
			# Create a Project class and append it to the 'project manager' array
			project = Project(file_path)
			self.app_pointer.projects.append(project)

			# Open it in the editor
			self.app_pointer.switch_project(len(self.app_pointer.projects) - 1)

			# Artificially trigger the event filter so the live-compiler activates
			self.app_pointer.thread_compile()

	def save_file(self):
		"""
		A function to prompt the user for a path to save to.

		:return: Returns the selected file path
		"""
		# Prompt for file path
		file_path = QFileDialog.getSaveFileName(parent=self.app_pointer,
		                                        caption="Save as",
		                                        filter="Tex File (*.tex);;PDF File (*.pdf);;JPG File (*.jpg)")[0]

		# If the user did not cancel the dialogue operation
		if file_path:
			# Split the full path into a path and extension
			split_path = splitext(file_path)

			# If the extension is a .tex, then save it as a Project
			if split_path[1] == ".tex":
				# Create the Project file
				self.app_pointer.status_bar_instance.update_status({"Task": "Copying data..."})
				project = Project(file_path)

				# Copy the data from the current Project to the new object
				project.data = self.app_pointer.project.data
				project.preamble = self.app_pointer.project.preamble
				project.peroration = self.app_pointer.project.peroration

				# Save the project
				self.app_pointer.status_bar_instance.update_status({"Task": "Saving..."})
				project.save(project.data, overwrite=True)

				# Add the new Project to the project manager
				self.app_pointer.status_bar_instance.update_status({"Task": "Switching projects..."})
				self.app_pointer.projects.append(project)

				# Close the current project
				self.app_pointer.close_project()

				# Switch onto the most recently added project
				self.app_pointer.switch_project(len(self.app_pointer.projects) - 1)
			elif split_path[1] == ".pdf":
				# Import this here, otherwise it's a recursive import and will lead to an error
				self.app_pointer.status_bar_instance.update_status({"Task": "Loading..."})
				from compile import Compile

				# If the extension is a pdf, compile the file again
				self.app_pointer.status_bar_instance.update_status({"Task": "Compiling..."})
				c = Compile(self.app_pointer)
				pdf_path, error_msg = c.compile(self.app_pointer.project.file_name)

				# Copy the file to its final path
				self.app_pointer.status_bar_instance.update_status({"Task": "Copying..."})
				copyfile(pdf_path, file_path)
			# If the extension is anything else (a .jpg)
			else:
				# Import this here, otherwise it's a recursive import and will lead to an error
				self.app_pointer.status_bar_instance.update_status({"Task": "Loading..."})
				from compile import compile_to_image

				# Compile to an image
				self.app_pointer.status_bar_instance.update_status({"Task": "Converting..."})
				image_path = compile_to_image(
					app_pointer=self.app_pointer,
					path=self.app_pointer.project.file_name,
					quality=self.app_pointer.settings["compile_quality"]
				)[0]

				# Copy it to the full path
				self.app_pointer.status_bar_instance.update_status({"Task": "Copying..."})
				copyfile(image_path + "1.jpg", file_path)

			# Reset Task status
			self.app_pointer.status_bar_instance.update_status({"Task": "Idling"})

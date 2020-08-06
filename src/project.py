"""
The Project file.
Used to store the Project class.
"""
from os.path import exists


class Project:
	"""
	The Project class is the class used
	to assist with single-file management.
	It stores the data on the file itself,
	any preamble data (LaTeX code), and such.
	It also includes methods for saving and opening files.
	"""
	def __init__(self, fileName):
		self.fileName = fileName
		self.data = ""
		self.preamble = ""

	def new(self):
		"""
		Generates a new file as a template for the project
		"""
		self.data = ""
		self.preamble = """\\documentclass[12pt]{article}\n\\begin{document}"""

	def save(self, text, overwrite=False):
		"""
		Saves the text to the Project object's file
		If overwrite is True, then it will overwrite the current project's file regardless of state.
		If it is False, then it will only save if there isn't a file currently in place.
		"""
		self.data = text
		if overwrite:
			# Point to the file
			file = open(self.fileName, "w")
			# Write the data to the file
			data_size = file.write("{pre}\n{code}\n{end}".format(
				pre=self.preamble,
				code=self.data,
				end="\\end{document}"
			))
			# Close the file pointer
			file.close()
			return data_size
		else:
			if exists(self.fileName):
				# If the file exists, don't overwrite it
				return
			else:
				# If it doesn't exist, call the function again as if it is meant to overwrite it
				self.save(text, overwrite=True)

	def open(self):
		"""
		Reads the data in the Project's file.

		Returns the data as a string.
		"""
		# Point to the file
		file = open(self.fileName, "r")
		# Read the data
		file_data = file.read()
		# Close the file pointer
		file.close()
		# Return the file's data
		self.preamble = file_data.split("\\begin{document}")[0]
		self.data = "\\begin{document}".join(file_data.split("\\begin{document}")[1:])
		return file_data

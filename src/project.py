"""
The Project file.
Used to store the Project class.
"""
from os.path import exists, split


class Project:
	"""
	The Project class is the class used
	to assist with single-file management.
	It stores the data on the file itself,
	any preamble data (LaTeX code), and such.
	It also includes methods for saving and opening files.
	"""

	def __init__(self, file_name):
		self.file_name = file_name
		self.name = split(self.file_name)[-1]
		self.data = str()
		self.preamble = str()
		self.peroration = str()

	def unload(self):
		"""
		Saves memory by unloading data in objects.
		"""
		if hasattr(self, "data"):
			del self.data
		if hasattr(self, "preamble"):
			del self.preamble
		if hasattr(self, "peroration"):
			del self.peroration

	def new(self):
		"""
		Generates a new file as a template for the project
		"""
		self.data = str()
		self.preamble = """\\documentclass[12pt]{article}\n\\begin{document}"""
		self.peroration = """\n\\end{document}"""

	def save(self, text, overwrite=False):
		"""
		Saves the text to the Project object's file
		If overwrite is True, then it will overwrite the current project's file regardless of state.
		If it is False, then it will only save if there isn't a file currently in place.
		"""
		self.data = text
		if overwrite:
			# Point to the file
			file = open(self.file_name, "w", encoding="utf-8")
			# Write the data to the file
			# data_size = file.write("{pre}\n{code}\n{post}".format(
			# 	pre=self.preamble,
			# 	code=self.data,
			# 	post=self.peroration
			# ))
			data_size = file.write(self.data)
			# Close the file pointer
			file.close()
			return data_size
		else:
			if exists(self.file_name):
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
		file = open(self.file_name, "r", encoding="utf-8")
		# Read the data
		file_data = file.read()
		# Close the file pointer
		file.close()
		# Return the file's data
		self.data = file_data
		# self.preamble = file_data.split("\\begin{document}")[0]
		# self.peroration = file_data.split("\\end{document}")[-1]
		# self.data = "\\end{document}".join(
		# 	"\\begin{document}".join(
		# 		file_data
		# 			.split("\\begin{document}")[1:])
		# 		.split("\\end{document}")[:-1])
		return self.data

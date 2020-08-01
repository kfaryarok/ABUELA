from os.path import exists


class Project:
	def __init__(self, fileName):
		self.fileName = fileName

	def save(self, text, overwrite=False):
		"""
		Saves the text to the Project object's file
		If overwrite is True, then it will overwrite the current project's file regardless of state.
		If it is False, then it will only save if there isn't a file currently in place.
		"""
		if overwrite:
			# Point to the file
			file = open(self.fileName, "w")
			# Write the data to the file
			dataSize = file.write(text)
			# Close the file pointer
			file.close()
			return dataSize
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
		fileData = file.read()
		# Close the file pointer
		file.close()
		# Return the file's data
		return fileData

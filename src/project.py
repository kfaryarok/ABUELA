from os.path import exists


class Project:
	def __init__(self, fileName):
		self.fileName = fileName

	def save(self, text, overwrite=False):
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
				return False
			else:
				# If it doesn't exist, call the function again as if it is meant to overwrite it
				self.save(text, overwrite=True)

	def open(self):
		# Point to the file
		file = open(self.fileName, "r")
		# Read the data
		fileData = file.read()
		# Close the file pointer
		file.close()
		# Return the file's data
		return fileData

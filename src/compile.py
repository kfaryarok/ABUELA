"""
The Compile file.
Stores objects (including classes
and functions) for compiling LaTeX
code into .pdf files and into image files.
"""
from os import remove
from os.path import splitext, exists
from shutil import copyfile
from subprocess import Popen, PIPE

from pdf2image import convert_from_path
from pdf2image.exceptions import PDFPageCountError
from psutil import process_iter

from utility import Utility


def compile_to_image(app_pointer, path, quality):
	"""
	Function to shorten the process of converting the current.tex file to an image.

	Returns an array containing the constant path to the
	images (more info in the .image() method), and any of
	the STDOUT messages (usually errors) from the compiler.
	"""
	# Create an instance of the compiler
	app_pointer.status_bar_instance.update_status({"Task": "Compiling..."})
	c = Compile(app_pointer)
	# Compile to a .pdf
	file_path, error_msg = c.compile(path)
	# If the file was compiled successfully...
	if file_path:
		# Convert the .pdf to a picture
		app_pointer.status_bar_instance.update_status({"Task": "Converting..."})
		split_path = c.image(file_path, quality=quality)
		# If the image was created...
		if split_path:
			return [split_path, error_msg]
		else:
			return [False, False]
	else:
		return [False, error_msg]


class Compile:
	"""
	The Compile class is the main class
	used to assist with all compiling
	and converting functions. This includes
	converting LaTeX code to PDF files
	and PDF files to image files.
	"""
	def __init__(self, app_pointer):
		self.app_pointer = app_pointer

	def compile(self, file_path):
		"""
		This method takes the current.tex file (Currently open project) and
		compiles it to a .pdf file, which is then put in

		Returns an array containing the path to the compiled .pdf, and a
		string containing any error messages from compilation.
		"""
		# Make sure pdflatex isn't in use at the moment or accessing files
		self.app_pointer.status_bar_instance.update_status({"Task": "Killing processes..."})
		self.kill()
		# Execute pdflatex with subprocess library
		self.app_pointer.status_bar_instance.update_status({"Task": "Multiprocessing..."})
		proc = Popen([
			'xelatex',
			'-quiet',
			'-enable-installer',
			'-c-style-errors',
			'-job-name=compile',
			file_path
		], stdout=PIPE)
		# Wait until execution is over, then copy all STDOUT text to an array
		self.app_pointer.status_bar_instance.update_status({"Task": "Compiling..."})
		proc.wait()
		# Read STDOUT (printed data)
		self.app_pointer.status_bar_instance.update_status({"Task": "Parsing..."})
		stdout_data = "".join([i.decode() for i in proc.stdout.readlines()])
		# Create instance of Utility class so we can move the compiled pdf to our folder
		utils = Utility(False)
		file_name = utils.get_file_id("pdf", "../compile/")
		# Try to move the file
		try:
			self.app_pointer.status_bar_instance.update_status({"Task": "Copying..."})
			copyfile("compile.pdf", file_name)
		except FileNotFoundError:
			# If the move failed, then return False.
			return [False, stdout_data]
		# Read the STDOUT lines from execution
		# Decode each one (current type is bytes, convert it to string)
		# Merge all the lines into one string
		# Return the file path if the file exists, otherwise return False
		if exists(file_name):
			return [file_name, stdout_data]
		else:
			return [False, stdout_data]

	@staticmethod
	def safe_remove(file):
		"""
		Attempts to remove a file, without the knowledge of whether it exists or not.

		:param file: The path to the file to clear.
		:return: True if deleted successfully, False if not or an error occurred.
		"""
		try:
			if exists(file):
				remove(file)
				return True
			else:
				return False
		except Exception as e:
			print("REPORT THIS ASAP 4 | ", e.__dict__)
			return False

	def clean(self):
		"""
		Deletes the temporary files generated by the pdflatex compiler
		"""
		if self.app_pointer:
			self.app_pointer.status_bar_instance.update_status({"Task": "Cleaning..."})
		self.safe_remove("compile.pdf")
		self.safe_remove("compile.aux")
		self.safe_remove("compile.log")

	@staticmethod
	def kill():
		"""
		Kills the pdflatex process, if it is currently being used.
		This method is meant to save RAM and assure that the compile.pdf data location is writable to.
		This method doesn't use the best algorithm, but it's one which can work on multiple operating systems.
		"""
		for proc in process_iter():
			# check whether the process name matches
			if "pdflatex" in proc.name():
				proc.kill()

	def image(self, path, quality=100):
		"""
		Converts a compiled LaTeX .pdf file to an image.

		Each page is converted as an image, which is exported
		in a .jpg file with the same name as the original .pdf
		file, and with the page number as a suffix.

		:param path: The full path to the compiled .pdf file.
		:param quality: The DPI of the image to create (Defaults to 100).

		Returns the constant path, not including the altering suffix.
		If the path to one of the compiled images is "../compile/compile1230.jpg",
		then the returned data would be "../compile/compile123"
		"""
		# Attempt to convert the files to an object
		try:
			self.app_pointer.status_bar_instance.update_status({"Task": "Loading..."})
			pages = convert_from_path(path, quality)
		except PDFPageCountError:
			return False

		# For each page in the pdf
		self.app_pointer.status_bar_instance.update_status({"Task": "Converting..."})
		page_index = int()
		for page in pages:
			page_index += 1
			# Save it as a picture
			page.save("{path}{index}.jpg".format(
				path=splitext(path)[0],
				index=page_index
			), 'JPEG')

		# Clean trash files
		try:
			self.clean()
		except PermissionError:
			# If the .pdf file is inaccessible, then a new update is currently compiling
			return False

		# Verify that all the pages were created successfully
		self.app_pointer.status_bar_instance.update_status({"Task": "Verifying..."})
		all_exists = True
		# For each page index (starting from 1)
		for i in range(1, len(pages) + 1):
			# If it doesn't exist,
			if not exists("{path}{index}.jpg".format(
				path=splitext(path)[0],
				index=i
			)):
				# Then not all of the images were created successfully
				all_exists = False

		# If all the images were created successfully...
		if all_exists:
			# Return the path
			return splitext(path)[0]
		else:
			# Otherwise, return False
			return False

from os import remove
from os.path import splitext
from shutil import copyfile
from subprocess import Popen, PIPE

from pdf2image import convert_from_path
from pdf2image.exceptions import PDFPageCountError
from psutil import process_iter

from utility import Utility


def compileToImage(quality):
	"""
	Function to shorten the process of converting the current.tex file to an image.

	Returns an array containing the constant path to the
	images (more info in the .image() method), and any of
	the STDOUT messages (usually errors) from the compiler.
	"""
	c = Compile()
	fName, errorMsg = c.compile()
	# If the file was compiled successfully...
	if fName:
		splitPath = c.image(fName, quality=quality)
		if splitPath:
			return [splitPath, errorMsg]
		else:
			return [False, False]
	else:
		return [False, errorMsg]


class Compile:
	def __init__(self):
		pass

	def compile(self):
		"""
		This method takes the current.tex file (Currently open project) and
		compiles it to a .pdf file, which is then put in

		Returns an array containing the path to the compiled .pdf, and a
		string containing any error messages from compilation.
		"""
		# Make sure pdflatex isn't in use at the moment or accessing files
		self.kill()
		# Execute pdflatex with subprocess library
		proc = Popen(['pdflatex', '-quiet', '-job-name=compile', "../project/current.tex"], stdout=PIPE)
		# Wait until execution is over, then copy all STDOUT text to an array
		proc.wait()
		stdoutArray = [i.decode() for i in proc.stdout.readlines()]
		# Create instance of Utility class so we can move the compiled pdf to our folder
		utils = Utility()
		fileName = utils.getFileID("pdf", "../compile/", "compile")
		# Try to move the file
		try:
			copyfile("compile.pdf", fileName)
		except FileNotFoundError:
			# If the move failed, then return False.
			return [False, "".join(stdoutArray)]
		# Read the STDOUT lines from execution
		# Decode each one (current type is bytes, convert it to string)
		# Merge all the lines into one string
		# Return the string
		return [fileName, "".join(stdoutArray)]

	def safeRemove(self, file):
		"""
		Attempts to remove a file, without the knowledge of whether it exists or not.

		:param file: The path to the file to delete.
		:return: True if deleted successfully, False if not or an error occurred.
		"""
		try:
			remove(file)
			return True
		except:
			return False

	def clean(self):
		"""
		Deletes the temporary files generated by the pdflatex compiler
		"""
		self.safeRemove("compile.pdf")
		self.safeRemove("compile.aux")
		self.safeRemove("compile.log")

	def kill(self):
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

		:param path: The path, filename, and extension to the compiled .pdf file.
		:param quality: The DPI of the image to create (Defaults to 100).

		Returns the constant path, not including the altering suffix.
		If the path to one of the compiled images is "../compile/compile1230.jpg",
		then the returned data would be "../compile/compile123"
		"""
		try:
			pages = convert_from_path(path, quality)
		except PDFPageCountError:
			return False
		pageIndex = 0
		# For each page in the pdf
		for page in pages:
			pageIndex += 1
			# Save it as a picture
			page.save("{path}{index}.jpg".format(path=splitext(path)[0], index=pageIndex), 'JPEG')
		# Clean trash files
		try:
			self.clean()
		except PermissionError:
			# If the .pdf file is inaccessible, then a new update is currently compiling
			return False
		# Return path
		return splitext(path)[0]

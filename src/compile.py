from os import remove
from os.path import exists
from shutil import copyfile
from subprocess import Popen, PIPE
from psutil import process_iter

from utility import Utility


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
		proc = Popen(['pdflatex', '-quiet', '-job-name=compile', "current.tex"], stdout=PIPE)
		# Wait until execution is over
		proc.wait()
		# Create instance of Utility class so we can move the compiled pdf to our folder
		utils = Utility()
		fileName = utils.getFileID("pdf", "compile\\", "compile")
		copyfile("compile.pdf", fileName)
		# Clean trash files
		self.clean()
		# Read the STDOUT lines from execution
		# Decode each one (current type is bytes, convert it to string)
		# Merge all the lines into one string
		# Return the string
		return [fileName, "".join([i.decode() for i in proc.stdout.readlines()])]

	def clean(self):
		"""
		Deletes the temporary files generated by the pdflatex compiler
		"""
		if exists("compile.aux"):
			remove("compile.aux")
		if exists("compile.log"):
			remove("compile.log")

	def kill(self):
		"""
		Kills the pdflatex process, if it is currently being used.
		This method is meant to save RAM and assure that the compile.pdf data location is writable to.
		This method doesn't use the best algorithm, but it's one which can work on multiple operating systems.
		"""
		for proc in process_iter():
			# check whether the process name matches
			if proc.name().contains("pdflatex"):
				proc.kill()

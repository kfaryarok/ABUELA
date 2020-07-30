from os import remove
from os.path import exists
from subprocess import Popen, PIPE
from psutil import process_iter


class Compile:
	def __init__(self):
		pass

	def compile(self):
		# Make sure pdflatex isn't in use at the moment or accessing files
		self.kill()
		# Execute pdflatex with subprocess library
		proc = Popen(['pdflatex', '-quiet', '-job-name=compile', 'test.tex'], stdout=PIPE)
		# Wait until execution is over
		proc.wait()
		# Clean trash files
		self.clean()
		# Read the STDOUT lines from execution
		# Decode each one (current type is bytes, convert it to string)
		# Merge all the lines into one string
		# Return the string
		return "".join([i.decode() for i in proc.stdout.readlines()])

	@staticmethod
	def clean():
		if exists("compile.aux"):
			remove("compile.aux")
		if exists("compile.log"):
			remove("compile.log")

	@staticmethod
	def kill():
		for proc in process_iter():
			# check whether the process name matches
			if proc.name() == "pdflatex.exe":
				proc.kill()

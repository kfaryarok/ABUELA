"""
The Error file is the file used to store
the Error class. More info on the class
is labeled in the class docstring.
"""
from PyQt5.QtWidgets import QMessageBox


class Error:
	"""
	The Error class is the class meant to display all
	sorts of warnings, errors, and informative messages
	as dialogue boxes on screen.
	"""

	def __init__(self):
		pass

	def normal(self, title, text, subtext):
		"""
		Prompts a dialogue as a normal message (no icon).

		:param title: The title of the message box
		:param text: The title inside the message box
		:param subtext: The subtext inside the message box
		"""
		return self.dialogue(QMessageBox.NoIcon, title, text, subtext)

	def question(self, title, text, subtext):
		"""
		Prompts a dialogue as an question-icon message.

		:param title: The title of the message box
		:param text: The title inside the message box
		:param subtext: The subtext inside the message box
		"""
		return self.dialogue(QMessageBox.Question, title, text, subtext)

	def info(self, title, text, subtext):
		"""
		Prompts a dialogue as an info message.

		:param title: The title of the message box
		:param text: The title inside the message box
		:param subtext: The subtext inside the message box
		"""
		return self.dialogue(QMessageBox.Information, title, text, subtext)

	def warning(self, title, text, subtext):
		"""
		Prompts a dialogue as an warning message.

		:param title: The title of the message box
		:param text: The title inside the message box
		:param subtext: The subtext inside the message box
		"""
		return self.dialogue(QMessageBox.Warning, title, text, subtext)

	def error(self, title, text, subtext):
		"""
		Prompts a dialogue as an error message.

		:param title: The title of the message box
		:param text: The title inside the message box
		:param subtext: The subtext inside the message box
		"""
		return self.dialogue(QMessageBox.Critical, title, text, subtext)

	@staticmethod
	def dialogue(icon, title, text, subtext):
		"""
		Create a Dialogue / Message box widget
		and display it to the screen.

		:param icon: The type of icon to show on the left
		:param title: The title of the message box
		:param text: The title inside the message box
		:param subtext: The subtext inside the message box
		:return Returns the exit value (or selection value) of the dialogue
		"""
		msg = QMessageBox()
		msg.setIcon(icon)
		msg.setWindowTitle(title)
		msg.setText(text)
		msg.setInformativeText(subtext)
		return msg.exec_()

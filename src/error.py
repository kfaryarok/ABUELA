"""
The Error file is the file used to store
the Error class, along with other
error-related functions and objects.
More info on the class is labeled
in the class docstring.
"""
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMessageBox
from functools import wraps


def CatchError(func):
	"""
	A decorator to catch uneeded errors or
	errors that, to fix, would simply require
	too many if statements to be efficient / readable.

    :param func: The function to decorate / pad.
    :return:
    """

	@wraps(func)
	def wrapper(*args, **kwargs):
		"""
		The main function to wrap / decorate

        :param args: Any function arguments
        :param kwargs: Any function kwarguments
        :return:
        """
		try:
			return func(*args, **kwargs)
		except RuntimeError:
			pass

	return wrapper


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

		:param icon: The type of icon to show on the left as a Qt object, or a string to the icon's path
		:param title: The title of the message box
		:param text: The title inside the message box
		:param subtext: The subtext inside the message box
		:return Returns the exit value (or selection value) of the dialogue
		"""
		# Initialize the message box
		msg = QMessageBox()
		# Set window icon
		msg.setWindowIcon(QIcon("../resources/logo.ico"))
		# Set message icon type
		if type(icon) == str:
			# If a string is inputted, then it's a path to the file
			msg.setIconPixmap(QPixmap(icon))
		else:
			# Otherwise, it's a Qt object
			msg.setIcon(icon)
		# Set window title
		msg.setWindowTitle(title)
		# Set text title
		msg.setText(text)
		# Set subtext data
		msg.setInformativeText(subtext)
		# Execute and return the data
		return msg.exec_()

"""
This file contains all the custom exceptions
used by the cleanup_model class.
"""

class DateConversionError(Exception):
	"""
	Custom exception raised for incorrect date input when calling
	set_target_end_date or set_target_start_date for the cleanup_model class.

	Attributes:
		message: explanation of the error
	"""

	def __init__(self,
				 message="Date input is incorrect, please make sure "
						 "input follows the format: month/date/year"):
		self.message = message
		super().__init__(self.message)


class EmptyConditionsError(Exception):
	"""
	Custom exception raised when trying to delete emails with no
	deletion conditions set

	Attributes:
		message: explanation of the error
	"""

	def __init__(self,
				 message="Missing any deletion conditions, cannot delete emails"):
		self.message = message
		super().__init__(self.message)

class NoEmailsError(Exception):
	"""
		Custom exception raised when program sees no emails
		have been signed into outlook

		Attributes:
			message: explanation of the error
		"""

	def __init__(self,
				 message="No emails have been signed into on outlook, please sign in onto outlook application with at least one email"):
		self.message = message
		super().__init__(self.message)

class OutlookNotOpenError(Exception):
	"""
			Custom exception raised when program sees no emails
			have been signed into outlook

			Attributes:
				message: explanation of the error
			"""

	def __init__(self,
				 message="Outlook Application Must Be Open Before Running this Program"):
		self.message = message
		super().__init__(self.message)

class MissingStartDate(Exception):
	"""
			Custom exception raised when enter deletion parameters
			and start date is missing

			Attributes:
				message: explanation of the error
			"""

	def __init__(self,
				 message="If there is an end date, then start date cannot be left empty"):
		self.message = message
		super().__init__(self.message)
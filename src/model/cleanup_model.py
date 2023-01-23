import win32com.client as client
from src.model.cleanup_custom_exceptions import *
from src.model.date_handler import date_handler

"""
This class is meant to have code that connects to outlook, pick
an email etc. and handle things before functionality of email-deletion.
There should only ever be one of this class and so I will apply a 
singleton pattern. This model will contain all functionality of actual e-mail 
deletion.
"""

class cleanup_model():

	def __init__(self):
		"""
		Constructor for the model. Does not require any parameters.
		It sets up empty attributes for the class.
		"""

		self.date_utility = date_handler()

		################ variables relating to deleting conditions ################
		self.target_sender_email = None    # string
		self.target_start_date = None      # datetime obj
		self.target_end_date = None        # datetime obj
		self.target_subject_keyphrase = None # string

		# dictionary used to hold information for confirmation string question
		# Dynamically set at runtime
		# key: 0, value : target_sender_email
		# key: 2, value : target_subject_key_[hrase
		self.verification_add_on = {}

	def set_target_sender_email(self, email: str) -> None:
		'''
		Set target_sender_email attribute if input is not empty
		:param email: (str) sender email target
		:return: None
		'''
		if email.isspace() or email == "":
			return
		else:
			self.target_sender_email = email
			self.verification_add_on[0] = email

	def set_target_subject_keyphrase(self, subject_key: str) -> None:
		'''
		Sets the target subject key if input is not empty
		:param subject_key: {str} representation of a word or phrase to target
		:return:None
		'''
		if subject_key.isspace() or subject_key == "":
			return
		else:
			self.target_subject_keyphrase = subject_key
			self.verification_add_on[2] = subject_key

	def set_target_start_date(self, date: str):
		'''
		Sets the target start date, with time at 00:00:00
		:param date: {str} representation of datetime, must be in the format mm/dd/yyyy
		:return: None
		'''
		#if empty date input then don't do anything
		if date.isspace() or date == "":
			return
		else:
			try:
				date_list_start = self.date_utility.process_str_date(date)
			except ValueError:
				raise DateConversionError()
			self.target_start_date = self.date_utility.convert_list_into_datetime(date_list_start)
			string_date_start = self.target_start_date.strftime("%m/%d/%Y")
			self.verification_add_on[1] = string_date_start

	def set_target_end_date(self, date: str):
		'''
		Sets the target end date with time at 11:59:59
		:param date: {str} representation of datetime, must be in the format mm/dd/yyyy
		:return:
		'''
		#if empty date input
		if date.isspace() or date == "":
			#check that start date is also empty
			if self.target_start_date is None:
				return
			else:
				raise MissingStartDate()

		# if input is not empty, but start date is, raise error
		if self.target_start_date is None:
			raise MissingStartDate()

		# if start_date is already set, set the end_date
		try:
			date_list_end = self.date_utility.process_str_date(date)
		except ValueError:
			raise DateConversionError()

		self.target_end_date = self.date_utility.convert_list_into_datetime(date_list_end,endtime=True)
		date_existing = self.verification_add_on[1]
		if date_existing == "" or date_existing is None:
			raise MissingStartDate()
		else:
			date_existing += f" to {self.target_end_date.strftime('%m/%d/%Y')}"
		self.verification_add_on[1] = date_existing

	def clear_deleting_conditions(self):
		'''
		Set all deleting conditions (attributes) to None and resetting appropriate attributes
		:return: None
		'''

		self.target_sender_email = None
		self.target_start_date = None
		self.target_end_date = None
		self.target_subject_keyphrase = None
		self.verification_add_on = {}

import win32com.client as client
from src.model.cleanup_custom_exceptions import *

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

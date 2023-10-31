class cleanup_view_interface():
	"""
	This interface lays out all mandated methods for a view to be used
	in conjunction with the cleanup_model class
	"""

	def display_welcome(self):
		"""
		Displays the welcome page for the model.
		:return:
		"""
		raise NotImplementedError()

	def display_message(self, msg: str, exit_after_msg: bool = True):
		"""
		Displays a message in the form of a string. If exit_after_msg
		:param msg: (str) Message to display
		:param exit_after_msg: (bool) if true, program will close after displaying message.
		:return:
		"""
		raise NotImplementedError()

	def get_email_to_use_for_program(self, dict_email_choices: dict) -> str:
		'''
		Display choices available from model and gets input from user.
		Returns user input as str format of an integer value
		:param dict_email_choices: (dict) This should be the mailbox_options
				attr of the cleanup_model
		:return:
		'''
		raise NotImplementedError()

	def get_target_sender(self) -> str:
		"""
		Prompts the user and gets the target_sender input from the user.
		:return: (str) sender email used for matching condition for the model
					ex. someone@gmail.com
		"""
		raise NotImplementedError()

	def get_target_sender_name(self) -> str:
		"""
		Prompts the user and gets the target_sender_name from the user.
		:return: (str) The keyword/phrase to be used in the matching conditions
					of the model
		"""
		raise NotImplementedError()

	def get_target_start_date(self) -> str:
		"""
		Prompts the user and gets the target_start_date input from the user.
		:return: (str) date should be in the format of month/day/year.
						This will be used for the matching conditions for the model.
		"""
		raise NotImplementedError()

	def get_target_end_date(self) -> str:
		"""
		Prompts the user and gets the target_end_date input from the user.
		:return: (str) date should be in the format of month/day/year
					This will be used for the matching conditions for the model.
		"""
		raise NotImplementedError()

	def get_target_subject_keyword(self) -> str:
		"""
		Prompts the user and gets the keyword and input from the user.
		:return: (str) The keyword/phrase to be used in the matching conditions
					of the model
		"""
		raise NotImplementedError()

	def confirm_deletion_parameters(self, confirmation_str: str, selected_email) -> bool:
		"""
		Asks the user if they want to delete emails that match the conditions as described
		in the confirmation_str (deletion_confirmation_str attribute of the model).
		:param confirmation_str: (str) Provided by deletion_confirmation_str attribute of the model
		:param selected_email: (str) Provided by the selected_email attribute of the model
		:return: (bool) True if the user agrees with the conditions shown by the confirmation_str,
						false otherwise.
		"""
		raise NotImplementedError()

	def display_deletion_summary(self, amt_deleted: int, amt_unprocessed: int) -> None:
		"""

		:param amt_deleted: (int) The amount of emails that were deleted by the model
		:param amt_unprocessed: (int) The amount of emails that could not be preocessed
									by the model.
		:return: None
		"""
		raise NotImplementedError()

	def ask_delete_more(self) -> bool:
		"""
		Asks the user if they would like to delete more emails using new conditions.
		:return: (bool) True if the user wants to continue, False otherwise
		"""
		raise NotImplementedError()

	def display_error(self, error_msg: str):
		"""
		Displays an error message
		:param error_msg: (str) The error message
		:return:
		"""

	def print_hash_divider(self):
		"""
		Useful for the print view, can be implemented as nothing for the
		tkinter view.
		:return:
		"""
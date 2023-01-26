from src.model.cleanup_model import cleanup_model
from src.view.cleanup_view_interface import cleanup_view_interface
from src.model.cleanup_custom_exceptions import NoEmailsError, OutlookNotOpenError, DateConversionError, \
	MissingStartDate, EmptyConditionsError

class cleanup_controller:
	"""
	This class coordinates the effect of the cleanup_model
	with the view classes.
	"""
	def __init__(self, model: cleanup_model, view: cleanup_view_interface):
		self.c_model = model
		self.c_view = view

	def coordinate_set_email(self):
		"""
		Coordinates the view and model to get the email input from the user
		and set in on the model.
		:return: None
		"""
		correct_input = False

		while correct_input == False:
			try:
				user_email_choice = self.c_view.get_email_to_use_for_program(self.c_model.mailbox_options)
				user_email_choice = int(user_email_choice)
				self.c_model.select_target_mailbox(user_email_choice)
				correct_input = True
			except:
				self.c_view.display_error(f"{user_email_choice} is NOT a valid option, please try again\n")

		self.c_model.select_target_mailbox(user_email_choice)

	def coordinate_get_email_deletion_parameters(self):
		"""
		Coordinates getting email deletion parameters inputs from user and provides
		relevant info to the model and calls relevant model methods.
		:return:
		"""
		self.c_model.clear_deleting_conditions()

		self.c_view.display_message(
			"Please enter the email parameter(s) for deletion, you may leave any parameter blank",exit_after_msg=False)

		sender = self.c_view.get_target_sender()
		self.c_model.set_target_sender_email(sender)

		full_date_processing_correct = False
		while full_date_processing_correct == False:
			correct_start_date_processing = False
			while correct_start_date_processing == False:
				try:
					start_date = self.c_view.get_target_start_date()
					self.c_model.set_target_start_date(start_date)
					correct_start_date_processing = True
				except DateConversionError:
					print("Date input is incorrect, please make sure "
						  "input follows the format: month/date/year")

			correct_end_date_processing = False
			while correct_end_date_processing == False:
				try:
					end_date = self.c_view.get_target_end_date()
					self.c_model.set_target_end_date(end_date)
					correct_end_date_processing = True
				except DateConversionError:
					print("Date input is incorrect, please make sure "
						  "input follows the format: month/date/year")
				except MissingStartDate:
					print("Start date CANNOT be empty if end date is filled")
					break
			if correct_start_date_processing == correct_end_date_processing == True:
				full_date_processing_correct = True

		keyword = self.c_view.get_target_subject_keyword()
		self.c_model.set_target_subject_keyphrase(keyword)

	def coordinate_verify_deletion_params(self):
		"""
		Coordinates obtaining verification of deletion parameters from the user input
		and sets and calls proper relevant methods of the model.
		:return:
		"""
		params_confirmed = False

		while params_confirmed == False:
			try:
				self.coordinate_get_email_deletion_parameters()
				self.c_model.verify_deletion_conditions()
			except EmptyConditionsError:
				self.c_view.display_error("\n!!!! ERROR: All parameters can NOT be left EMPTY, at least 1 must be filled !!!!")
				self.c_view.print_hash_divider()
				continue
			except RuntimeError:
				self.c_view.display_error("Missing a start or end date")
				continue

			self.c_view.display_message("\n############### Please Confirm Deletion Parameters... ###############",exit_after_msg=False)
			confirmation = self.c_view.confirm_deletion_parameters(self.c_model.deletion_confirmation_str, self.c_model.selected_email)

			if confirmation == True:
				params_confirmed = True
			else:
				self.c_view.display_message("\n############### Resetting Deletion Parameters... ###############", exit_after_msg=False)

	def coordinate_deletion(self):
		"""
		Coordinates deletion of emails.
		:return:
		"""
		self.c_model.delete_emails_with_matching_conditions()
		self.c_view.display_deletion_summary(self.c_model.delete_counter, self.c_model.emails_with_missing_attributes_count)

	def run(self):
		"""
		Runs the whole program.
		:return:
		"""
		try:
			self.c_model.call_startup_methods()
		except NoEmailsError:
			error = "You need to sign in with at least one account on your Outlook Application"
			self.c_view.display_message(error, exit_after_msg=True)
		except OutlookNotOpenError:
			error = "Outlook Application must be opened before running this program"
			self.c_view.display_message(error, exit_after_msg=True)

		self.c_view.display_welcome()

		self.coordinate_set_email()
		self.c_view.print_hash_divider()

		delete_more = True

		while delete_more == True:
			self.coordinate_verify_deletion_params()
			self.c_view.display_message(f"\n############### Looking through emails loaded on outlook for MATCHING emails... PLEASE WAIT ###############", exit_after_msg=False)
			self.coordinate_deletion()
			self.c_view.print_hash_divider()
			delete_more = self.c_view.ask_delete_more()

		self.c_view.display_message(
			"\n############### Disconnecting from Outlook Application... ###############",
			exit_after_msg=False)

		self.c_view.display_message(
			"\n############### EXITING PROGRAM ############### ",
			exit_after_msg=True)

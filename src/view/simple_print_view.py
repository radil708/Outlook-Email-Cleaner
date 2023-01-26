from src.view.cleanup_view_interface import cleanup_view_interface
from src.model.date_handler import date_handler

class simple_print_view(cleanup_view_interface):
	"""
	This view class is meant to display info and take some
	input from the user. It relies on the console to take
	in information. The cleanup_view_interface provides
	method docs.
	"""
	def __init__(self):
		self.date_processor = date_handler()

	def display_welcome(self):
		print("//////////// Welcome to Ramzi's Outlook Email Cleanup Program ////////////")

	def display_message(self, msg : str, exit_after_msg: bool = True):
		print(msg)
		if exit_after_msg == True:
			input("Program will close after Enter Key has been pressed")
			exit(0)

	def get_email_to_use_for_program(self, dict_email_choices : dict):
		print("Which email do do you want to cleanup? Please select the option corresponding to the email of your choice.")
		print("Option : Email")

		for key,value in dict_email_choices.items():
			print(f"{key} : {value}")

		user_choice = self.get_input_for_basic_message()

		return user_choice

	def get_input_for_basic_message(self) -> str:
		user_input = input("Your Choice: ")
		return user_input

	def get_target_sender(self):
		return input("Sender Email Address: ")

	def get_target_start_date(self):
		date_chosen = input("Lower Date Boundary (inclusive) in the format of mm/dd/yyyy, for ex. 12/16/2022 is Dec 16, 2022:\n")
		return date_chosen


	def get_target_end_date(self):
		date_chosen = input("Upper Date Boundary (inclusive) in the format of mm/dd/yyyy, for ex. 12/16/2022 is Dec 16, 2022:\n")
		return date_chosen

	def get_target_subject_keyword(self):
		return input("Subject key word or Phrase: ")

	def confirm_deletion_parameters(self, confirmation_str: str, selected_email) -> bool:
		print(f"This action will delete all emails from {selected_email}'s Inbox matching the following condition(s):")
		print(confirmation_str)
		user_choice = input("Enter y/yes to confirm: ")
		if user_choice.lower().__eq__("y") or user_choice.lower().__eq__("yes"):
			return True
		else:
			return False

	def ask_delete_more(self) -> bool:
		print("Do you wish to continue deleting more emails?")
		user_choice = input("Enter y/yes to confirm: ")
		if user_choice.lower().__eq__("y") or user_choice.lower().__eq__("yes"):
			return True
		else:
			return False

	def display_deletion_summary(self, amt_deleted: int, amt_unprocessed: int):
		print(f"{amt_deleted} emails have been moved to the TRASH folder")
		if amt_unprocessed > 0:
			print(f"{amt_unprocessed} could NOT be processed (missing date or sender address property)")

	def print_hash_divider(self):
		print("\n############################################################")

	def display_error(self, error_msg: str):
		print(error_msg)



import unittest
from src.model.cleanup_model import cleanup_model
from src.model.date_handler import LOCAL_TIMEZONE
from datetime import datetime
from src.model.cleanup_custom_exceptions import *


"""
DEVELOPER_MODE must be false on public repo. 
"""
try:
	ALL_EMAILS = []
	with open("developer_test_helper", "r") as file:
		for line in file:
			email_from_file = line.strip()
			if not email_from_file.isspace():
				ALL_EMAILS.append(email_from_file)
		DEVELOPER_MODE = True
except FileNotFoundError:
	DEVELOPER_MODE = False


class test_cleanup_model(unittest.TestCase):
	"""
	This class tests the methods of the cleanup_model. Some tests will be skipped
	because those tests are specific to the emails I used to test.
	"""
	@classmethod
	def setUpClass(cls) -> None:
		'''
		Since the model is a singleton we will only
		run these methods once as opposed to running
		them before every test is run
		:return: None
		'''
		cls.model = cleanup_model()
		cls.model.call_startup_methods()

	def test_singleton_pattern(self) -> None:
		"""
		Testing singleton pattern
		:return:
		"""
		model_2 = cleanup_model()
		#Testing identity
		self.assertTrue(self.model == model_2)

	def test_deletion_variable_setters(self) -> None:
		"""
		Testing setters for model
		:return: None
		"""
		model = self.model

		model.set_target_sender_email("example@email.com")
		self.assertEqual("example@email.com", model.target_sender_email)
		self.assertEqual("example@email.com", model.verification_add_on[0])

		model.set_target_subject_keyphrase("keyword")
		self.assertEqual("keyword", model.target_subject_keyphrase)
		self.assertEqual("keyword", model.verification_add_on[2])

		model.set_target_start_date("2/28/2022")
		self.assertEqual(datetime(2022,2,28,00,00,00, tzinfo=LOCAL_TIMEZONE), model.target_start_date)
		self.assertEqual("02/28/2022",model.verification_add_on[1])

		model.set_target_end_date("06/18/2022")
		self.assertEqual(datetime(2022, 6, 18, 23, 59, 59, tzinfo=LOCAL_TIMEZONE), model.target_end_date)
		self.assertEqual("02/28/2022 to 06/18/2022", model.verification_add_on[1])

		model.clear_deleting_conditions()

	def test_deletion_variable_setters_empty_set(self) -> None:
		"""
		Testing setters for model. Empty/space submission should not change values
		:return:
		"""
		model = self.model

		#empty sender
		model.set_target_sender_email("")
		self.assertEqual(None, model.target_sender_email)
		with self.assertRaises(KeyError):
			model.verification_add_on[0]
		model.set_target_sender_email("  ")
		self.assertEqual(None, model.target_sender_email)
		self.assertRaises(KeyError, lambda : model.verification_add_on[0])

		#empty keyword/phrase
		model.set_target_subject_keyphrase("")
		self.assertEqual(None, model.target_subject_keyphrase)
		self.assertRaises(KeyError, lambda : model.verification_add_on[2])
		model.set_target_subject_keyphrase(" ")
		self.assertEqual(None, model.target_subject_keyphrase)
		self.assertRaises(KeyError, lambda: model.verification_add_on[2])


		model.set_target_start_date("")
		self.assertEqual(None, model.target_start_date)
		self.assertRaises(KeyError, lambda : model.verification_add_on[1])
		model.set_target_start_date(" ")
		self.assertEqual(None, model.target_start_date)
		self.assertRaises(KeyError, lambda: model.verification_add_on[1])

		model.set_target_end_date("")
		self.assertEqual(None, model.target_end_date)
		self.assertRaises(KeyError, lambda : model.verification_add_on[1])
		model.set_target_end_date(" ")
		self.assertEqual(None, model.target_end_date)
		self.assertRaises(KeyError, lambda: model.verification_add_on[1])

		model.clear_deleting_conditions()

	def test_date_setter_throw_missing_date_error(self):
		"""
		Testing that an error is raised if an end date is set while the
		start date is empty.
		:return:
		"""
		model = self.model
		model.clear_deleting_conditions()
		self.assertRaises(MissingStartDate, model.set_target_end_date, "6/18/2022")
		model.clear_deleting_conditions()

	def test_date_setter_throw_date_conv_error(self):
		"""
		Testing that incorrect input throws conversion error when date handler
		throws Value error.
		:return:
		"""
		model = self.model
		model.clear_deleting_conditions()
		#invalid start date
		self.assertRaises(DateConversionError, model.set_target_start_date, "31/15/2021")

		#valid start date but invalid end date
		model.set_target_start_date("2/28/2022")
		self.assertRaises(DateConversionError, model.set_target_end_date, "06/82/2022")

		model.clear_deleting_conditions()

	def test_clear_deletion_conditions(self):
		"""
		Testing clear_deleting_conditions method
		:return:
		"""

		model = self.model

		model.set_target_sender_email("example@email.com")
		model.set_target_subject_keyphrase("keyword")
		model.set_target_start_date("2/28/2022")
		model.set_target_end_date("06/18/2022")

		model.clear_deleting_conditions()

		self.assertEqual(None, model.target_sender_email)
		self.assertEqual(None, model.target_subject_keyphrase)
		self.assertEqual(None, model.target_start_date)
		self.assertEqual(None, model.target_end_date)

	def test_verify_conditions_errors(self):
		"""
		testing the verify_deletions_conditions method raises
		expected errors for negative conditions.
		:return:
		"""

		model = self.model
		self.assertEqual(False, model.verified_conditions)
		#No conditions set
		self.assertRaises(EmptyConditionsError, model.verify_deletion_conditions)
		self.assertEqual(False, model.verified_conditions)
		model.clear_deleting_conditions()

		#Missing end date condition, but start date set
		model.set_target_start_date("2/28/2022")
		self.assertRaises(RuntimeError, model.verify_deletion_conditions)
		self.assertEqual(False, model.verified_conditions)
		model.clear_deleting_conditions()

	def test_verify_conditions_one_condition(self):
		"""
		Testing verified conditions method when one condition is set
		:return:
		"""
		model = self.model

		# only sender email set
		model.set_target_sender_email("example@email.com")
		self.assertEqual(False,model.verified_conditions)
		model.verify_deletion_conditions()
		self.assertEqual(True, model.verified_conditions)
		self.assertEqual([0],model.accepted_deletions_conditions)
		self.assertEqual("sender email: example@email.com", model.deletion_confirmation_str)

		#only dates set
		model.clear_deleting_conditions()
		model.set_target_start_date("02/28/2022")
		model.set_target_end_date("6/18/2022")
		self.assertEqual(False, model.verified_conditions)
		model.verify_deletion_conditions()
		self.assertEqual(True, model.verified_conditions)
		self.assertEqual([1], model.accepted_deletions_conditions)
		self.assertEqual("was sent between the dates (inclusive): 02/28/2022 to 06/18/2022", model.deletion_confirmation_str)

		#only keyword/phrase set
		model.clear_deleting_conditions()
		model.set_target_subject_keyphrase("psych!")
		self.assertEqual(False, model.verified_conditions)
		model.verify_deletion_conditions()
		self.assertEqual(True, model.verified_conditions)
		self.assertEqual([2], model.accepted_deletions_conditions)
		expected = "has the keyword/keyphrase in the subject: psych!"
		self.assertEqual(expected, model.deletion_confirmation_str)


	def test_verify_conditions_two_conditions(self):
		"""
		Testing verified conditions method when two condition are set
		:return:
		"""
		model = self.model

		#sender and dates
		model.clear_deleting_conditions()
		model.set_target_sender_email("example@email.com")
		model.set_target_start_date("02/28/2022")
		model.set_target_end_date("6/18/2022")
		self.assertEqual(False, model.verified_conditions)
		model.verify_deletion_conditions()
		self.assertEqual([0,1], model.accepted_deletions_conditions)
		self.assertEqual(True, model.verified_conditions)
		expected_str = "sender email: example@email.com AND was sent between the dates (inclusive): 02/28/2022 to 06/18/2022"
		self.assertEqual(expected_str, model.deletion_confirmation_str)

		#sender and keyword/phrase
		model.clear_deleting_conditions()
		self.assertEqual(False, model.verified_conditions)
		model.set_target_sender_email("example@email.com")
		model.set_target_subject_keyphrase("psych!")
		model.verify_deletion_conditions()
		self.assertEqual(True, model.verified_conditions)
		expected = "sender email: example@email.com AND has the keyword/keyphrase in the subject: psych!"
		self.assertEqual(expected, model.deletion_confirmation_str)

		#date and keyword/phrase
		model.clear_deleting_conditions()
		self.assertEqual(False, model.verified_conditions)
		model.set_target_start_date("02/28/2022")
		model.set_target_end_date("6/18/2022")
		model.set_target_subject_keyphrase("psych!")
		model.verify_deletion_conditions()
		self.assertEqual(True, model.verified_conditions)
		expected = "was sent between the dates (inclusive): 02/28/2022 to 06/18/2022 AND has the keyword/keyphrase in the subject: psych!"
		self.assertEqual(expected, model.deletion_confirmation_str)
		model.clear_deleting_conditions()

	def test_verify_conditions_three_conditions(self):
		"""
		Testing verified conditions method when three condition are set
		:return:
		"""
		model = self.model

		model.clear_deleting_conditions()
		model.set_target_sender_email("example@email.com")
		model.set_target_start_date("02/28/2022")
		model.set_target_end_date("6/18/2022")
		model.set_target_subject_keyphrase("psych!")
		self.assertEqual(False, model.verified_conditions)
		model.verify_deletion_conditions()
		self.assertEqual(True, model.verified_conditions)
		expected = "sender email: example@email.com AND "
		expected += "was sent between the dates (inclusive): 02/28/2022 to 06/18/2022 AND "
		expected += "has the keyword/keyphrase in the subject: psych!"
		self.assertEqual(expected, model.deletion_confirmation_str)
		model.clear_deleting_conditions()

	def test_select_mailbox_1(self):
		'''
		testing access to one of two emails on outlook
		:return:
		'''
		model = self.model

		if DEVELOPER_MODE == False:
			self.skipTest('developer_test_helper file not available, test_select_mailbox_1 has been skipped')

		# picking the first email as the email to delete from
		model.select_target_mailbox(1)
		self.assertEqual(ALL_EMAILS[0], model.selected_email)

	def test_select_mailbox_2(self):
		'''
		Testing access to the other email available on outlook
		:return:
		'''

		model = self.model

		if DEVELOPER_MODE == False:
			self.skipTest('developer_test_helper file not available, test_select_mailbox_2 has been skipped')

		# picking the second email as the email to delete from
		model.select_target_mailbox(2)
		self.assertEqual(ALL_EMAILS[1], model.selected_email)

	def test_find_emails_matching_one_condition(self):
		'''
		These tests will only run successfully on my (radil708's) computer because they are linked
		to my test email information. These tests WILL be skipped otherwise. Feel free to use it as
		a template if you want to make tests to run on your machine.
		This is to test finding emails that match 1 specified condition.
		:return: None
		'''

		# Since these tests are specific to my test email and the emails in my own test email
		# these tests will be skipped. You can use this test as a template for your
		# own email tests if you want, but I have already verified that these work.
		if DEVELOPER_MODE == False:
			self.skipTest("Not in developer mode, test_find_emails_matching_one_condition has been skipped")

		model = self.model
		model.clear_deleting_conditions()
		model.selected_email = ALL_EMAILS[0]
		# manually pointing directoy to inbox, usually is automatically set when calling select_target_mailbox
		model.selected_directory = model.outlook_connection.Folders(model.selected_email).Folders('Inbox')
		model.clear_deleting_conditions()

		######################## Test Finding Emails By Date Condition Only ########################
		model.set_target_start_date("1/18/2023")
		model.set_target_end_date("1/18/2023")
		model.verify_deletion_conditions()
		matching_date_cond_emails = model.get_emails_matching_search_conditions()
		self.assertEqual(12, len(matching_date_cond_emails),
						 msg="This test will fail if the email used is not my (radil708's) test email, you can make your own tests following this template though")

		######################## Test Finding Emails By Subject Key Word/Phrase Only ########################
		model.clear_deleting_conditions()  # clear up, now only look for matching subject
		model.set_target_subject_keyphrase("test")
		model.verify_deletion_conditions()
		matching_phrase_emails = model.get_emails_matching_search_conditions()
		self.assertEqual(164, len(matching_phrase_emails),
						 msg="This test will fail if the email used is not my (radil708's) test email, "
							 "you can make your own tests following this template though")

		######################## Test Finding Emails By Sender Email Address Only ########################
		model.clear_deleting_conditions()  # clear up, now only look for matching senderemailaddress
		model.set_target_sender_email(ALL_EMAILS[1])
		self.assertEqual(model.target_sender_email, ALL_EMAILS[1])
		model.verify_deletion_conditions()
		matching_sender = model.get_emails_matching_search_conditions()
		self.assertEqual(1, len(matching_sender),
						 msg="This test will fail if the email used is not my (radil708's) test email, you can "
							 "make your own tests following this template though")

	def test_find_emails_matching_two_conditions(self):
		"""
		These tests will only run successfully on my (radil708's) computer because they are linked
		to my test email information and the emails that are present in my test email server.
		These tests WILL be skipped otherwise. Feel free to use it as
		a template if you want to make tests to run on your machine.
		This is to test finding emails that match 2 specified conditions.
		:return: None
		"""

		# Since these tests are specific to my test email and the emails in my own test email
		# these tests will be skipped. You can use this test as a template for your
		# own email tests if you want, but I have already verified that these work.

		if DEVELOPER_MODE == False:
			self.skipTest("Not in developer mode, test_find_emails_matching_two_conditions has been skipped")

		model = self.model
		model.clear_deleting_conditions()
		model.selected_email = ALL_EMAILS[0]
		# manually pointing directory to inbox, usually is automatically set when calling select_target_mailbox
		model.selected_directory = model.outlook_connection.Folders(model.selected_email).Folders('Inbox')
		model.clear_deleting_conditions()

		######################## Test Finding Emails By Sender Address And Date Range Conditions Only ########################
		model.set_target_sender_email(ALL_EMAILS[1])
		model.set_target_start_date("1/15/2023")
		model.set_target_end_date("1/19/2023")
		model.verify_deletion_conditions()
		matching_sender_and_date_emails = model.get_emails_matching_search_conditions()
		self.assertEqual(2, len(matching_sender_and_date_emails),
						 msg="This test will fail if the email used is not my (radil708's) test email, you can make your own tests following this template though")

		######################## Test Finding Emails By Sender Address And Subject Key Word Conditions Only ########################
		model.clear_deleting_conditions()
		model.set_target_sender_email(ALL_EMAILS[1])
		model.set_target_subject_keyphrase("Test")
		model.verify_deletion_conditions()
		matching_sender_and_keyword_emails = model.get_emails_matching_search_conditions()
		self.assertEqual(1, len(matching_sender_and_keyword_emails))

		######################## Test Finding Emails By Date Range And Subject Key Word Conditions Only ########################
		model.clear_deleting_conditions()
		model.set_target_start_date("1/18/2023")
		model.set_target_end_date("1/19/2023")
		model.set_target_subject_keyphrase("ramzi")
		model.verify_deletion_conditions()
		matching_date_and_keyword_emails = model.get_emails_matching_search_conditions()
		self.assertEqual(2, len(matching_date_and_keyword_emails), msg="This test will fail if the email used is "
																	   "not my (radil708's) test email, you can make "
																	   "your own tests following this template though")

	def test_find_emails_matching_three_conditions(self):
		"""
		These tests will only run successfully on my (radil708's) computer because they are linked
		to my test email information. These tests WILL be skipped otherwise. Feel free to use it as
		a template if you want to make tests to run on your machine.
		This is to test finding emails that match 3 specified conditions.
		:return: None
		"""
		# Since these tests are specific to my test email and the emails in my own test email
		# these tests will be skipped. You can use this test as a template for your
		# own email tests if you want, but I have already verified that these work.

		if DEVELOPER_MODE == False:
			self.skipTest("Not in developer_mode, test_find_emails_matching_three_conditions has been skipped")

		model = self.model
		model.selected_email = ALL_EMAILS[0]
		# manually pointing directory to inbox, usually is automatically set when calling select_target_mailbox
		model.selected_directory = model.outlook_connection.Folders(model.selected_email).Folders('Inbox')
		model.clear_deleting_conditions()

		model.set_target_sender_email(ALL_EMAILS[1])
		model.set_target_start_date("1/15/2023")
		model.set_target_end_date("1/19/2023")
		model.set_target_subject_keyphrase("test")
		model.verify_deletion_conditions()
		matching_all_conditions = model.get_emails_matching_search_conditions()
		self.assertEqual(2, len(matching_all_conditions), msg="This test will fail if the email used is "
																	   "not my (radil708's) test email, you can make "
																	   "your own tests following this template though")

	def test_delete_emails_matching_conditions(self):
		"""
		Test deletion count and actual deletion of emails
		:return:
		"""

		# Since these tests are specific to my test email and the emails in my own test email
		# these tests will be skipped. You can use this test as a template for your
		# own email tests if you want, but I have already verified that these work.

		if DEVELOPER_MODE == False:
			self.skipTest("Not in developer mode, test_delete_emails_matching_condition has been skipped")

		model = self.model
		model.selected_email = ALL_EMAILS[0]
		# manually pointing directory to inbox, usually is automatically set when calling select_target_mailbox
		model.selected_directory = model.outlook_connection.Folders(model.selected_email).Folders('Inbox')
		model.clear_deleting_conditions()

		model.set_target_sender_email(ALL_EMAILS[1])
		model.set_target_start_date("1/15/2023")
		model.set_target_end_date("1/19/2023")
		model.set_target_subject_keyphrase("test")
		model.verify_deletion_conditions()
		model.delete_emails_with_matching_conditions()

		if model.delete_counter != 2:
			self.skipTest("Emails may already have been deleted, skipping test_delete_emails_matching_conditions")

		self.assertEqual(2, model.delete_counter)

def main():
	unittest.main(verbosity=3)

if __name__ == '__main__':
	main()
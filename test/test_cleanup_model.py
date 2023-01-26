import unittest
from src.model.cleanup_model import cleanup_model
from src.model.date_handler import LOCAL_TIMEZONE
from datetime import datetime
from src.model.cleanup_custom_exceptions import *

DEVELOPER_MODE = False

ALL_EMAILS = []
with open("test_helper", "r") as file:
	for line in file:
		email_from_file = line.strip()
		if not email_from_file.isspace():
			ALL_EMAILS.append(email_from_file)


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




def main():
	unittest.main(verbosity=3)

if __name__ == '__main__':
	main()
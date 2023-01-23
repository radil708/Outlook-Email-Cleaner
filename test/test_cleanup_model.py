import unittest
from src.model.cleanup_model import cleanup_model
from src.model.date_handler import LOCAL_TIMEZONE
from datetime import datetime
from src.model.cleanup_custom_exceptions import *

class test_cleanup_model(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		'''
		Since the model is a singleton we will only
		run these methods once as opposed to running
		them before every test is run
		:return: None
		'''
		cls.model = cleanup_model()

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

	def test_date_setter_throw_missing_date_error(self):
		"""
		Testing that an error is raised if an end date is set while the
		start date is empty.
		:return:
		"""
		model = self.model
		model.clear_deleting_conditions()
		self.assertRaises(MissingStartDate, model.set_target_end_date, "6/18/2022")

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

def main():
	unittest.main(verbosity=3)

if __name__ == '__main__':
	main()
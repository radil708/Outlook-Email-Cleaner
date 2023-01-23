import unittest
from src.model.date_handler import date_handler, LOCAL_TIMEZONE
from datetime import datetime
"""
This file tests the methods of the date_handler class.
"""

class test_date_handler(unittest.TestCase):

	def test_singleton_patter(self):
		"""
		Testing singelton pattern for date_handler class
		:return: None
		"""
		handler_1 = date_handler()
		handler_2 = date_handler()

		#test for identity
		self.assertTrue(handler_1 == handler_2)

	def test_proc_date_str(self):
		'''
		Test string processing when input is all correct
		:return: None
		'''
		handler = date_handler()
		example_date = '02/28/2001'
		processed = handler.process_str_date(example_date)
		self.assertEqual([2,28,2001], processed)

	def test_proc_date_negative_no_paren(self):
		'''
		Test string processing when input is not correct.
		> no parenthesis present in the string
		This should raise Value error
		:return: None
		'''

		handler = date_handler()
		no_paren_date = '02282001'

		self.assertRaises(ValueError,handler.process_str_date,no_paren_date)

		hyphen_date = '02-28-2001'
		self.assertRaises(ValueError, handler.process_str_date,hyphen_date)

	def test_proc_date_negative_string_contains_words(self):
		'''
		Test string processing when input is not correct.
		> word is present where month or day or year should be
		This should raise Value error
		:return: None
		'''

		handler = date_handler()

		invalid_month = "word/28/2001"
		invalid_day = "02/word/2001"
		invalid_year = "02/28/word"

		self.assertRaises(ValueError, handler.process_str_date, invalid_month)
		self.assertRaises(ValueError, handler.process_str_date, invalid_day)
		self.assertRaises(ValueError, handler.process_str_date, invalid_year)
	def test_proc_date_negative_invalid_month_input(self):
		'''
		Test string processing when input is not correct.
		> month value is greater than 12 or less than 1
		This should raise Value error
		:return: None
		'''

		handler = date_handler()
		invalid_month_high = '13/28/2001'
		invalid_month_low = '0/28/2001'

		self.assertRaises(ValueError, handler.process_str_date, invalid_month_high)
		self.assertRaises(ValueError, handler.process_str_date, invalid_month_low)

	def test_proc_date_negative_invalid_day(self):
		'''
		Test string processing when input is not correct.
		> day value is greater than 31 or less than 1
		This should raise Value error
		:return: None
		'''

		handler = date_handler()
		invalid_day_high = '02/0/2001'
		invalid_day_low = '02/32/2001'

		self.assertRaises(ValueError, handler.process_str_date, invalid_day_high)
		self.assertRaises(ValueError, handler.process_str_date, invalid_day_low)

	def test_proc_date_negative_invalid_year(self):
		'''
		Test string processing when input is not correct.
		> year value is less than 4 characters
		This should raise Value error
		:return: None
		'''

		handler = date_handler()
		self.assertRaises(ValueError, handler.process_str_date, '02/28/10')
		self.assertRaises(ValueError, handler.process_str_date, '02/28/20001')

	def test_convert_list_into_datetime(self):
		'''
		testing convert_list_into_datetime function
		> should create a datetime with accurate date and time at 00:00:00
		:return: None
		'''

		handler = date_handler()
		valid_input = '2/28/2001'
		valid_list_1 = handler.process_str_date(valid_input)
		dt1 = handler.convert_list_into_datetime(valid_list_1)

		self.assertEqual(datetime(2001,2,28,00,00,00, tzinfo=LOCAL_TIMEZONE), dt1)

		dt2 = handler.convert_list_into_datetime(valid_list_1, endtime=True)

		self.assertEqual(datetime(2001,2,28,23,59,59, tzinfo=LOCAL_TIMEZONE), dt2)

def main():
	unittest.main(verbosity=3)

if __name__ == '__main__':
	main()
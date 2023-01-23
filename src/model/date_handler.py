from datetime import datetime, timezone

LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo

'''
This is a helper/utility class. It handles a lot of functionality regarding dates
for the model.
'''
class date_handler():

	def __new__(cls):
		"""
		This is used to enforce the singleton pattern. If a date_handler instance
		has already been created, then it will return the instance and not
		a new instance, otherwise it will create a new instance of cleanup_model
		"""
		if not hasattr(cls, 'instance'):
			cls.instance = super(date_handler, cls).__new__(cls)
		return cls.instance

	def process_str_date(self, date_string: str) -> list:
		"""
        This method converts a string representation of a date in the format of month/day/year
        and returns a list of ints representing that year -> [month, day, year]
        :param date_string: (str) a string representation of the date. Value errors will be raised
        if any of the following conditions occur:
         - format is not followed i.e. month/day/year with "/" being required
         - if the month value is < 0 or > 12
         - if the day value is < 0 or > 31
         - if the year is not composed of 4 digits
         - if any value is composed of a string
         - if any value is missing ex. -> 12/05 does not contain a year value so an error will be raised
         - if there are too many values ex. 12/05/2010/10 has an extra "10" at the end
        :return: (list) a list of ints representing that year -> [month, day, year]
        """

		# Check if format has been followed
		if "/" not in date_string:
			raise ValueError("There is no '/' separator between dates")

		# Remove any empty leading and lagging spaces
		date_string = date_string.strip()
		# Remove any empty spaces in between string
		date_string = date_string.replace(" ", "")
		# Replace "/" with " " so that the string can be split by spaces
		date_split = date_string.split("/")

		# Check if there are 3 values and if the year is composed of 4 digits
		if len(date_split) <= 2:
			raise ValueError("One or more date values (month, date, or time) is missing")
		elif len(date_split) > 3:  # list should only contain 3 elements
			raise ValueError("There are more than 3 date values entered, please check date input")
		elif len(date_split[2]) != 4:  # last element should contain 4 chars
			raise ValueError("The year must contain 4 digits i.e. '2005' NOT '05'")

		date_list_int = []

		# will raise value error if any str element cannot be converted to int
		for each in date_split:
			date_list_int.append(int(each))

		# Check if month value is valid
		if date_list_int[0] < 1 or date_list_int[0] > 12:
			raise ValueError("The month value cannot be greater than 12 or less than 1")

		# Check if date value is valid
		if date_list_int[1] < 1 or date_list_int[1] > 31:
			raise ValueError("The day value cannot be less than 0 or greater than 31")

		return date_list_int

	def convert_list_into_datetime(self, date_list_int: list, endtime: bool = False) -> datetime:
		'''
		Helper method to convert output of process_str_date into a datetime object.
		:param date_list_int: (list) list of ints in the format of [month, day, year]. This
		input should be the output of the function: process_str_date
		:param endtime: (bool) if true, outputs a datetime with time at 11:59:59 PM, else
		time is set 00:00:00 AM
		:return:
		'''

		year = date_list_int[2]
		day = date_list_int[1]
		month = date_list_int[0]

		if endtime == True:
			# datetime(year, month, day, hour, minute, second, microsecond)
			return datetime(year, month, day, hour=23, minute=59, second=59,tzinfo=LOCAL_TIMEZONE)
		else:
			return datetime(year, month, day, hour=0, minute=0, second=0,tzinfo=LOCAL_TIMEZONE)

	def is_between_dates(self, lower_bound: datetime, upper_bound: datetime, target_date: datetime) -> bool:
		f'''
		Returns true or false, depending on whether the target_date is between the upper
		and lower_bound dates
		:param lower_bound: (datetime) lower boundary date
		:param upper_bound: (datetime) upper boundary date
		:param target_date: (datetime) target date
		:return: (bool) true if target date is between lower and upper bound (inclusive),
					false otherwise
		'''

		return lower_bound <= target_date <= upper_bound

	def convert_sent_on_datetime(self, msg):
		"""
		Converts the SentOn property of an email item method to a date time object.
		This is a helper function.
		:param msg: (win32com.client.CDispatch) the email item whose sentOn property we want to extract
		the date from
		:return: (datetime) the datetime representation of the date an email was sent
		"""

		return datetime.fromtimestamp(msg.SentOn.timestamp(), msg.SentOn.tzinfo)
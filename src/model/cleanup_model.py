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
    self.target_sender_email = None  # string
    self.target_start_date = None  # datetime obj
    self.target_end_date = None  # datetime obj
    self.target_subject_keyphrase = None  # string
    self.target_sender_name = None  # string

    """
		NOTE*: target_sender_name and target_sender_email are not the same. For example,
		an email can have the sender be LinkedIn but that same sender could be linked
		to multiple email addresses like linkedinjobs@linkedin.com & linkedinnotifications@linkedin.com
		for example. So tageting by the sender would remove the need to search for two 
		different addresses
		"""

    # if adding new conditions, new matching function must be added to the end of this list
    self.all_matching_functions = [self.is_match_for_sender_email_address,
                                   self.is_within_date_range,
                                   self.is_match_for_subject,
                                   self.is_match_for_sender_name]
    self.delete_counter = 0
    self.emails_with_missing_attributes_count = 0

    ###################### Verification Related Varibales ######################
    # dictionary used to hold information for confirmation string question
    # key: 0, value : target_sender_email
    # key: 1, value : target_start_date to target_end_date
    # key: 2, value : target_subject_key_phrase
    # key: 3, value : target_sender_name
    self.verification_add_on = {}

    self.accepted_deletions_conditions = []  # contains indexes corresponding to conditions to check

    # if adding new conditions, new keys must be added with appropriate value and verification must be modified
    self.verification_phrase_prefixes = {0: "sender email:",
                                         1: "was sent between the dates (inclusive):",
                                         2: "has the keyword/keyphrase in the subject:",
                                         3: "sender name:"}
    self.deletion_confirmation_str = ""
    self.verified_conditions = False  # Must be set to true before being able to look for matching emails

    ###################### Outlook Application Related Variables ######################
    self.com_obj = None  # stores COM
    self.outlook_connection = None  # stores namespace
    self.all_mailboxes = None  # helper variable to mailbox_options attribute
    self.mailbox_options = {}  # all available emails signed in on in outlook application
    self.selected_email = None  # email whose inbox items will be deleted
    self.selected_directory = None  # access to the inbox folder
    self.chosen_mailbox_option = None

  def __new__(cls):
    """
		This is used to enforce the singleton pattern. If a cleanup_model instance
		has already been created, then it will return the instance and not
		a new instance, otherwise it will create a new instance of cleanup_model
		"""
    if not hasattr(cls, 'instance'):
      cls.instance = super(cleanup_model, cls).__new__(cls)
    return cls.instance

  def set_target_sender_email(self, email: str) -> None:
    '''
		Set target_sender_email attribute if input is not empty. This should
		only be 1 specific sender.
		:param email: (str) sender email target
		:return: None
		'''
    if email.isspace() or email == "":
      return
    else:
      self.target_sender_email = email
      self.verification_add_on[0] = email

  def set_target_sender_name(self, name: str) -> None:
    '''
    Set target_sender_name attribute if input is not empty. This should
		only be 1 specific sender.
    :param name: (str) sender email name
    :return:  None
    '''

    if name.isspace() or name == "":
      return
    else:
      self.target_sender_name = name
      self.verification_add_on[3] = name

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
    # if empty date input then don't do anything
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
    # if empty date input
    if date.isspace() or date == "":
      # check that start date is also empty
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

    self.target_end_date = self.date_utility.convert_list_into_datetime(date_list_end, endtime=True)
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
    self.accepted_deletions_conditions = []
    self.deletion_confirmation_str = ""
    self.verified_conditions = False
    self.delete_counter = 0

  def verify_deletion_conditions(self):
    '''
		Checks that some deletion conditions have been set and formatted correctly.
		Raises a custom EmptyConditionsError if no attributes have been set.
		This method MUST be called before any deletion occurs.
		:return:
		'''

    # Check that at least one of the three conditions have been set
    if self.target_sender_email is None and self.target_start_date is None \
      and self.target_end_date is None and self.target_subject_keyphrase is None\
      and self.target_sender_name is None:
      raise EmptyConditionsError

    # Apply All matching conditions
    if self.target_sender_email is not None:
      self.accepted_deletions_conditions.append(0)  # represents condition index in self.all_matching_functions
    if self.target_start_date is not None and self.target_end_date is not None:
      self.accepted_deletions_conditions.append(1)  # represents condition index in self.all_matching_functions
    if self.target_subject_keyphrase is not None:
      self.accepted_deletions_conditions.append(2)  # represents condition index in self.all_matching_functions

    # Check that if start date is sets, that end date is also set
    if self.target_start_date is not None and self.target_end_date is None:
      raise RuntimeError("Missing target end date")
    elif self.target_start_date is None and self.target_end_date is not None:
      raise RuntimeError("Missing target start date")

    # string to ask for confirmation of settings
    for each_index in self.accepted_deletions_conditions:
      self.deletion_confirmation_str += self.verification_phrase_prefixes[each_index] + " " + \
                                        self.verification_add_on[each_index]
      self.deletion_confirmation_str += " AND "

    self.deletion_confirmation_str = self.deletion_confirmation_str.rstrip(" AND")
    self.verified_conditions = True

  def connect_to_outlook(self) -> None:
    """
		Sets com_obj and outlook_connection attributes. MUST be run before
		set_all_mailboxes.
		:return: None
		"""
    # create an instance of COM object
    # COM object allows us to interact with other programs
    self.com_obj = client.Dispatch("Outlook.Application")

    # need to make an object that can interact with folders in the outlook
    # MAPI means Message Application Program Interface, this only works for windows
    try:
      self.outlook_connection = self.com_obj.GetNameSpace('MAPI')
    except AttributeError:
      raise OutlookNotOpenError()

  def set_all_mailboxes_options(self):
    '''
		Sets the all_mailboxes attribute. Can only run after connect_to_outlook
		has been run
		:return: None
		'''
    # mailboxes include email addresses, some folders, calendars etc.
    list_mailboxes = []

    for mailbox in self.outlook_connection.Folders:
      # filter out non-emails
      if '@' in mailbox.Name:
        list_mailboxes.append(mailbox.Name)

    self.all_mailboxes = list_mailboxes

    # set up options attribute
    for i in range(len(self.all_mailboxes)):
      self.mailbox_options[i + 1] = self.all_mailboxes[i]

    if len(self.all_mailboxes) == 0:
      raise NoEmailsError()

  def call_startup_methods(self):
    """
		Methods that connect the model to the Outlook Application
		:return:
		"""
    try:
      self.connect_to_outlook()
    except:
      raise RuntimeError("Could not connect to outlook, make sure Outlook is Open")
    self.set_all_mailboxes_options()

  def select_target_mailbox(self, input: int):
    '''
		:param input: {int} the key of the corresponding chosen email. All valid
		options are the keys of the attribute self.mailbox_options dictionary
		:return: None
		'''

    self.chosen_mailbox_option = input

    if input not in list(self.mailbox_options.keys()):
      raise ValueError(f"Selected Option {input} not valid")

    self.selected_email = self.mailbox_options[input]

    # by default we will pick only the 'Inbox' folder
    self.selected_directory = self.outlook_connection.Folders(self.selected_email).Folders('Inbox')

  def get_all_emails_from_directory(self):
    '''
		Returns all emails from current inbox of email
		:return:
		'''
    if self.selected_directory == None:
      raise RuntimeError(
        'select_target_mailbox must be called before calling get_all_emails_from_directory in model')
    return self.selected_directory.Items

  def is_match_for_subject(self, email_item: client.CDispatch):
    """
		Checks if a an email's subject contains the keyword/phrase
		:param email_item: (win32com.client.CDispatch) an email item from outlook
		:return:
		"""
    # check if target keyphrase is in the email's subject
    return self.target_subject_keyphrase.lower() in email_item.Subject.lower()

  def is_within_date_range(self, email_item: client.CDispatch):
    """
		Check's if an email's sent date is within the date range deletion condition
		:param email_item: (win32com.client.CDispatch) an email item from outlook
		:return:
		"""
    # check if email date is in between target start and end dates
    email_date = self.date_utility.convert_sent_on_datetime(email_item)
    return self.date_utility.is_between_dates(lower_bound=self.target_start_date,
                                              upper_bound=self.target_end_date,
                                              target_date=email_date)

  def is_match_for_sender_email_address(self, email_item: client.CDispatch):
    """
		Check's if an email's sender email address matches the sender email address deletion condition
		This will not match for an email that was sent by multiple people.
		It can only be 1 sender.
		:param email_item: (win32com.client.CDispatch) an email item from outlook
		:return:
		"""
    # check if sender email address matches

    sender_address = email_item.SenderEmailAddress

    return self.target_sender_email.lower().__eq__(sender_address.lower())

  def is_match_for_sender_name(self, email_item: client.CDispatch):
    """
		Checks if the name of the sender (DIFFERENT FROM THE ADDRESS) matches the sender name
		deletion condition. This will not match for an email that was sent by multiple people.
		:param email_item:  (win32xom.client.CDispatch) an email item from outlook
		:return:
		"""
    sender_name = email_item.SenderName

    return self.self.target_sender_name.lower().__eq__(sender_name)

  def get_emails_matching_search_conditions(self):
    """
		Returns a list of items from the inbox with properties
		matching the deletion conditions.
		Helper method to delete_emails_with_matching_conditions
		:return:
		"""
    if self.verified_conditions == False:
      raise RuntimeError("Conditions Must Be Verified before Searching For Emails")

    all_emails = self.get_all_emails_from_directory()
    all_emails.Sort("[ReceivedTime]", True)
    emails_to_delete = []

    for each_email in all_emails:
      skip_flag = False
      for each_index in self.accepted_deletions_conditions:
        try:
          is_matching_condition = self.all_matching_functions[each_index](each_email)
        # Some emails do NOT have 1 of 2 properties:
        #  1.) SentOn property ( ex. emails about emails that failed to send)
        #  2.) SenderEmailAddress property (ex. some but NOT all no reply emails, these have a sender but
        #  		outlook does not see an address associated with the sender)
        except AttributeError:
          # self.emails_with_missing_attributes.append(each_email)
          self.emails_with_missing_attributes_count += 1
          skip_flag = True
          break

        if is_matching_condition is False:
          skip_flag = True
          break

      if skip_flag == True:  # don't collect email if condition did not match or has missing attribute
        continue
      else:
        emails_to_delete.append(each_email)

    return emails_to_delete

  def delete_emails_with_matching_conditions(self):
    '''
		Delete emails that match a certain condition
		:return:
		'''
    matching_emails = self.get_emails_matching_search_conditions()
    for email in matching_emails:
      email.Delete()
      self.delete_counter += 1

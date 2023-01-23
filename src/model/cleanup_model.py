import win32com.client as client

"""
This class is meant to have code that connects to outlook, pick
an email etc. and handle things before functionality of email-deletion.
There should only ever be one of this class and so I will apply a 
singleton pattern. This model will contain all functionality of actual e-mail 
deletion.
"""
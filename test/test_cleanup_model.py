import unittest
from src.model.cleanup_model import cleanup_model

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

def main():
	unittest.main(verbosity=3)

if __name__ == '__main__':
	main()
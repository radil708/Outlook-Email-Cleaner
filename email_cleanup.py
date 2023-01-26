from src.controller.cleanup_controller import cleanup_controller
from src.model.cleanup_model import cleanup_model
from src.view.simple_print_view import simple_print_view

"""
This is the file the should be called to run the email
cleanup program
"""

def main():
	m = cleanup_model()
	v = simple_print_view()
	controller = cleanup_controller(m, v)
	controller.run()


if __name__ == "__main__":
	main()
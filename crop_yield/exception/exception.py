import sys
from crop_yield.logging import logger
print("Running exception.py...")

class CropYieldException(Exception):
    """Base class for exceptions in the crop yield prediction module."""
    
    def __init__(self, error_message, error_details: sys):
        self.error_message = error_message
        _, _, exc_tb = error_details.exc_info()
        self.lineno = exc_tb.tb_lineno
        self.filename = exc_tb.tb_frame.f_code.co_filename

    def __str__(self):
        return "Error occurred in script: [{}] at line number: [{}] with message: [{}]".format(
            self.filename, self.lineno, self.error_message
        )


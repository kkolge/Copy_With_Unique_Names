# logger_setup.py
import logging
import datetime
import os

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILENAME = datetime.datetime.now().strftime("image_copier_%Y%m%d_%H%M%S.log")
LOG_FILEPATH = os.path.join(LOG_DIR, LOG_FILENAME) # This is where LOG_FILEPATH is defined

def setup_logger():
    """Configures and returns the application logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILEPATH),
            logging.StreamHandler() # For console output during development/debugging
        ]
    )
    return logging.getLogger("ImageCopierApp")

logger = setup_logger()
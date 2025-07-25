import logging
import os
from datetime import datetime

# Create log file name with timestamp
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Folder to store logs
logs_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Full path for log file
LOG_FILE_PATH = os.path.join(logs_dir, LOG_FILE)

# Setup basic logging config
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

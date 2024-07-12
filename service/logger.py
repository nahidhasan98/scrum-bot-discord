import os
import logging
from dotenv import load_dotenv
import colorlog

load_dotenv()

if os.getenv('MODE') == 'prod':
    # Log to a file if environment is production
    log_file = os.getenv('LOG_FILE')
    handler = logging.FileHandler(log_file)
else:
    # Log to console if environment is not production
    handler = colorlog.StreamHandler()

log_format = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
            'DEBUG': 'white',
            # 'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
    }
)
handler.setFormatter(log_format)

# Create a logger object
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

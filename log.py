import os
import logging

# Ensure the logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
log_file_path = os.path.join('logs', 'app.log')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger()
logger.addHandler(file_handler)
logger.propagate = False  # Ensure logs do not propagate to the root logger

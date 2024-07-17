import os
import yaml
from dotenv import load_dotenv


load_dotenv()

with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

config['openai']['api_key'] = os.getenv('OPENAI_API_KEY')
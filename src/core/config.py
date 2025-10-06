import os
from dotenv import load_dotenv


load_dotenv()


class Settings:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
    TMP_DIR = os.getenv('TMP_DIR', './tmp')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './outputs')


settings = Settings()
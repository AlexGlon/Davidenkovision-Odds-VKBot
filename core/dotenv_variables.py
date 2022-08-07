import os

from dotenv import load_dotenv

load_dotenv()

COEFFICIENT_OBSCURITY = os.environ.get('HIDE_COEFFICIENTS_UNTIL_CONTESTS_FINISHES')
MINUTES_PER_BACKUP = int(os.environ.get('MINUTES_PER_BACKUP'))
TOKEN = os.environ.get('TOKEN')

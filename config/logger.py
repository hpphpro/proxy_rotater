import logging 
from datetime import datetime


logging.basicConfig(
    format=f'%(levelname)s: %(message)s', 
    level=logging.INFO)

logger = logging.getLogger()

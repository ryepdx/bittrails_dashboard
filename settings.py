import pytz

APP_SECRET_KEY = 'iABSjQSiQSiYWq8mirZ7c8XxGzl6UBSsm9MFgMR7KUSL9b2Ft3aBsfUkiDUTVpy'

BITTRAILS_HOST = 'localhost:5000'
BITTRAILS_API_HOST = 'api.localhost:5000'
BITTRAILS_AUTH_URL = 'http://' + BITTRAILS_HOST + '/auth'

BITTRAILS_KEY = u'dAcFo8K6ArRC6zb3fZepVUvhGSU433'
BITTRAILS_SECRET = u'Ka0dSMaJwy2xGuxcw13nCk5c9VnVUR'

DATABASE = 'bittrails'
PORT = 5001
DEBUG = False
SERVER_TIMEZONE = pytz.timezone('America/Los_Angeles')

# Override any of the above settings if they are specified in settings_local.py
from settings_local import *

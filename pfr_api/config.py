from os import getenv, path

BASE_URL = 'https://www.pro-football-reference.com'
PARSER = 'lxml'
PFR_RATE_LIMIT_ERROR = 'Rate Limited Request (429 error)'
PFR_404_ERROR = 'Page Not Found (404 error)'

BASE_CACHE_DIR = path.join(path.expandvars(r'%APPDATA%'),'pfr_api')
BASE_HTML_CACHE_DIR = path.join(BASE_CACHE_DIR, 'HTML Cache')

# HTML cache directories
PFR_HTML_FANTASY_CACHE_DIR = path.join(BASE_HTML_CACHE_DIR, 'PFR Fantasy Cache')
PFR_HTML_PLAYER_CACHE_DIR = path.join(BASE_HTML_CACHE_DIR, 'PFR Player Cache')
SRCFB_HTML_PLAYER_CACHE_DIR = path.join(BASE_HTML_CACHE_DIR, 'SRCFB Player Cache')

# Feather cache directory
FEATHER_CACHE_DIRECTORY = path.join(BASE_CACHE_DIR, 'Feather Cache')
import re
from bs4 import BeautifulSoup
import pandas as pd
from os import path

from . config import BASE_URL, PFR_RATE_LIMIT_ERROR, PFR_404_ERROR, PFR_HTML_FANTASY_CACHE_DIR
from . database import pfr_website_singleton
from . parse.parse import parse_stats_table
from . parse.parser import PlayerRowParser
from . import fileutilities

PFR_HTML_ERROR_MESSAGES = [PFR_RATE_LIMIT_ERROR, PFR_404_ERROR]

class PFRWebpage(object):
    def __init__(self):
        pass
    
    ''' Checks BeautifulSoup HTML for error/corruption'''
    def _soup_has_errors(self, soup):
        # Return whether the HTML title contains an error message.
        errors = [error_message for error_message in PFR_HTML_ERROR_MESSAGES if error_message in soup.title.text]
        if errors:
            raise UserWarning(f'Received error(s): {[error for error in errors]}')
        
class PFRFantasy(PFRWebpage):
    def __init__(self, season):
        super().__init__()
        self._season = season
        self._soup = None
        self._cache_file = path.join(PFR_HTML_FANTASY_CACHE_DIR, f'{self._season}.html')

    ''' 
    Remove the HTML cache directory. Don't run this immediately after
    returning the desired data. It's possible that the data is corrupt.
    If it is, I don't want to have to request the data again.
    For that reason, the user is responsible for clearing the cache. 
    '''
    def clear_cache(self):
        fileutilities.remove_file(self._cache_file)

    def _fantasy_rankings_page_soup(self) -> BeautifulSoup:
        # First check if the file is cached. If so, check whether it has errors.
        if fileutilities.file_exists(self._cache_file):
            self._soup = pfr_website_singleton.get_soup_from_file(self._cache_file)
            if self._soup_has_errors(self._soup):
                self._soup = None
        # If the cached file does not exist or was errored, get the soup from PFR and cache the file.
        if self._soup == None:
            url = (
                '{base}/years/{season}/fantasy.htm'
                .format(base=BASE_URL, season=self._season)
            )
            self._soup = pfr_website_singleton.get_soup_from_website(url=url)
            if self._soup_has_errors(self._soup):
                raise RuntimeError(f'{url} ')
            fileutilities.write_to_file(f=self._cache_file, text=str(self._soup.prettify()))
        return self._soup
    
    def rankings(self) -> pd.DataFrame:
        soup = self._fantasy_rankings_page_soup()
        results_table = soup.find('table', {'id': 'fantasy'})
        columns, rows = parse_stats_table(
            results_table,
            stat_row_attributes={'class': lambda x: x != 'thead'},
            parsers={'player': PlayerRowParser()})
        return pd.DataFrame(columns=columns, data=rows)

''' Represents a NFL player's profile on PFR. Example https://www.pro-football-reference.com/players/H/HenrDe00.htm '''
class PFRProfile(PFRWebpage):
    def __init__(self, player_id: str):
        self._player_id = player_id
        super().__init__()

    def _profile_url_base(self) -> str:
        return f'{BASE_URL}/players/{self._player_id[0]}/{self._player_id}'

    def _nfl_gamelog_page_soup(self, season) -> BeautifulSoup:
        url = f'{self._profile_url_base()}/gamelog/{season}'
        soup = pfr_website_singleton.get_soup_from_website(url)
        if self._soup_has_errors(soup):
            raise RuntimeError(f'{url} ')
        return soup

    def _nfl_fantasy_page_soup(self, season: str = '') -> BeautifulSoup:  
        url = f'{self._profile_url_base()}/fantasy/{season}'
        soup = pfr_website_singleton.get_soup_from_website(url)
        if self._soup_has_errors(soup):
            raise RuntimeError(f'{url} ')
        return soup

    def nfl_regular_season_gamelog(self, season: str = '') -> pd.DataFrame:
        soup = self._nfl_gamelog_page_soup(season)
        results_table = soup.find('table', {'id': 'stats'})
        columns, rows = parse_stats_table(
            results_table,
            stat_row_attributes={'id': re.compile('^stats\..*$')})
        return pd.DataFrame(columns=columns, data=rows)

    def nfl_playoffs_gamelog(self, season: str = '') -> pd.DataFrame:
        soup = self._nfl_gamelog_page_soup(season)
        results_table = soup.find('table', {'id': 'stats_playoffs'})
        columns, rows = parse_stats_table(
            results_table,
            stat_row_attributes={'id': re.compile('^stats\..*$')})
        return pd.DataFrame(columns=columns, data=rows)

    def nfl_fantasy_stats(self, season: str = '') -> pd.DataFrame:
        soup = self._nfl_fantasy_page_soup(season)
        results_table = soup.find('table', {'id': 'player_fantasy'})
        # TODO handle weirdness with Inside 20 columns not being specific
        #      in data-stat field
        columns, rows = parse_stats_table(results_table)
        return pd.DataFrame(columns=columns, data=rows)

''' Represents a college player's profile on sports-refrence. Example https://www.sports-reference.com/cfb/players/derrick-henry-2.html'''
class SRCFBProfile(object):
    def __init__(self):
        super().__init__()

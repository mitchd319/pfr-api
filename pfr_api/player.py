import pandas as pd
from bs4 import BeautifulSoup
from . webpage import PFRProfile, SRCFBProfile
from pfr_api.config import FEATHER_CACHE_DIRECTORY
from pfr_api.fileutilities import file_exists
from os import path
'''
This class exists to store data about a player sourced from a database.
The data may then be used elsewhere, but this object is simply to store data.
'''
class Player(object):
    entity_type = 'players' # To be used in URL creation

    def __init__(
        self,
        name: str,
        player_id: str,
    ):
        self.name = name
        self.player_id = player_id
        self.pfr_profile = PFRProfile(self.player_id)
        self.srcfb_profile = SRCFBProfile()
        #self.seasons = self.pfr_profile.seasons()

    '''
    Get fantasy stats for a certain season. It is up to the user to verify that 
    this player has fantasy stats for a given season.
    '''
    def regular_season_gamelog(self, season: str = '') -> pd.DataFrame:
        file = path.join(FEATHER_CACHE_DIRECTORY,f'gamelog_{self.player_id}.feather')
        if not file_exists(file):
            gamelog = self.pfr_profile.nfl_regular_season_gamelog()
            gamelog.to_feather(path=file)
        df = pd.read_feather(file)
        # If the user wants just one season, group the DF accordingly
        if season:
            grouped = df.groupby(df.year_id)
            try:
                return grouped.get_group(int(season))
            except ValueError:
                raise RuntimeError(f'User did not pass in a valid season: {season}')
        else:
            return df

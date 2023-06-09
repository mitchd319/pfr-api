import sys
import pandas as pd
from os import path
from pfr_api.webpage import PFRFantasy
from pfr_api.player import Player
from pfr_api.config import FEATHER_CACHE_DIRECTORY
from pfr_api.fileutilities import file_exists
from progressbar import ProgressBar

# TODO: Move fantasy stuff to fantasy.py
def scrape_fantasy_rankings(year) -> pd.DataFrame:
    return PFRFantasy(season=year).rankings()    

def fantasy_rankings(year) -> pd.DataFrame:
    file = path.join(FEATHER_CACHE_DIRECTORY,f'fantasy_{year}.feather')
    fantasy = PFRFantasy(season=year)
    if not file_exists(file):
        data = fantasy.rankings()
        # Cache the data using Feather. https://towardsdatascience.com/the-best-format-to-save-pandas-data-414dca023e0d
        data.to_feather(path=file)
        print(f'Cached fantasy rankings: {file}')
    fantasy.clear_cache()
    del fantasy # Remove the object from memory
    return pd.read_feather(file)

def main():
    start_year = 1970
    end_year = 2022
    year = start_year
    
    # Get fantasy rankings
    yearly_fantasy_rankings_df_list = []
    while year <= end_year:
        yearly_fantasy_rankings_df_list.append(fantasy_rankings(year))
        print(f'Loaded {year} rankings...')
        year += 1

    # Create player objects found in fantasy rankings.
    # First, concatenate all of the fantasy ranking dataframes into one. Then make a
    complete_fantasy_rankings_df=pd.concat(yearly_fantasy_rankings_df_list)

    # I could make this look cleaner by using list comprehension to create the list of players,
    # but then I could not enforce that each player's ID is unique. Using all rows in the dataframe
    # from 1970-2022, there are just shy of 30,000 players created. When avoiding creating the same
    # player multiple times, only 6519 objects are created.
    print('Initializing player objects...')
    players = []
    for player_id, player_name in complete_fantasy_rankings_df[['player_id','player_name']].to_numpy():
        if not player_id in [p.player_id for p in players]:
            players.append(Player(name=player_name, player_id=player_id))
    print(len(players))

    # And here I am choosing against using list comprehension so I can use a really cool progress bar! :)
    print('Collecting gamelogs for each player...')
    gamelog_progress_bar = ProgressBar()
    gamelogs = []
    for player in players:
        gamelog_progress_bar.print_progress_bar(iteration=players.index(player), total=len(players))
        gamelogs.append(player.regular_season_gamelog())
    gamelogs = [player.regular_season_gamelog() for player in players]
    print(gamelogs)
if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover%
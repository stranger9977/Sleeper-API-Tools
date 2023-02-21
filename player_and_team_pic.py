import pandas as pd
import numpy as np
import nfl_data_py as nfl


player_df = pd.read_csv('/Users/nick/sleepertoolsversion2/values/players.csv')
data = nfl.import_rosters([2022])
df = pd.DataFrame(data)
df = df[['sleeper_id','headshot_url']]

team_data = nfl.import_team_desc()
team_df = pd.DataFrame(team_data)
team_df = team_df[['team_abbr', 'team_logo_espn','team_league_logo']]
player_team = player_df.merge(team_df, left_on='team', right_on='team_abbr')
player_team['team_logo_espn'].fillna(player_team['team_league_logo'], inplace=True)
player_team['player_id'] = player_team['player_id'].astype(str)
player_urls_df = player_team.merge(df, left_on='player_id', right_on='sleeper_id')
player_urls_df['headshot_url'].fillna(player_urls_df['team_league_logo'], inplace=True)

player_urls_df.to_csv('/Users/nick/sleepertoolsversion2/values/player_urls.csv', index=False)


# -*- coding: utf-8 -*-
"""Untitled35.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1L5V2n6f8pbjGfUsTI2NL-qUGTcSHKz6J
"""



import nfl_data_py as nfl
import pprint as pp
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
import urllib
from PIL import Image
import matplotlib.font_manager as font_manager


seasons = np.arange(2018,2023).tolist()
df = nfl.import_pbp_data(seasons)

df.info(verbose=True)

roster_data = pd.DataFrame()

# Loop over the past 5 years (including the current year)
for year in range(2022, 2016, -1):
    # Import the roster data for the current year
    roster_df = nfl.import_rosters([year])

    # Append the roster data to the new DataFrame
    roster_data = roster_data.append(roster_df, ignore_index=True)

roster_df = nfl.import_rosters([2022])
roster_df = roster_data

roster_df.info(verbose=True)

roster_df = roster_df[['player_id','player_name','team','position','sleeper_id','headshot_url']]

team_data = nfl.import_team_desc()
team_df = pd.DataFrame(team_data)
team_df.columns
team_df = team_df[['team_abbr', 'team_logo_espn','team_league_logo','team_color','team_color2']]
player_team = roster_df.merge(team_df, left_on='team', right_on='team_abbr')
player_team['team_logo_espn'].fillna(player_team['team_league_logo'], inplace=True)
player_team['player_id'] = player_team['player_id'].astype(str)

player_team['headshot_html'] =  player_team['headshot_url'] \
        .str.replace(
        '(.*)',
        '<img src="\\1" style="max-height:62px;"></img>')
player_team['team_logo_espn_html'] = player_team['team_logo_espn'] \
        .str.replace(
        '(.*)',
        '<img src="\\1" style="max-height:62px;"></img>')
rb_roster_df = player_team[player_team['position'] == 'RB'].drop('position',axis = 1)


# df = df.dropna(subset=['player_id'])

# df = df.merge(roster, on='player_id')
# df.info(verbose=True)
# weighted_opportunity_df = df[['player_id','player_name','receiver_player_id','game_id','pass_attempt','rush_attempt','yardline_100']]
# plays_per_game_df = df[['player_id','player_name','game_id']]
# goal_to_go_att = df[['player_id','player_name','game_id','rush_attempt','goal_to_go']]
# team_tgt = df[['player_id','player_name','posteam','pass_attempt']]


rb_roster_df



df = df.groupby('receiver_player_id').filter(lambda x: x['game_id'].nunique() >= 6)

target_df = df.groupby(['game_id', 'receiver_player_id', 'receiver_player_name', 'posteam'], as_index=False)['pass_attempt'].sum().merge(df.loc[df['receiver_player_id'].notnull()].groupby(['game_id', 'posteam'], as_index=False)['pass_attempt'].sum(), on=['game_id', 'posteam'], suffixes=('_player', '_team'))

target_df['target_share'] = round(target_df['pass_attempt_player'] / target_df['pass_attempt_team'] * 100, 2)

target_df = target_df.groupby(['receiver_player_id', 'receiver_player_name', 'posteam'], as_index=False)[['target_share' , 'pass_attempt_player']].mean().sort_values(by='target_share', ascending=False)
target_df
target_df.rename(columns={'receiver_player_id':'player_id', 'posteam':'team','pass_attempt_player':'player_targets','pass_attempt_team':'team_targets'}, inplace=True)
target_df
target_df = target_df[['player_id','team','target_share']]

target_df = rb_roster_df.merge(target_df, on=('player_id','team'))
target_df = target_df.drop_duplicates(subset=['player_id', 'team','target_share'])
target_df.sort_values(by='target_share', ascending=False,inplace=True)
target_df.columns
target_df.rename(columns={'player_name':"Name",'team_logo_espn':'Team', 'target_share':'Team TGT %'}, inplace=True)


visual_df = target_df[['Name','headshot_url','Team','Team TGT %','team_color','team_color2']]
visual_df.to_csv('visual_df.csv', index=False)

# Load the processed data from a file


# visual_df=visual_df[:25]
#
# visual_df = visual_df.reset_index(drop=True)


# rb_html = (visual_df
#  .style\
#  .format({
#      'Team TGT %': '{:.2f}%'.format
#      })\
# .set_properties(**{'text-align':'center','font':'Bebas Neue','font-weight':'bold','font-size':'16px','padding':'5px'})\
# # .set_table_styles([{'selector': 'th', 'props': [('background-color', '#30b5fd'),('font-size','20px'),('color','white'),('padding','5px')]}])\
#  .hide_index()\
#  .render()
#  )
#
# import os
#
# # to open/create a new html file in the write mode
# f = open('rb_html.html', 'w')
#
# # the html code which will go in the file GFG.html
#
# # writing the code into the file
# f.write(rb_html)
#
# # close the file
# f.close()
#
# # 1st method how to open html files in chrome using
# filename = 'file:///'+os.getcwd()+'/' + 'rb_html.html'
#
#
# import IPython
# IPython.display.HTML(filename='/content/rb_html.html')


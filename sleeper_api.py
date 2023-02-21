import sys
from pprint import pprint
from sleeper_wrapper import League
from sleeper_wrapper import User
from sleeper_wrapper import Players
import requests
import json
import pandas as pd


#input league id
league_id = 824128043063820288
league = League(league_id)
# get rosters from sleeper
rosters = league.get_rosters()
users = league.get_users()

#get players
def get_players_to_csv():
    players = Players()
    data = Players.get_all_players(players)
    players_df = pd.DataFrame.from_dict(data)
    players_df = players_df.transpose()
    players_df.to_csv('/Users/nick/sleeper_api_tools/Data/players.csv', index=False)


def get_rosters_df():
    league_id = 824128043063820288
    league = League(league_id)
    # get rosters from sleeper
    rosters = league.get_rosters()
    users = league.get_users()
    players_df = pd.read_csv('/Users/nick/sleeper_api_tools/Data/players.csv')
    #this function gets all information needed to understand each teams players
    # including taxi, reserve, starters, and bench
    rosters_df = pd.DataFrame(rosters)
    users_df = pd.DataFrame(users)
    rosters_df_trim = rosters_df[['owner_id', 'roster_id', 'players','taxi','reserve']]
    rosters_df_users = rosters_df[['owner_id', 'roster_id']]
    users_df_trim = users_df[['user_id', 'display_name']]
    rosters_df = rosters_df_trim.merge(users_df_trim, left_on='owner_id', right_on='user_id')
    users_df_trim = users_df[['user_id', 'display_name']]
    users_df_trim = rosters_df_users.merge(users_df_trim, left_on='owner_id', right_on='user_id')
    rosters_players_df = rosters_df[['owner_id','roster_id','display_name', 'players']]
    rosters_taxi_df = rosters_df[['owner_id','roster_id','display_name', 'taxi']]
    rosters_reserve_df= rosters_df[['owner_id','roster_id','display_name', 'reserve']]
    rosters_players_df = rosters_players_df.explode('players').reset_index(drop=True)
    rosters_taxi_df = rosters_taxi_df.explode('taxi').reset_index(drop=True)
    rosters_reserve_df = rosters_reserve_df.explode('reserve').reset_index(drop=True)
    rosters_taxi_df.rename(columns={'taxi':'players'},inplace=True)
    rosters_reserve_df.rename(columns={'reserve':'players'},inplace=True)
    rosters_df = pd.concat([rosters_players_df])
    #trim players_df
    players_df = players_df[[ 'player_id','full_name', 'position','team']]

    rosters_df = rosters_df.merge(players_df, how='left', left_on='players',right_on='player_id')
    rosters_df = rosters_df[['owner_id', 'roster_id','display_name', 'full_name',
       'position', 'team']]
    roster_df_concat = rosters_df[['display_name','full_name','position','team']]

    league = League(824128043063820288)

    # pulling in rosters from sleeper/
    rosters = league.get_rosters()
    rosters_df = pd.DataFrame(rosters)

    # pulling in the user data and ids.
    users = league.get_users()
    users_df = pd.DataFrame(users)

    # #merging for display names
    rosters_df_trim = rosters_df[['owner_id', 'roster_id']]
    users_df_trim = users_df[['user_id', 'display_name']]

    rosters_df = rosters_df_trim.merge(users_df_trim, left_on='owner_id', right_on='user_id')

    rosters_df = rosters_df[['display_name', 'user_id', 'roster_id']]

    rosters_display_name = rosters_df[['display_name', 'user_id', 'roster_id']]

    rosters_df = rosters_df_trim.merge(users_df_trim, left_on='owner_id', right_on='user_id')

    # #getting the draft order

    response = requests.get("https://api.sleeper.app/v1/draft/824128043810394112")

    draft_order = response.json()["draft_order"]

    draft_order_df = pd.DataFrame.from_dict(draft_order, orient='index', columns=['Pick'])

    # #combining draft order with rosters
    picks_df = rosters_df.merge(draft_order_df, left_on='owner_id', right_index=True)

    picks_df = picks_df.sort_values(by=['Pick'])
    print(picks_df)
    # #generating a repeating list for the draft order for a period of 3 years
    draft_order_list = []

    for i in range(15):
        for index, row in picks_df.iterrows():
            r = row.to_dict()
            draft_order_list.append(r)

        draft_order_df = pd.DataFrame(draft_order_list)

    # adding a column that shows the pick number from 1 to 180 (three full years of drafts)
    draft_order_df['range'] = pd.Series(range(1, 181)).astype(int)

    from datetime import date

    # add a column with the year
    def year(row):
        if row['range'] > 0 and row['range'] <= 60:
            return date.today().year + 1
        elif row['range'] > 60 and row['range'] <= 120:
            return date.today().year + 2
        elif row['range'] > 120 and row['range'] <= 180:
            return date.today().year + 3

    # # add a column with the round
    def round(row):
        if row['range'] > 0 and row['range'] <= 12:
            return "1"
        elif row['range'] > 12 and row['range'] <= 24:
            return "2"
        elif row['range'] > 24 and row['range'] <= 36:
            return "3"
        elif row['range'] > 36 and row['range'] <= 48:
            return "4"
        elif row['range'] > 48 and row['range'] <= 60:
            return "5"
        if row['range'] > 60 and row['range'] <= 72:
            return "1"
        elif row['range'] > 72 and row['range'] <= 84:
            return "2"
        elif row['range'] > 84 and row['range'] <= 96:
            return '3'
        elif row['range'] > 96 and row['range'] <= 108:
            return '4'
        elif row['range'] > 108 and row['range'] <= 120:
            return '5'
        if row['range'] > 120 and row['range'] <= 132:
            return '1'
        elif row['range'] > 132 and row['range'] <= 144:
            return '2'
        elif row['range'] > 144 and row['range'] <= 156:
            return '3'
        elif row['range'] > 156 and row['range'] <= 168:
            return '4'
        elif row['range'] > 160 and row['range'] <= 180:
            return '5'

    draft_order_df['Year'] = draft_order_df.apply(lambda row: year(row), axis=1)
    draft_order_df['Round'] = draft_order_df.apply(lambda row: round(row), axis=1)

    # adds a zero to the picknumber
    draft_order_df["pick_concat"] = draft_order_df.Pick.map("{:02}".format)

    draft_order_df['player'] = draft_order_df['Year'].astype(str) + " " + "Pick" + " " + draft_order_df['Round'] + "." + \
                               draft_order_df['pick_concat']

    # creating a table with the original owner id and the year and round of the pick
    draft_order_df = draft_order_df[['roster_id', 'display_name', 'Year', 'Round', 'Pick', 'range']]

    draft_order_df = draft_order_df.rename(columns={'roster_id': 'original_owner_id'})
    draft_order_df['new_owner_id'] = draft_order_df['original_owner_id']

    trade = league.get_traded_picks()
    trade_df = pd.DataFrame(trade)
    # print(draft_order_df)
    # trade_df.to_csv('/Users/nick/Desktop/FantasyDashboard/Sleeper/traded_picks.csv', index_col=False)

    # trade_df = pd.read_csv('/Users/nick/Desktop/FantasyDashboard/Sleeper/traded_picks.csv' , index_col=False )
    # print(picks_df.head())
    trade_shuffle_df = trade_df[['owner_id', 'roster_id', 'season', 'round']].astype(int)
    trade_shuffle_df = trade_shuffle_df.rename(
        columns={'roster_id': 'original_owner_id', 'owner_id': 'new_owner_id', 'season': 'Year', 'round': 'Round'})
    picks_df = picks_df.rename(columns={'roster_id': 'original_owner_id'})
    picks_df['original_owner_id'] = picks_df['original_owner_id'].astype(int)
    trade_shuffle_df['original_owner_id'] = trade_shuffle_df['original_owner_id'].astype(int)
    picks_df = picks_df[['original_owner_id', 'display_name', 'Pick']]
    trade_shuffle_df = trade_shuffle_df.merge(picks_df, how='left', on='original_owner_id')
    # print(picks_df.dtypes)
    # print(draft_order_df)
    # print(trade_shuffle_df.head(40))
    # print(picks_df.info(verbose=True))
    # print(trade_shuffle_df.info(verbose=True))
    # print(trade_shuffle_df)

    draft_order_df['Round'] = draft_order_df['Round'].astype(int)

    draft_order_df = draft_order_df[['original_owner_id', 'display_name', 'Year', 'Round', 'Pick', 'range']]
    draft_trade_df = pd.merge(draft_order_df, trade_shuffle_df, on=['Year', 'Round', 'Pick'], how='left')

    # do I need to add the drat order to this dataframe before merging? It think this will help me re order the picks.

    draft_trade_df.sort_values(by='range')

    draft_trade_df['new_owner_id'].fillna(draft_trade_df['original_owner_id_x'], inplace=True)

    draft_trade_df['display_name_y'].fillna(draft_trade_df['display_name_x'], inplace=True)

    final_draft_order_df = draft_trade_df[['new_owner_id', 'Year', 'Round', 'Pick']]

    final_draft_order_df = final_draft_order_df.rename(columns={'new_owner_id': 'roster_id'})
    rosters_display_name = rosters_display_name[['roster_id', 'display_name']]
    final_draft_order_df = final_draft_order_df.merge(rosters_display_name, how='left', on='roster_id')

    # need tou seperate future picks out and reformat the strings so they match dynastyprocess values. I am so happy to be at this stage.

    final_draft_order_df.to_csv('/Users/nick/sleeper_api_tools/picks.csv')

    final_draft_order_df['full_name'] = final_draft_order_df['Year'].astype(str) + " " + final_draft_order_df['Round'].astype(str) + final_draft_order_df['Pick'].astype(str)
    final_draft_order_df['position'] = 'Pick'
    final_draft_order_df['team'] = 'Draft'
    final_draft_order_df = final_draft_order_df[['display_name','full_name','position','team']]

    full_roster_and_picks_df = pd.concat([final_draft_order_df,roster_df_concat])
    full_roster_and_picks_df.to_csv('/Users/nick/sleeper_api_tools/picks.csv')
    values_df = pd.read_csv(
        'https://raw.githubusercontent.com/dynastyprocess/data/master/files/values.csv')



    print(values_df.sort_values(by='value_2qb',ascending=False))


    values_df = values_df[['player','pos','team','age','value_2qb']]
    pick_values_df = values_df[values_df['pos'] =='PICK']
    values_df = values_df[values_df['pos'] !='PICK']
    print(values_df)
    values_df['merge_name'] = values_df[
        'player'].str.replace(r'( [A-Z]*)$',
                              '').str.strip().str.replace('-',
                                                          '').str.replace(
        r'\bJr.$', '', regex=True).str.replace(r'\bSr.$', '', regex=True).str.replace('.', "").str.replace(r'\bII$', '',
                                                                                                           regex=True).str.replace(
        r'\bI$', '', ).str.strip()
    print(pick_values_df)
    pick_values_df['merge_name'] = pick_values_df['player']
    pick_values_df['merge_name'] =  pick_values_df['merge_name'].str.replace('st','').str.replace('nd','').str.replace('rd','').str.replace('th','')

    values_df = pd.concat([values_df,pick_values_df])






    keep_trade_cut_player_and_pick_values_df = pd.read_csv('/Users/nick/sleeper_api_tools/Data/ktcvalue.csv')
    keep_trade_cut_player_values_df = keep_trade_cut_player_and_pick_values_df[keep_trade_cut_player_and_pick_values_df['pos']!= 'PICK']
    keep_trade_cut_player_values_df['merge_name'] = keep_trade_cut_player_values_df[
        'Player'].str.replace(r'( [A-Z]*)$',
                              '').str.strip().str.replace('-',
                                                          '').str.replace(
        r'\bJr.$', '', regex=True).str.replace(r'\bSr.$', '', regex=True).str.replace('.', "").str.replace(r'\bII$', '',
                                                                                                           regex=True).str.replace(
        r'\bI$', '', ).str.strip()
    keep_trade_cut_pick_values_df = keep_trade_cut_player_and_pick_values_df[keep_trade_cut_player_and_pick_values_df['pos']== 'PICK']
    keep_trade_cut_pick_values_df['merge_name']= keep_trade_cut_pick_values_df['Player']
    print(keep_trade_cut_pick_values_df.info(verbose=True))
    keep_trade_cut_pick_values_df['merge_name'] = keep_trade_cut_pick_values_df['merge_name'].str.replace('st', '').str.replace('nd', '').str.replace('rd','').str.replace('th', '').str.replace(' Mid','')
    keep_trade_cut_player_and_pick_values_df = pd.concat([keep_trade_cut_player_values_df,keep_trade_cut_pick_values_df])


    keep_trade_cut_player_and_pick_values_df.to_csv('/Users/nick/sleeper_api_tools/picks.csv')
    print(keep_trade_cut_player_and_pick_values_df[keep_trade_cut_player_and_pick_values_df['pos']=='PICK'])



    full_roster_and_picks_df.replace({'full_name': {"William Fuller": "Will Fuller", 'Ken Walker': "Kenneth Walker"
        , "Robby Anderson": "Robbie Anderson",
                                                     "Amon-Ra St.": "Amon-Ra St. Brown", "Gabe Davis": "Gabriel Davis",
                                                     'Joshua Palmer': "Josh Palmer"}}, inplace=True)
    full_roster_and_picks_df['merge_name'] = full_roster_and_picks_df['full_name'].str.replace(r'( [A-Z]*)$',
                                                                           '').str.strip().str.replace('-',
                                                                                                       '').str.replace(
        r'\bJr.$', '', regex=True).str.replace(r'\bSr.$', '', regex=True).str.replace('.', "").str.replace(r'\bII$', '',
                                                                                                           regex=True).str.replace(
        r'\bI$', '', ).str.strip()
    values_df.replace({'merge_name': {"William Fuller": "Will Fuller", 'Ken Walker': "Kenneth Walker"
        , "Robby Anderson": "Robbie Anderson",
                                      "Amon-Ra St.": "Amon-Ra St. Brown", "Gabe Davis": "Gabriel Davis",
                                      'Joshua Palmer': "Josh Palmer"}}, inplace=True)



    etr_df = pd.read_csv('/Users/nick/sleeper_api_tools/Data/ETR Dynasty Rankings.csv')

    etr_players_df = etr_df[etr_df['Status']!='Pick']
    etr_picks_df = etr_df[etr_df['Status']=='Pick']
    etr_picks_df['Player'] = etr_picks_df['Player'].str.replace('st', '').str.replace('nd', '').str.replace('rd','').str.replace('th', '').str.replace('Mid', '').str.replace('--','').\
        str.replace('Top','').str.replace('Half','').str.replace('Bottom','')

    etr_df = pd.concat([etr_picks_df,etr_players_df])
    etr_df.to_csv('/Users/nick/sleeper_api_tools/picks.csv')





    etr_df.replace({'merge_name': {"William Fuller": "Will Fuller", 'Ken Walker': "Kenneth Walker"
        , "Robby Anderson": "Robbie Anderson",
                                      "Amon-Ra St.": "Amon-Ra St. Brown", "Gabe Davis": "Gabriel Davis",
                                      'Joshua Palmer': "Josh Palmer"}}, inplace=True)
    etr_df['merge_name'] = etr_df['Player'].str.replace(r'( [A-Z]*)$',
                                                        '').str.strip().str.replace('-',
                                                                                    '').str.replace(
        r'\bJr.$', '', regex=True).str.replace(r'\bSr.$', '', regex=True).str.replace('.', "").str.replace(r'\bII$', '',
                                                                                                           regex=True).str.replace(
        r'\bI$', '', ).str.strip()


    points_df = pd.read_csv('/Users/nick/sleeper_api_tools/Data/FantasyPros_Fantasy_Football_Points_PPR.csv')
    ros_df = pd.read_csv('/Users/nick/sleeper_api_tools/Data/ros-proj-QBRBWRTE.csv')

    points_df.replace({'Player': {"William Fuller": "Will Fuller", 'Ken Walker': "Kenneth Walker"
        , "Robby Anderson": "Robbie Anderson",
                                  "Amon-Ra St.": "Amon-Ra St. Brown", "Gabe Davis": "Gabriel Davis",
                                  'Joshua Palmer': "Josh Palmer"}}, inplace=True)
    ros_df.replace({'Name': {"William Fuller": "Will Fuller", 'Ken Walker': "Kenneth Walker"
        , "Robby Anderson": "Robbie Anderson",
                               "Amon-Ra St.": "Amon-Ra St. Brown", "Gabe Davis": "Gabriel Davis",
                               'Joshua Palmer': "Josh Palmer"}}, inplace=True)

    new_header = ros_df.iloc[0]  # grab the first row for the header
    ros_df = ros_df[1:]  # take the data less the header row
    ros_df.columns = new_header  # set the header row as the df header
    keep_trade_cut_player_and_pick_values_df = keep_trade_cut_player_and_pick_values_df[['merge_name','KTC Value']]
    # keep_trade_cut_player_and_pick_values_df = pd.concat([keep_trade_cut_player_and_pick_values_df]*12, ignore_index =True)
    # values_df = pd.concat([values_df] * 12, ignore_index=True)
    ros_df.rename(columns={'Rank':'ROS Points Rank','Points':'ROS Points'}, inplace=True)
    print(ros_df.info(verbose=True))
    points_df['merge_name'] = points_df['Player'].str.replace(r'( [A-Z]*)$',
                                                                           '').str.strip().str.replace('-',
                                                                                                       '').str.replace(
        r'\bJr.$', '', regex=True).str.replace(r'\bSr.$', '', regex=True).str.replace('.', "").str.replace(r'\bII$', '',
                                                                                                           regex=True).str.replace(
        r'\bI$', '', ).str.strip()

    ros_df['merge_name'] = ros_df['Name'].str.replace(r'( [A-Z]*)$',
                                                                           '').str.strip().str.replace('-',
                                                                                                       '').str.replace(
        r'\bJr.$', '', regex=True).str.replace(r'\bSr.$', '', regex=True).str.replace('.', "").str.replace(r'\bII$', '',
                                                                                                           regex=True).str.replace(
        r'\bI$', '', ).str.strip()

    points_df = points_df[['Player', 'merge_name','Points', 'Games']]
    numeric_columns = ['Pass_Att', 'Rush_Att', 'Pass_Comp', 'Pass_Yards', 'Rush_Yards', 'Pass_Tds',
                       'Rush_Tds', 'Pass_Ints', 'Fum_Lost', 'Rec', 'Rec_Tds', 'Rec_Yds', 'ADP', 'Health']



    df_list = [etr_df, full_roster_and_picks_df, points_df, ros_df,values_df]

    points_df = points_df.merge(ros_df, on='merge_name')
    points_df = points_df[['merge_name', 'Points', 'ROS Points','ROS Points Rank']]
    # points_df[['Points', 'ROS Points']] = points_df[['Points', 'ROS Points']].fillna(0
    etr_df.rename(columns={'SF/TE Prem': 'ETR Rank'}, inplace=True)
    etr_merge_df = etr_df[['merge_name', 'ETR Rank']]
    values_df = values_df[['merge_name','value_2qb','age']]
    values_df.rename(columns={'value_2qb': 'DyPro Value'}, inplace=True)

    display_etr_df = full_roster_and_picks_df.merge(etr_merge_df, how='left', on='merge_name')
    display_etr_df = display_etr_df.merge(keep_trade_cut_player_and_pick_values_df, how='left', on='merge_name')
    display_etr_df = display_etr_df.merge(values_df, how='left', on='merge_name')
    display_etr_df = display_etr_df.merge(points_df, how='left', on='merge_name')

    display_etr_df['Points Rank'] = display_etr_df['Points'].rank(ascending=False)
    display_etr_df.sort_values(by='ROS Points Rank', ascending=True, inplace=True)

    print(display_etr_df.columns)

    #
    import math
    display_etr_df['KTC Rank'] = display_etr_df['KTC Value'].rank( ascending=False ,method='average')
    display_etr_df['DyPro Rank'] = display_etr_df['DyPro Value'].rank(ascending=False, method='average')
    def exponential_decay(x):
        return 10500 * math.exp(x * -0.0235)
    display_etr_df['DyPro Value'] = display_etr_df['DyPro Rank'].apply(lambda x : 10500 * math.exp(x * -0.0235))
    display_etr_df['KTC Value'] = display_etr_df['KTC Rank'].apply(lambda x : 10500 * math.exp(x * -0.0235))
    display_etr_df['ETR Value'] = display_etr_df['ETR Rank'].apply(lambda x : 10500 * math.exp(x * -0.0235))
    display_etr_df['WinNow Rank'] = display_etr_df[['Points Rank', 'ROS Points Rank']].mean(axis=1)
    display_etr_df['WinNow Value'] = display_etr_df['WinNow Rank'].apply(lambda x: 10500 * math.exp(x * -0.0235))

    # display_etr_df['WinNow Value'] = round(display_etr_df[['Points Value', 'ROS Points Value']].mean(axis=1), 2)
    display_etr_df['Future Value'] = display_etr_df[['KTC Value', 'DyPro Value', 'ETR Value']].mean(axis=1)



    display_etr_df['HIM Value'] = display_etr_df[['WinNow Value', 'Future Value']].mean(axis=1)


    display_etr_df['Uncertainty'] = display_etr_df[['KTC Value', 'DyPro Value', 'ETR Value']].std(axis=1)

    display_etr_df['HIM RANK'] = display_etr_df['HIM Value'].rank(ascending=False)
    display_etr_df.sort_values(by='HIM RANK', inplace=True)
    display_etr_df.rename(columns={'display_name': "Rostered By",'full_name':'Player','age':'Age'},inplace=True)
    display_etr_df = display_etr_df[['Rostered By','HIM RANK', 'Player', 'Age','position', 'team', 'Points Rank','ROS Points Rank', 'KTC Value',
       'DyPro Value', 'DyPro Rank', 'ETR Value', 'WinNow Value', 'Future Value', 'HIM Value',
       'Uncertainty' ]]
    display_etr_df.to_csv('/Users/nick/sleeper_api_tools/Data/makeitdynasty.csv')

#
#     # values_df.rename(columns={'ecr_2qb': 'value_2qb', 'age': 'dypro_age'}, inplace=True)
#     #
#     #
#     # # draft_order_df = draft_order_df.rename(columns={'roster_id': 'original_owner_id'})
#     # # draft_order_df['new_owner_id'] = draft_order_df['original_owner_id']
#     # draft_order_df.to_csv('/Users/nick/sleeper_api_tools/Data/picks.csv')
#     #
#     #
#     # trade = league.get_traded_picks()
#     # trade_df = pd.DataFrame(trade)
#     # trade_shuffle_df = trade_df[['owner_id', 'roster_id', 'season', 'round']].astype(int)
#     # users_df_trim = users_df_trim[['roster_id','display_name']]
#     # trade_shuffle_df = trade_shuffle_df[trade_shuffle_df['season'] != 2022]
#     # trade_shuffle_df = trade_shuffle_df.merge(users_df_trim, how='left', left_on='owner_id', right_on='roster_id')
#     # trade_shuffle_df = trade_shuffle_df[['owner_id','display_name','season','round']]
#     # trade_shuffle_df.to_csv('/Users/nick/sleeper_api_tools/Data/picks.csv')
#     #
#     #
#     # trade_shuffle_df = trade_shuffle_df.rename(
#     #     columns={'season': 'Year', 'round': 'Round'})
#     # print(draft_order_df)
#     # draft_order_df['roster_id'] = draft_order_df['roster_id'].astype(int)
#     # trade_shuffle_df['owner_id'] = trade_shuffle_df['owner_id'].astype(int)
#     # draft_order_df = draft_order_df[['roster_id', 'display_name','Year', 'Round','Pick']]
#     # draft_order_df['Round'] = draft_order_df['Round'].astype(int)
#     # #
#     # #
#     # # draft_order_df = draft_order_df[['original_owner_id', 'display_name', 'Year', 'Round']]
#     # draft_trade_df = pd.merge(draft_order_df, trade_shuffle_df, on =['Year', 'Round'], how='left')
#     # draft_trade_df.sort_values(by='Round')
#     # #
#     # final_draft_order_df = draft_trade_df[['display_name_y','display_name_x','Year', 'Round']]
#     #
#     # final_draft_order_df.to_csv('/Users/nick/sleeper_api_tools/Data/picks.csv')
# # #
get_rosters_df()
#
# #     # need tou seperate future picks out and reformat the strings so they match dynastyprocess values. I am so happy to be at this stage.
# # #
# # #     final_draft_order_df.to_csv('/Users/nick/Desktop/FantasyDashboard/Sleeper.draft_order.csv')
# # #
# # #     player_values_df = pd.read_csv('https://raw.githubusercontent.com/dynastyprocess/data/master/files/values.csv')
# # #
# # #     player_values_df['position'] = player_values_df['pos'].astype(str)
# # #
# # #     player_values_df = player_values_df[player_values_df['player'].str.contains('Early | Late | Mid ') == False]
# # #     pick_values_df = player_values_df.loc[player_values_df['position'] == 'PICK']
# # #
# # #     pick_values_df = pick_values_df[['player', 'position', 'value_1qb', 'value_2qb', 'scrape_date']]
# # #
# # #     final_draft_order_df["pick_concat"] = final_draft_order_df.Pick.map("{:02}".format)
# # #
# # #     year = date.today().year
# # #     this_year = str(year)
# # #     next_year = str(year + 1)
# # #     year_following = str(year + 2)
# # #
# # #     final_draft_order_df = final_draft_order_df.astype(str)
# # #
# # #     def pick_names(row):
# # #         if row['Year'] == next_year or row['Year'] == year_following:
# # #             if row['Round'] == '1':
# # #                 return row['Year'] + " " + row['Round'] + "st"
# # #             if row['Round'] == '2':
# # #                 return row['Year'] + " " + row['Round'] + "nd"
# # #             if row['Round'] == '3':
# # #                 return row['Year'] + " " + row['Round'] + "rd"
# # #             if row['Round'] == '4':
# # #                 return row['Year'] + " " + row['Round'] + "th"
# # #             if row['Round'] == '5':
# # #                 return row['Year'] + " " + row['Round'] + "th"
# # #         elif row['Year'] == this_year:
# # #             return row['Year'] + " " + "Pick" + " " + row['Round'] + "." + row['pick_concat']
# # #
# # #     final_draft_order_df['player'] = final_draft_order_df.apply(lambda row: pick_names(row), axis=1)
# # #
# # #     final_draft_order_df = final_draft_order_df[['roster_id', 'display_name', 'player']]
# # #
# # #     from datetime import datetime
# # #
# # #     pick_values_df = pd.merge(final_draft_order_df, pick_values_df, on='player', how='left')
# # #     print(pick_values_df.head())
# # #     pick_values_df.to_csv(f'/Users/nick/Desktop/FantasyDashboard/Sleeper/pick_values-{datetime.now():%Y-%m-%d}.csv',
# # #                           index=False)
# # #
# # #     # # # # future_picks_df = future_picks_df.sort_values(by=['ecr_1qb'])
# # #
# # #     # # # # # future_picks_df[['season', 'round']] = future_picks_df.player.str.split(' ', expand=True)
# # #     # # # # # future_picks_df['round'] = future_picks_df['round'].str[:1]
# # #
# # #     # # # # # # # pick_values_df = pd.concat([pick_values_df,future_picks_df], ignore_index=True)
# # #
# # #     # # # # # rosters_picks = pd.concat([draft_order_df, pick_values_df], axis=1)
# # #     # # # # # print(future_picks_df.info(verbose=True))
# # #
# # #     # # # # # # # # pick_values_df = pd.concat([draft_order_df, pick_values_df], axis=1)
# # #
# # #     # # # # # # # # pick_values_shuffle_df = pick_values_df[['roster_id', 'season_orig', 'round_orig']]
# # #
# # #     # # # # # # # # # from datetime import datetime
# # #     # # # # # # # from datetime import datetime
# # #
# # #     # # # # # # print(pick_values_shuffle_df)
# # #
# # # # create pick grid
# # # # apply pick grid to rosters
# # # # merge users with rosters
# # # # get transactions from sleeper
# # # # merge trasactions with rosters
# # #
# # #
# # # # Press the green button in the gutter to run the script
# # #
# # # # See PyCharm help at https://www.jetbrains.com/help/pycharm/

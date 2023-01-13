from datetime import datetime
import streamlit as st
import requests
import pandas as pd
def main():
    username = st.text_input('Enter your sleeper username here', 'brochillington')
    user_id = get_user_id(username)
    get_rosters(user_id)

def get_user_id(username):
    response = requests.get(f'https://api.sleeper.app/v1/user/{username}')
    data = response.json()
    user_id = data['user_id']
    return user_id

def get_rosters(user_id):
    current_year = datetime.now().year
    previous_year = current_year-1
    response = requests.get(f'https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{previous_year}')
    leagues = response.json()
    league_id_list = [d['league_id'] for d in leagues]
    league_name_list = [d['name'] for d in leagues]
    option = st.selectbox(
        'Please Choose Your League',
        (league_name_list))
    league_name_id = dict(zip(league_name_list, league_id_list))
    league_id = league_name_id[option]
    response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/rosters')
    rosters = response.json()
    response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/users')
    users = response.json()
    users_df = pd.DataFrame(users)
    rosters_df = pd.DataFrame(rosters)
    rosters_df_trim = rosters_df[['owner_id', 'roster_id', 'players']]
    users_df_trim = users_df[['user_id', 'display_name']]
    rosters_df = rosters_df_trim.merge(users_df_trim, left_on='owner_id', right_on='user_id')
    rosters_df = rosters_df[['display_name', 'players']]
    rosters_df = rosters_df.explode('players').reset_index(drop=True)
    if option:
        st.write(rosters_df)
    return rosters


if __name__ == '__main__':
    main()
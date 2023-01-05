from datetime import datetime
import streamlit as st
import requests
def main():
    username = st.text_input('Enter your sleeper username here', 'brochillington')
    user_id = get_user_id(username)
    get_league_info(user_id)

def get_user_id(username):
    response = requests.get(f'https://api.sleeper.app/v1/user/{username}')
    data = response.json()
    user_id = data['user_id']
    return user_id

def get_league_info(user_id):
    current_year = datetime.now().year
    previous_year = current_year-1
    response = requests.get(f'https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{previous_year}')
    leagues = response.json()
    league_id_list = [d['league_id'] for d in leagues]
    league_name_list = [d['name'] for d in leagues]
    scoring_settings_list = [d['scoring_settings'] for d in leagues]
    settings_list = [d['settings'] for d in leagues]
    roster_positions_list = [d['roster_positions'] for d in leagues]
    settings_name = dict(zip(league_name_list, settings_list))
    scoring_settings_name = dict(zip(league_name_list, scoring_settings_list))
    roster_positions_name = dict(zip(league_name_list, roster_positions_list))
    option = st.selectbox(
        'Please Choose Your League',
        (league_name_list))
    if option:
        st.write(settings_name[option])
        st.write(scoring_settings_name[option])
        st.write(roster_positions_name[option])
    return settings_name, scoring_settings_name, roster_positions_name, option , league_id_list, league_name_list


if __name__ == '__main__':
    main()
from datetime import datetime
import streamlit as st
import requests
import pandas as pd
import plotly.express as px


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
    values_df = pd.read_csv('/Users/nick/sleepertoolsversion2/values/values.csv')
    players_df = pd.read_csv(
        '/Users/nick/sleepertoolsversion2/values/players.csv')
    print(values_df.info(verbose=True))
    print(rosters_df.info(verbose=True))
    rosters_df = rosters_df[rosters_df['players'].str.isnumeric()]
    rosters_df['players'] = rosters_df['players'].astype(int)
    rosters_values_df = rosters_df.merge(players_df, left_on='players', right_on='player_id', how='left')
    rosters_values_df = rosters_values_df.merge(values_df, on='merge_name')
    if option:
        st.write(rosters_values_df)

        fig = px.histogram(rosters_values_df
                           , x="display_name", y="HIM VALUE", hover_data=['full_name'])
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)



        fig = px.histogram(rosters_values_df, x="display_name", y='HIM VALUE', color='position', barmode='group')
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)


    return rosters_values_df

if __name__ == '__main__':
    main()

from datetime import datetime
import streamlit as st
import requests
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go





def main():
    st.title('Data, Bitch')
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
    response = requests.get(f'https://api.sleeper.app/v1/user/{user_id}/leagues/nfl/{current_year}')
    leagues = response.json()
    league_id_list = [d['league_id'] for d in leagues]
    league_name_list = [d['name'] for d in leagues]
    draft_id_list = [d['draft_id'] for d in leagues]

    option = st.selectbox(
        'Please Choose Your League',
        (league_name_list), index=2 )

    # Load data into a pandas DataFrame
    # Create a multiselect widget
    positions = ["QB", "RB", "WR",'TE']
    selected_positions = st.multiselect("Select Positions", positions)

    # Filter the DataFrame based on the selected options


    # Display the filtered DataFrame

    league_name_id = dict(zip(league_name_list, league_id_list))
    league_name_draft_id = dict(zip(league_name_list, draft_id_list))

    league_id = league_name_id[option]
    draft_id = league_name_draft_id[option]

    response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/rosters')
    rosters = response.json()
    response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/users')

    users = response.json()
    users_df = pd.DataFrame(users)

    rosters_df = pd.DataFrame(rosters)
    rosters_df_trim = rosters_df[['owner_id', 'roster_id', 'players']]

    users_df_trim = users_df[['user_id', 'display_name']]
    rosters_df = rosters_df_trim.merge(users_df_trim, left_on='owner_id', right_on='user_id')
    rosters_draft_df = rosters_df[['owner_id','roster_id','display_name']]
    rosters_df = rosters_df[['display_name', 'players']]

    rosters_df = rosters_df.explode('players').reset_index(drop=True)

    response = requests.get(f'https://api.sleeper.app/v1/draft/{draft_id}')
    draft_order = response.json()['draft_order']


    draft_order_df = pd.DataFrame.from_dict(draft_order, orient='index', columns=['Pick'])

    #combining draft order with rosters
    picks_df = rosters_draft_df.merge(draft_order_df, left_on='owner_id', right_index=True)
    picks_df = picks_df.sort_values(by=['Pick'])
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
            return date.today().year
        elif row['range'] > 60 and row['range'] <= 120:
            return date.today().year + 1
        elif row['range'] > 120 and row['range'] <= 180:
            return date.today().year + 2

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


    def merge_name(year, rnd):
            return f"{year}{rnd}"




    draft_order_df = draft_order_df.dropna()

    # creating a table with the original owner id and the year and round of the pick
    draft_order_df = draft_order_df[['roster_id', 'display_name', 'Year', 'Round', 'Pick', 'range']]
    draft_order_df = draft_order_df.rename(columns={'roster_id': 'original_owner_id'})
    draft_order_df['new_owner_id'] = draft_order_df['original_owner_id']
    response = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/traded_picks')
    trade = response.json()

    trade_df = pd.DataFrame(trade)


    trade_shuffle_df = trade_df[['owner_id', 'roster_id', 'season', 'round']].astype(int)
    trade_shuffle_df = trade_shuffle_df[trade_shuffle_df['season']!=previous_year]
    trade_shuffle_df = trade_shuffle_df.rename(columns={'roster_id': 'original_owner_id', 'owner_id': 'new_owner_id', 'season': 'Year', 'round': 'Round'})
    picks_df = picks_df.rename(columns={'roster_id': 'original_owner_id'})
    picks_df['original_owner_id'] = picks_df['original_owner_id'].astype(int)
    trade_shuffle_df['original_owner_id'] = trade_shuffle_df['original_owner_id'].astype(int)
    picks_df = picks_df[['original_owner_id', 'display_name', 'Pick']]

    trade_shuffle_df = trade_shuffle_df.merge(picks_df, how='left', on='original_owner_id')
    draft_order_df['Round'] = draft_order_df['Round'].astype(int)
    # #
    draft_order_df = draft_order_df[['original_owner_id', 'display_name', 'Year', 'Round', 'Pick', 'range']]
    draft_trade_df = pd.merge(draft_order_df, trade_shuffle_df, on=['Year', 'Round', 'Pick'], how='left')
    # #
    # # # do I need to add the drat order to this dataframe before merging? It think this will help me re order the picks.
    # #
    draft_trade_df.sort_values(by='range')

    draft_trade_df['new_owner_id'].fillna(draft_trade_df['original_owner_id_x'], inplace=True)

    draft_trade_df['display_name_y'].fillna(draft_trade_df['display_name_x'], inplace=True)

    final_draft_order_df = draft_trade_df[['new_owner_id', 'Year', 'Round', 'Pick']]

    final_draft_order_df = final_draft_order_df.rename(columns={'new_owner_id': 'roster_id'})
    final_draft_order_df = final_draft_order_df.merge(rosters_draft_df, how='left', on='roster_id')

    final_draft_order_df["pick_concat"] = final_draft_order_df.Pick.map("{:02}".format)

    final_draft_order_df['merge_name'] = final_draft_order_df.apply(lambda row: merge_name(row['Year'], row['Round']), axis=1)
    final_draft_order_df['full_name'] =  final_draft_order_df['Year'].astype(str) + " " + "Pick" + " " + final_draft_order_df['Round'].astype(str) + "." + \
                                          final_draft_order_df['pick_concat']
    final_draft_order_df['position'] = 'Pick'

    final_draft_order_df['team'] = 'Draft'
    final_draft_order_df = final_draft_order_df[['display_name','full_name','merge_name','position','team']]
    values_df = pd.read_csv('/Users/nick/sleepertoolsversion2/values/values.csv')
    players_df = pd.read_csv(
        '/Users/nick/sleepertoolsversion2/values/player_urls.csv')
    rosters_df = rosters_df[rosters_df['players'].str.isnumeric()]
    rosters_df['players'] = rosters_df['players'].astype(int)
    rosters_values_df = rosters_df.merge(players_df, left_on='players', right_on='player_id', how='left')
    rosters_values_df = rosters_values_df[['display_name','full_name','merge_name','position','team_logo_espn','headshot_url']]
    rosters_values_df.dropna(subset=['full_name'], inplace=True)
    rosters_values_df = pd.concat([final_draft_order_df,rosters_values_df])
    rosters_values_df = rosters_values_df.merge(values_df, on='merge_name')
    rosters_values_df.sort_values(by=['HIM RANK'], inplace=True)
    rosters_values_df['HIM RANK'] = rosters_values_df['HIM RANK'].astype(int)

    rosters_values_df['Pos Rank'] = rosters_values_df.groupby('position')['HIM RANK'].cumcount() + 1

    rosters_table_df = rosters_values_df[['HIM RANK', 'display_name','headshot_url','full_name','Pos Rank','position','team_logo_espn']]

    rosters_table_df['headshot_url'] =  rosters_table_df['headshot_url'] \
        .str.replace(
        '(.*)',
        '<img src="\\1" style="max-height:62px;"></img>')
    rosters_table_df['team_logo_espn'] = rosters_table_df['team_logo_espn'] \
        .str.replace(
        '(.*)',
        '<img src="\\1" style="max-height:62px;"></img>')
    rosters_table_df.rename(columns={'display_name':'Manager','full_name':"Name", 'position':'Pos','team_logo_espn':'team','headshot_url':''}, inplace=True)


    min_rank, max_rank = rosters_table_df['HIM RANK'].min(), rosters_table_df['HIM RANK'].max()

    range_slider = st.slider('Select a range of rankings', min_value=int(min_rank), max_value=int(max_rank),
                             value=(int(min_rank), int(100)), step=int(1))
    rosters_table_df = rosters_table_df[(rosters_table_df['HIM RANK'] > range_slider[0]) & (rosters_table_df['HIM RANK'] <= range_slider[1])]

    if len(selected_positions) > 0:
        rosters_table_df = rosters_table_df[rosters_table_df["Pos"].isin(selected_positions)]

    else:
        rosters_table_df = rosters_table_df


    html = (rosters_table_df
                .style \
                .format({

            'HIM RANK': '{:.0f}'.format,

        }) \
                .set_properties(
            **{'font': 'Bebas Neue', 'font-weight': 'bold', 'font-size': '16px',
               'padding': '5px'}) \
                # .set_table_styles([{'selector': 'th', 'props': [('background-color', '#30b5fd'),('font-size','20px'),('color','white'),('padding','5px')]}])\
                .set_sticky(axis=1) \
                .hide_index() \
                .render()
                )

    if option:
        st.title('OVERALL HIM RANKING')
        st.write(
            'HIM RANK determined by aggregated market values')
        st.markdown(html, unsafe_allow_html=True)
        st.title('TOTAL HIM VALUE')
        fig = px.histogram(rosters_values_df
                           , x="display_name", y="HIM VALUE", hover_data=['full_name'])
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        fig.update_layout(xaxis_title='Manager', yaxis_title='Total HIM VALUE')
        fig.update_traces(marker_color='#fc6f03')

        st.plotly_chart(fig, use_container_width=True)
        avg_by_position = rosters_values_df.groupby('position')['HIM VALUE'].mean().reset_index
        df = rosters_values_df[['display_name','position','HIM VALUE']]
        df.rename(columns={'display_name': 'Manager','position':'Position'},inplace=True)
        avg_values = df.groupby(['Manager', 'Position'])['HIM VALUE'].mean().reset_index()
        avg_values = avg_values.groupby('Position')['HIM VALUE'].mean().reset_index()

        # create the streamlit app
        st.title('Manager Value by Position')
        st.write(
            'Select a manager from the dropdown menu to see their total value at each position and how they compare to the average manager value at each position.')

        # create the dropdown menu
        managers = df['Manager'].unique()
        selected_manager = st.selectbox('Select a manager', managers)

        # filter the dataframe by the selected manager
        manager_df = df[df['Manager'] == selected_manager]
        manager_df = manager_df.groupby('Position')['HIM VALUE'].mean().reset_index()


        # merge with the average values dataframe

        # create the plotly chart
        trace1 = go.Bar(x=manager_df['Position'], y=manager_df['HIM VALUE'],
                        name=selected_manager, marker={'color': '#9403fc'})
        trace2 = go.Bar(x=avg_values['Position'], y=avg_values['HIM VALUE'],
                        name='Average', marker={'color': '#03fc2c'})

        # create layout and figure
        layout = go.Layout(title=f"{selected_manager}'s Average Value by Position Compared to the Average Manager Value by Position",
                           xaxis={'title': 'Position'},
                           yaxis={'title': 'AVG Value'},
                           barmode='group')
        fig = go.Figure(data=[trace1, trace2], layout=layout)
        st.plotly_chart(fig)

    return rosters_values_df

if __name__ == '__main__':
    main()
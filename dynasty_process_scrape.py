import pandas as pd
import unidecode as unidecode
from cmath import exp
import re

df = pd.read_csv(
    'https://raw.githubusercontent.com/dynastyprocess/data/master/files/values-players.csv')
# new_header = dynasty_process_player_values_df.iloc[0] #grab the first row for the header
# dynasty_process_player_values_df = dynasty_process_player_values_df[1:] #take the data less the header row
# dynasty_process_player_values_df.columns = new_header #set the header row as the df header
dynasty_process_player_values_df = df[['player', 'pos', 'team', 'age', 'value_2qb']]
dynasty_process_player_values_df['value_2qb'] = dynasty_process_player_values_df['value_2qb'].astype(float)


dynasty_process_pick_values_df = pd.read_csv(
    'https://raw.githubusercontent.com/dynastyprocess/data/master/files/values-picks.csv')

dynasty_process_pick_values_df['age'] = '21'
dynasty_process_pick_values_df['team'] = 'FA'
dynasty_process_pick_values_df.rename(columns={'ecr_2qb': 'value_2qb'}, inplace=True)
dynasty_process_pick_values_df = dynasty_process_pick_values_df[['player', 'pos', 'team', 'age', 'value_2qb']]

values_df = pd.concat([dynasty_process_player_values_df, dynasty_process_pick_values_df])
values_df['scrape_date'] = pd.Timestamp.today()

values_df['scrape_date'] = values_df['scrape_date'].dt.floor('d')
values_df.rename(columns={'age': 'dypro_age'}, inplace=True)

df = values_df
df['full_name'] = df['player']
df['position'] = df['pos']

## REFORMAT PLAYER NAMES BY REMOVING NON-ALPHA-NUMERICS
df["first_name"] = df.full_name.apply(lambda x: x.split(" ")[0])
df["last_name"] = df.full_name.apply(lambda x: " ".join(x.split(" ")[1::]))

# Remove non-alpha numeric characters from first/last names.
df["first_name"] = df.first_name.apply(
    lambda x: "".join(c for c in x if c.isalnum())
)
df["last_name"] = df.last_name.apply(
    lambda x: "".join(c for c in x if c.isalnum())
)

# Recreate full_name to fit format "Firstname Lastname" with no accents
df["full_name"] = df.apply(
    lambda x: x.first_name + " " + x.last_name, axis=1
)
df["full_name"] = df.full_name.apply(lambda x: x.lower())
df.drop(["first_name", "last_name"], axis=1, inplace=True)
df.loc[df.position != "PICK", "full_name"] = df.loc[
    df.position != "PICK"
    ].full_name.apply(
    lambda x: x.split(" ")[0][0].upper()
              + x.split(" ")[0][1::]
              + " "
              + x.split(" ")[-1][0].upper()
              + x.split(" ")[-1][1::]
)
df["full_name"] = df.full_name.apply(lambda x: unidecode.unidecode(x))

# Create Column to match with RotoGrinders
df["merge_name"] = df.full_name.apply(
    lambda x: x.lower().split(" ")[0][0:4] + x.lower().split(" ")[1][0:6]
)

regex = re.compile(r'\d+')

# create a boolean mask that identifies which rows have numbers in the "merge name" column
has_numbers = df['merge_name'].str.contains(regex)

# apply the regular expression to the selected rows using the str.replace() method
df.loc[has_numbers, 'merge_name'] = df.loc[has_numbers, 'merge_name'].apply(lambda x: re.sub(r'[a-zA-Z]', '', x))
df['dypro_name'] = df['player']
df['DyPro Rank'] = df['value_2qb'].rank(ascending=False, method='average')
df['DyPro Value'] = round(df['DyPro Rank'].apply(lambda x : 10500 * exp(x* - 0.0235)),0)
df['DyPro Value'] = df['DyPro Value'].astype(float)
df.sort_values(by='DyPro Value', ascending=False, inplace=True)
df = df.groupby(['merge_name', 'dypro_age', 'pos'])[['DyPro Value','DyPro Rank']].median().reset_index()
df = df[['merge_name','dypro_age','DyPro Value','pos','DyPro Rank']]

df.to_csv('/Users/nick/sleepertoolsversion2/values/dypro_values.csv', index=False)

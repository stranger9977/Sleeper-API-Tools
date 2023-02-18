import pandas as pd
import requests as requests
import unidecode as unidecode

response = requests.get("https://api.sleeper.app/v1/players/nfl")
data = response.json()

df = pd.DataFrame.from_dict(data)

df = df.transpose()

df = df.reset_index()

# Rename the column
df = df.rename(columns={'index': 'id'})



df['scrape_date'] = pd.Timestamp.today()
df['scrape_date'] = df['scrape_date'].dt.floor('d')
df = df[['player_id','full_name', 'position','team']]
df['full_name'] =df['full_name'].astype(str)


# ## REFORMAT PLAYER NAMES BY REMOVING NON-ALPHA-NUMERICS
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
df.loc[df.position != "DEF", "full_name"] = df.loc[
    df.position != "DEF"
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
    lambda x: x.lower().split(" ")[0][0:4] + x.lower().split(" ")[1][0:5]
)
df = df[['player_id','full_name','merge_name','position','team']]
df = df[df['position'].isin(['QB','WR','TE','RB'])]
df.to_csv('/Users/nick/sleepertoolsversion2/values/players.csv', index=False)

#
# # players_df = players_df.transpose()


#this program will scrape values from keeptradecut and clean the data set for modeling
import requests
import unidecode as unidecode
from bs4 import BeautifulSoup
import pandas as pd
from cmath import exp



def get_ktc_values():
    url = 'https://keeptradecut.com/dynasty-rankings'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find(id="rankings-page-rankings")
    players = results.find_all("div", class_="onePlayer")

    name_list = []
    value_list = []
    position_list =[]
    for player in players:
        name = (player.find("p", class_="player-name").text.strip())
        value = (player.find("p", class_="value").text.strip())
        position = (player.find("p", class_="position").text.strip())
        name_list.append(name)
        value_list.append(value)
        position_list.append(position)
    Player_lists_to_dicts = {"Player": name_list, 'KTC Value': value_list,'pos':position_list}

    df = pd.DataFrame(Player_lists_to_dicts)
    df['scrape_date'] = pd.Timestamp.today()
    df['scrape_date'] = df['scrape_date'].dt.floor('d')
    df['full_name'] = df['Player']
    df['position'] = df['pos'].str.replace('\d', '')
    df['full_name'].replace({'Gabriel Davis': 'Gabe Davis'}, inplace=True)

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
            lambda x: x.lower().split(" ")[0][0:4] + x.lower().split(" ")[1][0:5]
        )

    df['ktc_name'] = df['Player']
    df['KTC Value']= df['KTC Value'].astype(float)
    df.sort_values(by='KTC Value', ascending=False,inplace=True)
    df['KTC Rank'] = df['KTC Value'].rank(ascending=False, method='min')
    df['KTC Value'] = round(df['KTC Rank'].apply(lambda x: 10500 * exp(x * - 0.0235)), 0)
    df['KTC Value'] = df['KTC Value'].astype(float)
    df.sort_values(by='KTC Value', ascending=False, inplace=True)
    df = df[['ktc_name', 'merge_name', 'KTC Value','KTC Rank']]
    df.to_csv('/Users/nick/sleepertoolsversion2/values/ktc_values.csv', index=False)


get_ktc_values()


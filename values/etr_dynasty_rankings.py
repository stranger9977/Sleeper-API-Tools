
import pandas as pd
import html5lib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import unidecode as unidecode
from cmath import exp



driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


# from user_agent import random_header
pd.set_option("display.max_columns", 99)
pd.set_option("display.max_columns", 99)





# set url
url = 'https://establishtherun.com/wp-login.php?redirect_to=%2Fx'

driver.get(url)
username = 'nick.gurol'
password = "22eTyS8JUx!fben"
# # login to website
driver.find_element(By.ID, "user_login").send_keys(username)
driver.find_element(By.ID, "user_pass").send_keys(password)
driver.find_element(By.ID, "wp-submit").click()

# wait the ready state to be complete
WebDriverWait(driver=driver, timeout=10).until(
    lambda x: x.execute_script("return document.readyState === 'complete'")
)
driver.get('https://establishtherun.com/2022-dynasty-rankings/')

page_source = driver.page_source

soup = page_source

df = pd.read_html(driver.page_source,flavor='html5lib')[1]

df['full_name'] = df['Player']
df['full_name'].replace({'Gabriel Davis':'Gabe Davis'}, inplace=True)

df['position'] = df['Position']

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

df['etr_name'] = df['Player']

df['ETR Rank'] = df['SF/TE Prem'].rank(ascending=True, method='average')
df['ETR Value'] = round(df['ETR Rank'].apply(lambda x : 10500 * exp(x* - 0.0235)),0)
df['ETR Value'] = df['ETR Value'].astype(float)
df.sort_values(by='ETR Value', ascending=False, inplace=True)
df = df[['etr_name','merge_name','ETR Value','ETR Rank']]
df.to_csv('/Users/nick/sleepertoolsversion2/values/etr_ranks.csv', index=False)


#
# from datetime import datetime
# df.to_csv(f'/Users/nick/Sleeper-Dashboard/Data/etr_underdog_rankings-{datetime.now():%Y-%m-%d}.csv')
# # df3.to_csv(f'/Users/nick/Sleeper-Dashboard/Data/etr_ppr_rankings-{datetime.now():%Y-%m-%d}.csv')
#

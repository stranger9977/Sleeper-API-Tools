
import nfl_data_py as nfl
import pprint as pp
import pandas as pd
import numpy as np
import requests
import os
import io
from io import BytesIO
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.font_manager as font_manager
import matplotlib as mpl

# Load the data
visual_df = pd.read_csv('visual_df.csv')

# Sort the dataframe by Team TGT %
sorted_df = visual_df.sort_values(by='Team TGT %', ascending=False).head(15)
sorted_df['label'] = sorted_df['headshot_url'].apply(lambda x: x.split('/')[-1])

for label in sorted_df['label']:
    response = requests.get(f"https://static.www.nfl.com/image/private/f_auto,q_auto/league/{label}")
    img = Image.open(BytesIO(response.content))

    # Save the image and get the path
    img_path = f"image_directory/{label.split('/')[-1]}.png"
    img.save(img_path, quality=90)

    # Add the path to the DataFrame
    sorted_df.loc[sorted_df['label'] == label, 'image_path'] = img_path
font_path = "/Users/nick/sleepertoolsversion2/Exo/static/Exo-Bold.ttf"
exo_regular = font_manager.FontProperties(fname=font_path)

fig, ax = plt.subplots(figsize=(15, 10))

def getImage(path):
    return OffsetImage(plt.imread(path), zoom=.030)

# Add team logos
for y0, x0, path in zip(sorted_df['Name'], sorted_df['Team TGT %'] + .005, sorted_df['image_path']):
    ab = AnnotationBbox(getImage(path), (x0, y0), frameon=False, fontsize=4)
    ax.add_artist(ab)

# Add bar chart, y axis is an array from 0-31 (length of 32, one per team)
ax.barh(sorted_df['Name'], sorted_df['Team TGT %'], color=sorted_df['team_color'], height=0.5, edgecolor=sorted_df['team_color2'],
        linewidth=3)

# Add a grid across the x-axis
ax.grid(zorder=0, alpha=.5, axis='x', linewidth=3)
ax.set_axisbelow(True)
ax.axes.xaxis.set_visible(False)

# Invert y-axis
ax.invert_yaxis()

import nfl_data_py as nfl
import pprint as pp
import pandas as pd
import numpy as np
import requests
import os
import io
from io import BytesIO
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.font_manager as font_manager

# Load the data
visual_df = pd.read_csv('visual_df.csv')

# Sort the dataframe by Team TGT %
sorted_df = visual_df.sort_values(by='Team TGT %', ascending=False).head(15)
sorted_df['label'] = sorted_df['headshot_url'].apply(lambda x: x.split('/')[-1])

for label in sorted_df['label']:
    response = requests.get(f"https://static.www.nfl.com/image/private/f_auto,q_auto/league/{label}")
    img = Image.open(BytesIO(response.content))

    # Save the image and get the path
    img_path = f"image_directory/{label.split('/')[-1]}.png"
    img.save(img_path, quality=90)

    # Add the path to the DataFrame
    sorted_df.loc[sorted_df['label'] == label, 'image_path'] = img_path
font_path = "/Users/nick/sleepertoolsversion2/Exo/static/Exo-Bold.ttf"
exo_regular = font_manager.FontProperties(fname=font_path)

fig, ax = plt.subplots(figsize=(15, 10))

def getImage(path):
    return OffsetImage(plt.imread(path), zoom=.035)

# Add team logos
for y0, x0, path in zip(sorted_df['Name'], sorted_df['Team TGT %'] + .005, sorted_df['image_path']):
    ab = AnnotationBbox(getImage(path), (x0, y0), frameon=False, fontsize=4)
    ax.add_artist(ab)

# Add bar chart, y axis is an array from 0-31 (length of 32, one per team)
ax.barh(sorted_df['Name'], sorted_df['Team TGT %'], color=sorted_df['team_color'], height=0.5, edgecolor=sorted_df['team_color2'],
        linewidth=3)

# Invert y-axis
ax.invert_yaxis()
ax.set_xlim(10, 25)
# Set the font for the axis and plot titles
ax.set_xlabel('Team TGT %', fontproperties=exo_regular, fontsize=18, labelpad=20, color='#FCC331')
ax.set_facecolor('#202F52')
fig.patch.set_facecolor('#202F52')
ax.set_title('Top 15 RBs 2018-2023: Team TGT % ', fontproperties=exo_regular, fontsize=26, pad=20, fontweight='bold', loc='left', color='#FCC331')
for i, v in enumerate(sorted_df['Team TGT %']):
    ax.text(v + .50, i - 0.25, '{:.01f}%'.format(v), color='#FCC331', fontproperties=exo_regular)

# Set the color of the tick marks to #FCC331
ax.tick_params(axis='both', colors='#FCC331')

# Set the color of the border of the plot to #FCC331
for spine in ax.spines.values():
    spine.set_edgecolor('#FCC331')

# Set the background color of the figure
fig.patch.set_facecolor('#202F52')
plt.figtext(.65, .06, 'Figure: @run_the_sims | Data: nflfastR', fontsize=14, fontproperties=exo_regular, color='#FCC331')
plt.show()

plt.savefig('/Users/nick/sleepertoolsversion2/team_target_%rb.png', dpi=300, bbox_inches='tight', )











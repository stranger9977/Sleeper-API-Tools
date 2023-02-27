import pandas as pd
import numpy as np
import requests
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.font_manager as font_manager

seasons = np.arange(2022,2023).tolist()
visual_df = pd.read_csv('visual_df.csv')
visual_df = visual_df.drop_duplicates(subset='Name', keep='last')


metric_list = ['Weighted Opportunity Per Game']
# comment out for tgt share graph
# visual_df = visual_df.groupby(['Name']).max().reset_index()
#
# visual_df = visual_df.replace('nan', np.nan)
# print(visual_df.columns)

visual_df = visual_df.dropna(subset = ['headshot_url'])
for metric in metric_list:

    # Sort the dataframe by Team TGT %

    sorted_df = visual_df.sort_values(by=metric, ascending=False).head(15)

    sorted_df['label'] = sorted_df['headshot_url'].apply(lambda x: x.split('/')[-1]).astype(str).dropna()

    for label in sorted_df['label']:
        response = requests.get(f"https://static.www.nfl.com/image/private/f_auto,q_auto/league/{label}")
        img = Image.open(BytesIO(response.content))

        # Save the image and get the path
        img_path = f"image_directory/{label.split('/')[-1]}.png"
        img.save(img_path, quality=90)

        # Add the path to the DataFrame if img_path is not NaN
        if img_path != 'NaN':
            sorted_df.loc[sorted_df['label'] == label, 'image_path'] = img_path

    font_path = "/Users/nick/sleepertoolsversion2/Exo/static/Exo-Bold.ttf"

    exo_regular = font_manager.FontProperties(fname=font_path)

    fig, ax = plt.subplots(figsize=(15, 10))

    def getImage(path):
        return OffsetImage(plt.imread(str(path)), zoom=.035)

    # Add team logos

    for y0, x0, path in zip(sorted_df['Name'], sorted_df[metric] + .005, sorted_df['image_path']):

        ab = AnnotationBbox(getImage(path), (x0, y0), frameon=False, fontsize=4)

        ax.add_artist(ab)

    # Add bar chart, y axis is an array from 0-31 (length of 32, one per team)

    ax.barh(sorted_df['Name'], sorted_df[metric], color=sorted_df['team_color'], height=0.5, edgecolor=sorted_df['team_color2'],

            linewidth=3)

    # Invert y-axis

    ax.invert_yaxis()

    min_value = sorted_df[metric].min()
    max_value = sorted_df[metric].max()

    # Calculate the range for the xlim
    xlim_range = max_value - min_value

    # Set the xlim for the plot
    ax.set_xlim(min_value - 2, max_value + 2)

    # Set the font for the axis and plot titles

    ax.set_xlabel(metric, fontproperties=exo_regular, fontsize=18, labelpad=20,  y=-1)
    print(seasons)
    ax.set_title(f'Top 15 RBs: {metric}, {seasons[0]} - {seasons[len(seasons)-1]}', fontproperties=exo_regular, fontsize=26,pad=20, fontweight='bold', loc='left')
    plt.suptitle(
        'Opportunity Weights: RedZone Carry = 1.35, RedZone Target = 2.29, Carry Outside the RedZone = 0.49, Target Outside the RedZone = 1.48')
    if '%' in metric:
        # Set the format string for percentage values
        format_str = '{:.02f}%'
    else:
        # Set the format string for non-percentage values
        format_str = '{:.1f}'
    for i, v in enumerate(sorted_df[metric]):
        # Calculate the position of the label based on the xlim

        ax.text(v+0.15, i - 0.01, format_str.format(v), fontproperties=exo_regular)

    # Set the color of the tick marks to #FCC331

    ax.tick_params(axis='both')

    # Set the color of the border of the plot to #FCC331

    # Set the background color of the figure

    plt.figtext(.65, .06, 'Figure: @run_the_sims | Data: nflfastR', fontsize=14, fontproperties=exo_regular)

    plt.savefig(f'/Users/nick/sleepertoolsversion2/{metric}-2022.png', dpi=300, bbox_inches='tight')

    plt.show()
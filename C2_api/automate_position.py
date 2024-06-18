import re
import config
import pandas as pd
from datetime import datetime
import json
import paho.mqtt.client as mqtt
import time
import os
from glob import glob
from api_modules import *
from tqdm import tqdm
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from matplotlib_scalebar.scalebar import ScaleBar
import time


while True:
    ############################################
    ######### Glider Position ##################
    ############################################
    gliders_id_list = ['unit_397', 'unit_405', 'unit_398', 'unit_345']
    glider_position = pd.DataFrame({'date' : [], 'lon' : [], 'lat' : [], 'platform_type' : str(), 'platform_id' : str()})

    for glider_id in gliders_id_list :
        positions = get_positions(config.token, platform_type = "slocum", platform_serial = glider_id)
        position_df = convert_positions(positions)

        #recent_position = position_df.head(7)

        glider_data = []
        for _, row in position_df.iterrows():
            date_row = pd.to_datetime(row['time'])
            if date_row > pd.to_datetime('2024-05-29T00:00:00Z'):
                glider_data.append({
                    'date': date_row.strftime('%Y-%m-%d %H:%M:%S'),
                    'lon': row['longitude'],
                    'lat': row['latitude'],
                    'platform_type': 'glider',
                    'platform_id': glider_id
                })
            else:
                break

        # Convert the list of dictionaries to a DataFrame
        glider_temp_position = pd.DataFrame(glider_data)
        glider_position = pd.concat([glider_position if not glider_position.empty else None, glider_temp_position], ignore_index=True)
        print(f'retrieved {glider_id} position')

    print(f'Glider position updated and formatted')

    #########################################
    ###  Ship Position dataframe     ########
    #########################################

    print(f'Ignoring Ship position')
    ##########################################
    ###### Float position dataframe ##########
    ##########################################

    my_files = glob('Data/Floats/cts5_emails/*')
    floats_position = pd.DataFrame({'date' : [], 'lon' : [], 'lat' : [], 'platform_type' : str(), 'platform_id' : str()})
    for file in my_files:
        temp_df = email_to_csv_pos(file)
        floats_position = pd.concat([floats_position if not floats_position.empty else None, temp_df], ignore_index=True)

    print(f'Float position updated and formatted')


    ###########################################
    ########### Respire dataframe ############
    ##########################################

    print(f'ignore respire')
    ##########################################
    ######## Bind all the positions df #######
    ##########################################

    combined_positions = pd.concat([glider_position, floats_position])

    #combined_position.to_csv('Plotting_tools/shared_data/rt_positions.csv')

    print(f'position for all 3 components written in Plotting_tools/shared_data/rt_positions.csv')

    platform_mask = {
            'Ship':  'x',
            'glider': '^',
            'Float':  'o',
            'respire': '>'}

    platform_colors = {
            'Discovery':  'black',
            'unit_405': '#b2182b',
            'unit_397':  '#f4a582',
            'unit_398': '#d6604d',
            'unit_345': '#fddbc7',
            'lovuse031c': '#92c5de',
            'lovuse032c': '#4393c3',
            'lovuse026d': '#2166ac',
            'respire': '#b8e186'}

    def get_color(platform_id):
        return platform_colors.get(platform_id, 'black')

    combined_positions['color'] = combined_positions['platform_id'].apply(get_color)

    max_lon = combined_positions['lon'].max() + 0.05
    min_lon = combined_positions['lon'].min() - 0.05
    max_lat = combined_positions['lat'].max() + 0.05
    min_lat = combined_positions['lat'].min() - 0.05

    current_time = datetime.now()
    now = current_time.strftime(format = '%Y-%m-%d %H:%M:%S')

    combined_positions['datetime'] = pd.to_datetime(combined_positions['date'])
    positions_from_start = combined_positions[combined_positions['datetime'] > pd.to_datetime('2024-05-30 20:00:00')]
    floats_positions = combined_positions[combined_positions['platform_type'] == 'Float']
    dates_of_gliders = positions_from_start[positions_from_start['platform_type'] == 'glider']['date'].unique()

    for i in tqdm(dates_of_gliders):
        temp = combined_positions[combined_positions['datetime']< pd.to_datetime(i)]
        temp = temp.loc[temp.groupby('platform_id')['datetime'].idxmax()]
        datename = i.replace(" ", "_").replace(":", "").replace("-", "")
        filename = 'C:/Users/flapet/OneDrive - NOC/DY180_NRT_plots/rt_tracking/automatic_plots/rt_tracking_' + datename + '.png'


        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())

                            # Set the map extent based on your latitude and longitude ranges
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())


        for platform_type, mask in platform_mask.items():
            subset = temp[temp['platform_type'] == platform_type]
            for platform_id, color in platform_colors.items():
                sub_subset = subset[subset['platform_id'] == platform_id]
                if not sub_subset.empty:
                    ax.scatter(sub_subset['lon'], sub_subset['lat'], c=color, label=platform_id, marker=mask, s=100, transform=ccrs.PlateCarree())
                    for index, row in sub_subset.iterrows():
                        ax.annotate(str(row['date']), (row['lon'], row['lat']), transform=ccrs.PlateCarree())

        ax.scatter(-24, 60, label = 'Station 1', marker = 'X', c = 'Black', transform = ccrs.PlateCarree(), s = 200)

        # Add a scale bar
        ax.add_artist(ScaleBar(1, location = "lower left"))

        # Add gridlines and labels
        gl = ax.gridlines(draw_labels=True)
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 10}
        gl.ylabel_style = {'size': 10}
        gl.top_labels=False   # suppress top labels
        gl.right_labels=False # suppress right labels

        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title(f'Platform Positions \n {i}')

        plt.legend(title='Platform ID', bbox_to_anchor=(1.05, 1), loc='upper left')  # Adjust the coordinates as needed

        plt.savefig(filename)
        plt.close()
    time.sleep(900)
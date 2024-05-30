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
        if date_row > pd.to_datetime('2024-05-27T00:00:00Z'):
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

############################################
########## Ship position update ############
############################################

# CConfiguration of the MQTT broker
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(config.username, config.password)
client.on_connect = mqtt_connect
client.on_message = download_data

# Connexion to the broker
client.connect(config.broker, config.port, 60)

# Start the network loop in a separate thread
client.loop_start()

# Collect data for 1 seconds
time.sleep(1)

#Stop the network loop and disconnect
client.loop_stop()
client.disconnect()

#########################################
###  Ship Position dataframe     ########
#########################################

my_files = glob('Data/Ship_position/raw_msg/*')
ship_position = pd.DataFrame({'date' : [], 'lon' : [], 'lat' : [], 'platform_type' : str(), 'platform_id' : str()})
for file in my_files:
    temp_df = json_to_csv_pos(file)
    ship_position = pd.concat([ship_position if not ship_position.empty else None, temp_df], ignore_index=True)

print(f'Ship position updated and formatted')
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

respire = pd.read_csv('Data/Respire/raw_location_respire.csv')
input_format = '%b %d %Y %I:%M:%S.%f %p'

respire['Datetime'] = pd.to_datetime(respire['Timestamp'], format=input_format)

# Ensure microseconds are dropped by converting to string and back to datetime without microseconds
respire['Datetime'] = respire['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
respire['Datetime'] = pd.to_datetime(respire['Datetime'], format='%Y-%m-%d %H:%M:%S')


respire_sel = respire[['Datetime', 'Longitude', 'Latitude']]

colnames = ['date', 'lon', 'lat']

respire_sel.columns = colnames

respire_sel = respire_sel.copy()

respire_sel.loc[:,'platform_type'] = 'respire'
respire_sel.loc[:,'platform_id'] = 'respire'

print(f'respire position formatted')
##########################################
######## Bind all the positions df #######
##########################################

combined_position = pd.concat([ship_position, glider_position])
combined_position = pd.concat([combined_position, floats_position])
combined_position = pd.concat([combined_position, respire_sel])

combined_position.to_csv('Plotting_tools/shared_data/rt_positions.csv')

print(f'position for all 3 components written in Plotting_tools/shared_data/rt_positions.csv')
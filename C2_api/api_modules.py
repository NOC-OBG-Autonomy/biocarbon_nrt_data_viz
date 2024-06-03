import requests
import re
import config
import pandas as pd
from datetime import datetime
import json
import paho.mqtt.client as mqtt
import time
import os
from glob import glob
import io
def get_positions(token, platform_type, platform_serial):
    api_url = "https://api.c2.noc.ac.uk/positions/positions" 


    # Headers including the token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
    "platform_type": platform_type,
    "platform_serial": platform_serial
    }

    # Making my query
    response = requests.get(api_url, headers=headers, params = params)

    # Check the status code of the response
    if response.status_code == 200:
        # Successful request
        data = response.json()
        return(data[0])
    else:
        # Handle errors
        print(f"Error: {response.status_code}")
        print(response.text)

def convert_positions(json_pos):
    import pandas as pd
    data = pd.DataFrame(json_pos)
    my_pos = data['positions'].iloc[0]
    data_cleaned = pd.DataFrame(my_pos)
    return(data_cleaned)

def mqtt_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe("DY/POSMV/data/GPGGA")
    else:
        print("Failes to connect, error:", rc)

def download_data(client, userdata, msg):
    print(f"Message received from {msg.topic}: {msg.payload.decode()}")
    
    data = {
        "timestamp": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "topic": [msg.topic],
        "message": [msg.payload.decode()]
    }
    df = pd.DataFrame(data)
    
    #Convert df into json
    json_data = df.to_json(orient='records', lines=True)
    
    filename = f"mqtt_message_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path_to_save = os.path.join('Data/Ship_position/raw_msg', filename)
    with open(path_to_save, 'w') as file:
        file.write(json_data)
    
    print(f"Message saved in {path_to_save}")

def extract_datetime(json_string):
    
    datetime_pattern = r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})'

    match = re.search(datetime_pattern, json_string)
    
    if not match:
        raise ValueError(f"No datetime found in the filename: {jsom_string}")

    date_str = match.group(1)
    time_str = match.group(2)
    
    # Combine date and time strings
    datetime_str = date_str + ' ' + time_str
    
    # Convert the combined string to a datetime object
    dt = pd.to_datetime(datetime_str)
    return(dt)


def convert_to_decimal(degrees, minutes):
    """Convert degrees and minutes to decimal degrees."""
    return degrees + (minutes / 60)


def extract_lonlat(json_string):
    """Parse GPGGA string to extract and convert latitude and longitude."""
    # Define regex pattern to match GPGGA string
    pattern = r'\$GPGGA,\d+\.\d+,(?P<lat>\d{2})(?P<lat_min>\d{2}\.\d+),(?P<lat_dir>[NS]),(?P<lon>\d{3})(?P<lon_min>\d{2}\.\d+),(?P<lon_dir>[EW])'
    
    match = re.search(pattern, json_string)
    
    if not match:
        raise ValueError("Invalid GPGGA string format")
    
    # Extract latitude and longitude parts
    lat_deg = int(match.group('lat'))
    lat_min = float(match.group('lat_min'))
    lat_dir = match.group('lat_dir')
    
    lon_deg = int(match.group('lon'))
    lon_min = float(match.group('lon_min'))
    lon_dir = match.group('lon_dir')
    
    # Convert to decimal degrees
    lat_decimal = convert_to_decimal(lat_deg, lat_min)
    lon_decimal = convert_to_decimal(lon_deg, lon_min)
    
    # Adjust for direction
    if lat_dir == 'S':
        lat_decimal = -lat_decimal
    if lon_dir == 'W':
        lon_decimal = -lon_decimal
    
    return lat_decimal, lon_decimal

def json_to_csv_pos(filename):

    # Open and read the JSON file
    with open(filename, 'r') as file:
        data = json.load(file)

    # Extract the "message" variable
    message = data.get('message')
    date = extract_datetime(message)
    lat, lon = extract_lonlat(message)
    position_info = {
    'date': date,
    'lon': lon,
    'lat': lat,
    'platform_type': 'Ship',
    'platform_id': 'Discovery'
    }
    position_df = pd.DataFrame([position_info])
    return(position_df)

def read_cts_datetime(filepath):
    with open(filepath, 'r') as file:
        file_content = file.read()
    datetime_pattern = r'UTC=3D(\d{2}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})'

    match = re.search(datetime_pattern, file_content)
    
    if not match:
        raise ValueError(f"No datetime found in the file : {file_content}")

    date_str = match.group(1)
    time_str = match.group(2)

    # Combine date and time strings
    datetime_str = date_str + ' ' + time_str
    
    # Convert the combined string to a datetime object
    dt = pd.to_datetime(datetime_str, format = '%y-%m-%d %H:%M:%S')
    return(dt)

def read_cts_position(filepath):
    with open(filepath, 'r') as file:
        file_content = file.read()
    
    pattern = r'Lat=3D(?P<lat>\d{2})(?P<lat_min>\d{2}\.\d+)(?P<lat_dir>[NS]) Long=3D(?P<lon>\d{3})(?P<lon_min>\d{2}\.\d+)(?P<lon_dir>[EW])'
    
    match = re.search(pattern, file_content)
    
    if not match:
        raise ValueError("Invalid CTS5 format")
    
    # Extract latitude and longitude parts
    lat_deg = int(match.group('lat'))
    lat_min = float(match.group('lat_min'))
    lat_dir = match.group('lat_dir')
    
    lon_deg = int(match.group('lon'))
    lon_min = float(match.group('lon_min'))
    lon_dir = match.group('lon_dir')
    
    # Convert to decimal degrees
    lat_decimal = convert_to_decimal(lat_deg, lat_min)
    lon_decimal = convert_to_decimal(lon_deg, lon_min)
    
    # Adjust for direction
    if lat_dir == 'S':
        lat_decimal = -lat_decimal
    if lon_dir == 'W':
        lon_decimal = -lon_decimal
    
    return lat_decimal, lon_decimal

def email_to_csv_pos(email_path):
    date = read_cts_datetime(email_path)
    lat, lon  = read_cts_position(email_path)

    position_info = {
    'date': date,
    'lon': lon,
    'lat': lat,
    'platform_type': 'Float',
    'platform_id': email_path[-17:-7]
    }
    position_df = pd.DataFrame([position_info])
    return(position_df)

def get_observations(token, platform_type, platform_serial, variables):
    api_url = "https://api.c2.noc.ac.uk/timeseries/observations/csv" 


    # Headers including the token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
    "platform_type": platform_type,
    "platform_serial": platform_serial,
    "from": "2024-05-28T18:57",
    "variable": variables
    }

    # Making my query
    response = requests.get(api_url, headers=headers, params = params)

    # Check the status code of the response
    if response.status_code == 200:
        # Successful request
        data = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(data))
        return(df)
    else:
        # Handle errors
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == '__main__':

    test = get_observations(config.token, 'slocum', 'unit_397', variables = ["m_water_vy", "m_water_vx", "m_final_water_vx", "m_final_water_vy"])
    test.to_csv('response.csv')
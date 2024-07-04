from api_modules import *
import os
import config
import json
from datetime import datetime
import geopy.distance
import numpy as np

def write_waypoints(filename, current_date, lon, lat, commit, message_to_pilote):
    """Modify the JSON standard C2 format to send gliders waypoints

    Args:
        filename (str): The name of the json file associated to the glider that need a wpt update
        current_date (str): the date to apply on the commit
        lon (float): longitude in decimal degrees
        lat (float): latitude in decimal degrees
        commit (str): the message to describe the change
        message_to_pilote (str): the message that is sent to the pilote
    """
    # Open and read the JSON file

    with open(filename, 'r') as file:
        data = json.load(file)

    data["Bodies"][0]['waypoints update'][0]['behaviours'][0]['parameters']['target_position']['latitude'] = lat
    data["Bodies"][0]['waypoints update'][0]['behaviours'][0]['parameters']['target_position']['longitude'] = lon
    data["Bodies"][0]['waypoints update'][0]['behaviours'][0]['created_at'] = current_date
    data["Bodies"][0]['waypoints update'][0]['commit_message'] = commit
    data["Bodies"][0]['Update log'][0]['message'] = message_to_pilote

    with open(filename, "w") as jsonFile:
        json.dump(data, jsonFile, indent = 4)

def sending_waypoints(token, filename, plan_id):
    """Send the json file to the C2 API

    Args:
        filename (string): The filepath of the json file to send to C2
        plan_id (int): The plan ID  of the glider mission
    """

    patch_url = 'https://api-test.c2.noc.ac.uk/planner/plans/' + str(plan_id)
    post_url = 'https://api-test.c2.noc.ac.uk/logging/log'
    # Headers including the token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    with open(filename, 'r') as file:
        data = json.load(file)

    patch = data["Bodies"][0]['waypoints update'][0]
    post = data["Bodies"][0]['Update log'][0]

    params_patch = {
        "payload" : patch,
        "ID" : plan_id
    }

    params_post = {
        "payload" : post,
        "ID" : plan_id
    }

    # Making my query
    response = requests.patch(patch_url, headers=headers, json=patch)

    # Check the status code of the response
    if response.status_code == 200:
        # Successful request
        print(f"Waypoints updated")
    else:
        # Handle errors
        print(f"Error in patching: {response.status_code}")
        print(response.text)
    
    response = requests.post(post_url, headers=headers, json=post)

    if response.status_code == 200:
        # Successful request
        print(f"Loggs sent to pilote")
    else:
        # Handle errors
        print(f"Error in logging: {response.status_code}")
        print(response.text)

def get_last_coordinates(data):
    """
    Extract the last latitude and longitude from the JSON response.

    Args:
    data: JSON response in dictionary format.

    Returns:
    Tuple containing the last latitude and longitude.
    """
    # Extract the list of positions
    positions = data['positions']['internal']
    
    # Get the last position
    last_position = positions[-1]
    
    # Extract the latitude and longitude
    last_latitude = last_position['latitude']
    last_longitude = last_position['longitude']
    
    return last_latitude, last_longitude

def calculate_distance(lon1, lat1, lon2, lat2):
    coords1 = (lon1, lat1)
    coords2 = (lon2, lat2)
    dist = round(geopy.distance.geodesic(coords1, coords2).km, 2)
    return(dist)

def calculate_bearing(lon1, lat1, lon2, lat2):
    dx = lon2 - lon1
    dy = lat2 - lat1
    angle = np.arctan2(dx, dy)  # angle in radians
    bearing = np.degrees(angle)  # convert to degrees
    bearing = round((bearing + 360) % 360,0)  # normalize to 0-360
    return bearing

def angle_to_direction(angle):
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    # Normalize the angle to be within 0 to 360 degrees
    angle = angle % 360
    
    # Calculate the corresponding index for the directions list
    index = round(angle / 22.5) % 16
    return directions[index]

def update_waypoints(glider, lon, lat, token, message = False):
    """Combine the writting and the sending of new glider waypoints to C2. The user only need to give the glider name and the new lon lat, and a message to the pilote if needed.

    Args:
        glider (str): The name of the glider
        lon (float): the longitude in decimal degrees
        lat (float): the latitude in decimal degrees
        message (bool, optional): If True, will ask you to prompt a message to the pilote. Defaults to False.
    """
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    commit = f'WP update on {current_date}'

    files = {
        'test' : 'C2_api/json_files/test.json',
        'doombar' : 'C2_api/json_files/doombar_wpts.json'}

    IDS = {
        'test' : 799
    } 

    filename = files[glider]
    ID = IDS[glider]

    json_position = get_positions(token, platform_type = "slocum", platform_serial = "unit_398", test = True)
    current_lon, current_lat =  get_last_coordinates(json_position)

    dist = calculate_distance(current_lon, current_lat, lon, lat)
    bearing = calculate_bearing(current_lon, current_lat, lon, lat)

    direction = angle_to_direction(bearing)

    print(f"The glider will be sent to {dist}km away from its current location in a {direction} direction ({bearing} angle).")
    validation = input("Do you want to proceed ? (y/n) ")

    if validation == "n":
        print(f"abortion of waypoint sending.")
        quit()
    if validation == "y":

        if message == True:
            message_to_pilote = input("Type your message to the glider pilote : ")

        else :
            message_to_pilote = f"Waypoints generated in ID {ID} on {current_date} new waypoints ({lon},{lat}), {dist}km away."

        write_waypoints(filename, current_date, lon, lat, commit, message_to_pilote)

        sending_waypoints(token, filename, ID)
    else :
        "answer not recognised"
if __name__ == '__main__':

    glider = 'test'
    update_waypoints(glider, 0, 0, token = config.token_test)

    
    
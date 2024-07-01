from api_modules import *
import os
import config
import json
from datetime import datetime


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

    patch_url = 'https://api-test.c2.noc.ac.uk/planner/plans/' + str(plan_id) + '/'
    post_url = 'https://api-test.c2.noc.ac.uk/logging/log/'
    # Headers including the token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    with open(filename, 'r') as file:
        data = json.load(file)

    patch = data["Bodies"][0]['waypoints update']
    post = data["Bodies"][0]['Update log']

    # Making my query
    response = requests.patch(patch_url, headers=headers, params = patch)

    # Check the status code of the response
    if response.status_code == 200:
        # Successful request
        data = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(data))
        return(df)
    else:
        # Handle errors
        print(f"Error in patching: {response.status_code}")
        print(response.text)
    
    params = {
        "payload" : patch
    }
    response = requests.post(post_url, headers = headers, params = params)

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

    if message == True:
        message_to_pilote = input("Type your message to the glider pilote : ")

    else :
        message_to_pilote = f"Waypoints generated in ID {ID} and version <plan_version> new waypoints ({lon},{lat})"

    write_waypoints(filename, current_date, lon, lat, commit, message_to_pilote)

    sending_waypoints(token, filename, ID)

if __name__ == '__main__':

    glider = 'test'
    update_waypoints(glider, 24, 55, token = config.token_test, message = True)
    
    
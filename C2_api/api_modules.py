import requests
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
    my_pos = data['positions'][0]
    data_cleaned = pd.DataFrame(my_pos)
    return(data_cleaned)

def mqtt_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe("DY/POSMV/data/GPGGA")
    else:
        print("Failes to connect, error:", rc)

def download_data(client, userdata, msg):
    print(f"Message reçu sur {msg.topic}: {msg.payload.decode()}")
    
    data = {
        "timestamp": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "topic": [msg.topic],
        "message": [msg.payload.decode()]
    }
    df = pd.DataFrame(data)
    
    # Convertir le DataFrame en JSON
    json_data = df.to_json(orient='records', lines=True)
    
    filename = f"mqtt_message_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path_to_save = os.path.join('Data/Ship_position/raw_msg', filename)
    with open(path_to_save, 'w') as file:
        file.write(json_data)
    
    print(f"Message sauvegardé dans {path_to_save}")

if __name__ == '__main__':
    import config
    import pandas as pd
    from datetime import datetime
    import json
    import paho.mqtt.client as mqtt
    import time
    import os
    #positions = get_positions(config.token, platform_type = "slocum", platform_serial = "unit_306")
    #position_df = convert_positions(positions)
    #print(position_df)
    # Configuration du broker MQTT
    # Initialisation du client MQTT
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(config.username, config.password)
    client.on_connect = mqtt_connect
    client.on_message = download_data

    # Connexion to the broker
    client.connect(config.broker, config.port, 60)

    # Start the network loop in a separate thread
    client.loop_start()

    # Collect data for 10 seconds
    time.sleep(10)

    # Stop the network loop and disconnect
    client.loop_stop()
    client.disconnect()

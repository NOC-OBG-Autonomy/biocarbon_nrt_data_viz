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


if __name__ == '__main__':
    import config
    positions = get_positions(config.token, platform_type = "slocum", platform_serial = "unit_306")
    position_df = convert_positions(positions)
    print(position_df)


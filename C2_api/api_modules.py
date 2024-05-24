import requests
def get_position(token, platform_type, platform_serial):
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
        data = response.json()  # Parse the JSON response
        return(data)
    else:
        # Handle errors
        print(f"Error: {response.status_code}")
        print(response.text)

def get_positions(id):
    ...


if __name__ == '__main__':
    import config
    positions = get_position(config.token, platform_type = "slocum", platform_serial = "unit_306")


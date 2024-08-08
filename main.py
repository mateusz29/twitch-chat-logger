import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_live_channels(category_name, client_id, oauth_token) -> list[str]:
    url = 'https://api.twitch.tv/helix/games'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {oauth_token}'
    }
    params = {
        'name': category_name
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if not data['data']:
        raise ValueError(f"No category found with name '{category_name}'")
    
    category_id = data['data'][0]['id']
    
    url = 'https://api.twitch.tv/helix/streams'
    params = {
        'game_id': category_id,
        'first': 100  # maximum number of results per request
    }
    
    response = requests.get(url, headers=headers, params=params)
    channels = response.json()['data']
    
    return [channel['user_login'] for channel in channels]

def main() -> None:
    client_id = os.getenv('TWITCH_CLIENT_ID')
    oauth_token = os.getenv('TWITCH_OAUTH_TOKEN')
    category_name = 'Artifact'
    
    channels = get_live_channels(category_name, client_id, oauth_token)
    print(channels)

if __name__ == "__main__":
    main()

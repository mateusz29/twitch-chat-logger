import requests
import os
from dotenv import load_dotenv
import json

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

def send_chat_message(broadcaster_id: str, sender_id: str, message: str, client_id: str, oauth_token: str) -> None:
    url = 'https://api.twitch.tv/helix/chat/messages'
    headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Client-Id': client_id,
        'Content-Type': 'application/json'
    }
    payload = {
        'broadcaster_id': broadcaster_id,
        'sender_id': sender_id,
        'message': message
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.status_code} - {response.text}")

def get_user_id(username: str, client_id: str, oauth_token: str) -> str:
    url = 'https://api.twitch.tv/helix/users'
    headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Client-Id': client_id
    }
    params = {
        'login': username
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            return data['data'][0]['id']
        else:
            raise ValueError(f"User {username} not found")
    else:
        raise Exception(f"Failed to fetch user ID: {response.status_code} - {response.text}")

def main() -> None:
    client_id = os.getenv('TWITCH_CLIENT_ID')
    oauth_token = os.getenv('TWITCH_OAUTH_TOKEN')
    category_name = 'Artifact'
    
    #channels = get_live_channels(category_name, client_id, oauth_token)
    #print(channels)

    try:
        broadcaster_id = get_user_id('', client_id, oauth_token)
        sender_id = get_user_id('', client_id, oauth_token)
        print(broadcaster_id, sender_id)
    except Exception as e:
        print(f"Error: {e}")

    broadcaster_id = ''
    sender_id = ''
    message = ''
    send_chat_message(broadcaster_id, sender_id, message, client_id, oauth_token)

if __name__ == "__main__":
    main()

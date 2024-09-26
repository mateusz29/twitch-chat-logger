import json

import requests


def get_category_id(category_name: str, client_id: str, oauth_token: str) -> str:
    url = "https://api.twitch.tv/helix/games"
    headers = {"Client-ID": client_id, "Authorization": f"Bearer {oauth_token}"}
    params = {"name": category_name}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if not data["data"]:
        raise ValueError(f"No category found with name '{category_name}'")

    return data["data"][0]["id"]


def get_live_channels(category_id: str, client_id: str, oauth_token: str) -> list[str]:
    url = "https://api.twitch.tv/helix/streams"
    headers = {"Client-ID": client_id, "Authorization": f"Bearer {oauth_token}"}
    params = {
        "game_id": category_id,
        "first": 100,  # maximum number of results per request
    }

    response = requests.get(url, headers=headers, params=params)
    channels = response.json()["data"]

    return [channel["user_login"] for channel in channels]


def send_chat_message(
    broadcaster_id: str, sender_id: str, message: str, client_id: str, oauth_token: str
) -> None:
    url = "https://api.twitch.tv/helix/chat/messages"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }
    payload = {
        "broadcaster_id": broadcaster_id,
        "sender_id": sender_id,
        "message": message,
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        raise Exception(
            f"Failed to send message: {response.status_code} - {response.text}"
        )


def get_user_id(username: str, client_id: str, oauth_token: str) -> str:
    url = "https://api.twitch.tv/helix/users"
    headers = {"Authorization": f"Bearer {oauth_token}", "Client-Id": client_id}
    params = {"login": username}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]["id"]
        else:
            raise ValueError(f"User {username} not found")
    else:
        raise Exception(
            f"Failed to fetch user ID: {response.status_code} - {response.text}"
        )


def get_top_categories(client_id: str, oauth_token: str, after=None) -> str:
    url = "https://api.twitch.tv/helix/games/top"
    headers = {"Authorization": f"Bearer {oauth_token}", "Client-Id": client_id}
    params = {
        "first": 100,  # max number of items per page
    }
    if after:
        params["after"] = after

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

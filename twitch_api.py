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

def get_all_live_categories(client_id: str, oauth_token: str) -> set:
    cursor = ""
    all_categories = set()

    while True:
        categories_data = get_top_categories(client_id, oauth_token, cursor)

        for category in categories_data["data"]:
            category_name = category["name"]
            if category_name not in all_categories:
                all_categories.add(category_name)

        cursor = categories_data.get("pagination", {}).get("cursor")
        if not cursor:
            break
    
    return all_categories

def check_user_banned(usernames: list[str]) -> list[tuple[str, bool]]:
    url = "https://api.ivr.fi/v2/twitch/user"
    params = {"login": ",".join(usernames)}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        login_and_banned = []
        for channel in data:
            login = channel.get('login')
            banned = channel.get('banned')
            login_and_banned.append((login, banned))
        return login_and_banned
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")
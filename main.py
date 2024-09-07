import requests
import os
from dotenv import load_dotenv
import json
import twitchio
from twitchio.ext import commands
import asyncio

load_dotenv()


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


class Bot(commands.Bot):
    def __init__(self, client_id, oauth_token, category_name):
        self.client_id = client_id
        self.oauth_token = oauth_token
        self.category_id = get_category_id(category_name, client_id, oauth_token)
        self.channels = get_live_channels(self.category_id, client_id, oauth_token)
        super().__init__(
            token=oauth_token,
            client_id=client_id,
            prefix="!",
            initial_channels=self.channels,
        )
        self.loop.create_task(self.update_channels())

    async def event_ready(self) -> None:
        print("Successfully logged in!")
        print(f"Connected to channels: {', '.join(self.channels)}")

    async def event_message(self, message: twitchio.Message) -> None:
        print(f"[{message.channel.name}] {message.author.name}: {message.content}")

    async def update_channels(self) -> None:
        while True:
            new_channels = get_live_channels(
                self.category_id, self.client_id, self.oauth_token
            )
            channels_to_join = list(set(new_channels) - set(self.channels))

            print(f"Joining channels: {channels_to_join}")
            await self.join_channels(channels_to_join)

            self.channels = new_channels
            await asyncio.sleep(60)


async def main() -> None:
    client_id = os.getenv("TWITCH_CLIENT_ID")
    oauth_token = os.getenv("TWITCH_OAUTH_TOKEN")
    category_name = "Artifact"

    bot = Bot(client_id, oauth_token, category_name)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())

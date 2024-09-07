import asyncio

import twitchio
from twitchio.ext import commands

from twitch_api import get_category_id, get_live_channels


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

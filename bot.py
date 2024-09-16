import asyncio

import twitchio
from sqlalchemy.orm import sessionmaker
from twitchio.ext import commands

from db import Channel, Message, engine
from twitch_api import get_category_id, get_live_channels


class Bot(commands.Bot):
    def __init__(self, client_id, oauth_token, category_name):
        self.client_id = client_id
        self.oauth_token = oauth_token
        self.category_name = category_name
        self.category_id = None
        self.channels = []
        self.Session = sessionmaker(bind=engine)
        super().__init__(
            token=oauth_token,
            client_id=client_id,
            prefix="!",
            initial_channels=self.channels,
        )

    def get_channels_from_db(self) -> list[str]:
        # TODO: check if channel is band before joining
        with self.Session() as session:
            channels = session.query(Channel.name).all()
            return [channel[0] for channel in channels]

    async def event_ready(self) -> None:
        print("Successfully logged in!")
        self.category_id = get_category_id(self.category_name, self.client_id, self.oauth_token)

        self.channels = self.get_channels_from_db()

        if self.channels:
            print(f"Joining channels from db: {', '.join(self.channels)}")
            await self.join_channels(self.channels)

        await self.update_channels()
        self.loop.create_task(self.update_channels_loop())

    async def event_message(self, message: twitchio.Message) -> None:
        with self.Session() as session:
            channel = (
                session.query(Channel).filter_by(name=message.channel.name).first()
            )
            new_message = Message(
                channel_id=channel.id,
                user_name=message.author.name,
                content=message.content,
                timestamp=message.timestamp,
            )
            session.add(new_message)
            session.commit()

        print(
            f"[{message.channel.name}] [{message.timestamp}] {message.author.name}: {message.content}"
        )

    async def update_channels(self) -> None:
        new_channels = get_live_channels(
            self.category_id, self.client_id, self.oauth_token
        )
        channels_to_join = list(set(new_channels) - set(self.channels))

        if channels_to_join:
            print(f"Joining new live channels: {channels_to_join}")
            await self.join_channels(channels_to_join)

            with self.Session() as session:
                for channel_name in channels_to_join:
                    channel = session.query(Channel).filter_by(name=channel_name).first()
                    if not channel:
                        channel = Channel(name=channel_name)
                        session.add(channel)
                session.commit()

            self.channels.extend(channels_to_join)
        else:
            print("No new live channels to join.")
            
    async def update_channels_loop(self) -> None:
        while True:
            await asyncio.sleep(60)
            await self.update_channels()

import asyncio

import twitchio
from sqlalchemy.orm import sessionmaker
from twitchio.ext import commands

from db import Category, Channel, Message, engine
from twitch_api import check_user_banned, get_category_id, get_live_channels


class Bot(commands.Bot):
    def __init__(self, client_id: str, oauth_token: str, category_names: list[str]):
        self.client_id = client_id
        self.oauth_token = oauth_token
        self.category_names = category_names
        self.category_ids = []
        self.channels = []
        self.Session = sessionmaker(bind=engine)
        super().__init__(
            token=oauth_token,
            client_id=client_id,
            prefix="!",
            initial_channels=self.channels,
        )

    def get_categories_from_db(self) -> list[str]:
        with self.Session() as session:
            categories = session.query(Category.name).all()
            return [category[0] for category in categories]

    def get_channels_from_db(self) -> list[str]:
        with self.Session() as session:
            channels = session.query(Channel.name).all()
            return [channel[0] for channel in channels]

    def save_categories_to_db(self, category_names: list[str]) -> None:
        with self.Session() as session:
            for category_name in category_names:
                category = session.query(Category).filter_by(name=category_name).first()
                if not category:
                    category = Category(name=category_name)
                    session.add(category)
            session.commit()

    def save_channels_to_db(self, channel_names: list[str]) -> None:
        with self.Session() as session:
            for channel_name in channel_names:
                channel = session.query(Channel).filter_by(name=channel_name).first()
                if not channel:
                    channel = Channel(name=channel_name)
                    session.add(channel)
            session.commit()

    async def event_ready(self) -> None:
        print("Successfully logged in!")

        # Query existing categories from the db and add categories selected by user
        categories_from_db = self.get_categories_from_db()
        categories_to_join = list(set(self.category_names) - set(categories_from_db))
        self.category_names += categories_to_join
        
        self.save_categories_to_db(categories_to_join)

        for category in self.category_names:
            category_id = get_category_id(category, self.client_id, self.oauth_token)
            self.category_ids.append(category_id)

        self.channels = self.get_channels_from_db()

        # Exclude banned channels from the list of channels
        login_banned_list = check_user_banned(self.channels)
        self.channels = [login for login, banned in login_banned_list if not banned]

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
        new_channels = []
        for category_id in self.category_ids:
            new_channels.extend(
                get_live_channels(category_id, self.client_id, self.oauth_token)
            )

        channels_to_join = list(set(new_channels) - set(self.channels))

        if channels_to_join:
            print(f"Joining new live channels: {channels_to_join}")
            await self.join_channels(channels_to_join)

            self.save_channels_to_db(channels_to_join)

            self.channels.extend(channels_to_join)
        else:
            print("No new live channels to join.")

    async def update_channels_loop(self) -> None:
        while True:
            await asyncio.sleep(60)
            await self.update_channels()

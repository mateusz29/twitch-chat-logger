import asyncio
import os

from dotenv import load_dotenv

from bot import Bot

load_dotenv()


async def main() -> None:
    client_id = os.getenv("TWITCH_CLIENT_ID")
    oauth_token = os.getenv("TWITCH_OAUTH_TOKEN")
    category_names = ["Artifact", "Creature Resort", "a"]

    bot = Bot(client_id, oauth_token, category_names)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())

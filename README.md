# Twitch Chat Logger

## Project Overview

This project implements a Twitch bot that monitors live channels in specific categories and logs the messages from those channels to a PostgreSQL database. It utilizes the Twitch API to fetch live channels based on categories and uses SQLAlchemy for database management. 

## Features
- Automatically fetch live channels from specified Twitch categories.
- Join live Twitch channels and log chat messages to a PostgreSQL database.
- Persistently store chat messages with details such as the channel name, username, content, and timestamp.
- Automatically updates the list of joined channels when new channels in the specified categories go live.

## Technologies Used
- **Python**: The bot is written in Python using the `twitchio` library to interact with the Twitch API.
- **Twitch API**: Used to retrieve live channels by category.
- **SQLAlchemy**: For ORM-based interaction with the PostgreSQL database.
- **PostgreSQL**: The database used to store channel and message data.
- **Dotenv**: For securely managing sensitive environment variables like API keys and database URLs.
- **Asyncio**: Manages asynchronous operations to ensure smooth bot functionality.

## How it Works

1. **Fetching Categories & Channels**: The bot logs in and fetches the live channels for the specified categories using the Twitch API.
2. **Monitoring Channels**: It joins the channels and listens to chat messages.
3. **Storing Messages**: When a new message is detected, it is saved to the PostgreSQL database, with the channel, username, message content, and timestamp.
4. **Updating Channels**: Every 60 seconds, the bot checks for new live channels in the specified categories and joins any new channels that have gone live.


## TODO

- [x] Check if channel is band before joining
- [ ] Change connection to the db
- [x] Add a possibilty to add categories manually
- [ ] Add a possibility to add channels manually
- [ ] Make tests
- [ ] Host the code 


import os
import ssl
import subprocess
import re

import discord
import aiohttp
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USERNAME')
DB_PW = os.getenv('DB_PASSWORD')
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
sslcontext = ssl.create_default_context()
sslcontext.check_hostname = False
sslcontext.verify_mode = ssl.CERT_NONE
connector = aiohttp.TCPConnector(ssl=sslcontext)
client = discord.Client(connector=connector, intents=intents)


@client.event
async def on_ready():
    # CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
    guild_count = 0

    # LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
    for guild in client.guilds:
        # PRINT THE SERVER'S ID AND NAME.
        print(f"- {guild.id} (name: {guild.name})")

        # INCREMENTS THE GUILD COUNTER.
        guild_count = guild_count + 1

    # PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN.
    print("SampleDiscordBot is in " + str(guild_count) + " guilds.")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send("Hello")
    elif message.content.startswith('!HAI'):
        await message.channel.send(f'hai, {message.author.mention}')
    elif message.content.startswith('hai, ra!'):
        await message.channel.send('hai, ali')
    elif message.content.startswith('!show_databases'):
        cmd = f"mysql -h {DB_HOST} -u {DB_USER} -e 'show databases;'"
        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            if result.returncode == 0:
                output = result.stdout
            else:
                output = f"Error: {result.stderr}"
        except Exception as e:
            output = f"An error occurred: {e}"

        await message.channel.send(output)
    elif message.content.startswith('!backup'):
        database_name = message.content.split(" ")[1]
        path_file = f"/Users/rafiizzatulrizqufaris/Documents/python_upi/{database_name}.sql"
        cmd = f"mysqldump -h {DB_HOST} -u {DB_USER} {database_name} > {path_file}"
    try:
        # Run the backup command
        result = subprocess.run(
            cmd, shell=True, text=True, check=True)

        # Send a success message
        await message.channel.send("Database backup completed successfully.")

        # Send the backup file to the same channel
        backup_file = discord.File(f"{path_file}")
        await message.channel.send(file=backup_file)
        os.remove(path_file)

    except subprocess.CalledProcessError as e:
        # If the command returns a non-zero exit code, there was an error
        await message.channel.send(f"Error during database backup:\n```{e.stderr}```")


@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    try:
        # Process commands if applicable
        await bot.process_commands(message)
    except Exception as e:
        # Handle exceptions gracefully
        print(f"An error occurred while processing a command: {e}")

    # Check if the author is valid before accessing attributes
    if message.author is not None:
        # Now you can safely access attributes of message.author
        author_id = message.author.id
        author_name = message.author.name
        print(
            f"Message received from user {author_name} (ID: {author_id}): {message.content}")
    else:
        print("Received a message with no valid author.")

    await bot.process_commands(message)


client.run(TOKEN)

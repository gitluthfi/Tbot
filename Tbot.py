# fix uploader id error
# watch this bro, this unreal

import os
import ssl
import subprocess
import re
import youtube_dl
import asyncio
import pandas as pd
import io
import discord
import aiohttp
from dotenv import load_dotenv
from discord.ext import commands
from urllib.request import build_opener

import certifi
import urllib3
import urllib

# Set the SSL certificate path
urllib3.util.ssl_.DEFAULT_CERTS_FILE = certifi.where()

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
ssl._create_default_https_context = ssl._create_unverified_context
ssl_context = ssl._create_unverified_context()
opener = build_opener(urllib.request.HTTPSHandler(context=ssl_context))
youtube_dl.utils.urlopen = opener.open
connector = aiohttp.TCPConnector(ssl=sslcontext)
client = discord.Client(connector=connector, intents=intents)


urllib3.util.ssl_.DEFAULT_CERTS_FILE = certifi.where()

# Disable SSL certificate verification
sslcontext = ssl.create_default_context()
sslcontext.check_hostname = False
sslcontext.verify_mode = ssl.CERT_NONE


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
        # Check if there is a channel named "general" in the guild
        general_channel = discord.utils.get(
            guild.text_channels, name="general")

        if general_channel:
            # Send a message in the "general" channel
            if general_channel.permissions_for(guild.me).send_messages:
                await general_channel.send("@everyone ILY ready to serve!")

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='play_song', help='To play song')
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(
                executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@client.event
async def on_message(message):
    global voice_clients
    perintah = '!ILY'
    if message.author == client.user:
        return

    if message.content.startswith(f"{perintah} hello"):
        await message.channel.send("Hello")
    elif message.content.startswith(f"{perintah} berikan aku ruang"):
        # Mengambil server (guild) tempat pesan tersebut diposting
        guild = message.guild
        parts = message.content.split(" ")
        if len(parts) >= 5:
            namespace = " ".join(parts[4:])

    # Membuat saluran teks baru dengan nama "ruang-<nama_pengguna>"
        channel_name = f"ruang-{namespace}"
        new_channel = await guild.create_text_channel(channel_name)

    # Mengirim pesan konfirmasi ke saluran teks yang asal
        await new_channel.send(f"Ruang teks baru '{channel_name}' telah dibuat untuk {message.author.mention}")
    #                               #
    #INI MASIH DALAM TAHAP UJI COBA #
    #                               #
    elif message.content.startswith(f"{perintah} aku mau ngomong sesuatu ra"):
        guild = message.guild

    # Membuat kategori (category) untuk thread baru
        category = await guild.create_category(f"Ruang-{message.author.name}")

    # Membuat thread baru dalam kategori tersebut
        thread = await category.create_text_channel(name="ruang-teks", reason="Membuat thread baru")

    # Mengirim pesan ke dalam thread yang baru saja dibuat
        await thread.send(f'kemari ali! {message.author.mention}')
    # batas uji coba
    elif message.content.startswith('!HAI'):
        await message.channel.send(f'hai, {message.author.mention}')
    elif message.content.startswith('hai, ra!'):
        await message.channel.send('hai, ali')

    elif message.content.startswith(f"{perintah} play"):
        # Mendapatkan URL lagu dari pesan pengguna
        url = message.content[len(f"{perintah} play"):].strip()

        if message.author.voice is None:
            await message.channel.send("Anda harus bergabung dengan channel suara terlebih dahulu.")
            return

        voice_channel = message.author.voice.channel
        voice_client = await voice_channel.connect()

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
                'preferredquality': '256',
            }],
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            # bind to ipv4 since ipv6 addresses cause issues sometimes
            'source_address': '0.0.0.0',
        }

        ffmpeg_options = {
            'options': '-vn -b:a 256k -af loudnorm',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                voice_client.play(discord.FFmpegPCMAudio(url2))
                await message.channel.send('Lagu anda diputar, ENJOY!!!')
                print("Playing music...")  # Add this line for debugging

                while voice_client.is_playing():
                    await asyncio.sleep(1)

                print("Finished playing.")  # Add this line for debugging
                await voice_client.disconnect()
            except Exception as e:
                print(f"An error occurred during music playback: {e}")
    elif message.content.startswith(f"{perintah} show_databases"):
        cmd = f"mysql -h {DB_HOST} -u {DB_USER} -e 'select DB_ILY.m_staging.database_name, DB_ILY.m_staging.project_name from DB_ILY.m_staging;'"
        # parts = message.content.split(" ")
        # if len(parts) >= 1:
        #     link = " ".join(parts[1:])
        #     cmd = f"mysql -h {DB_HOST} -u {DB_USER} -e 'select DB_ILY.m_staging.database_name, DB_ILY.m_staging.project_name from DB_ILY.m_staging;"

        if message.content.startswith(f"{perintah} show_databases"):
            parts = message.content.split(" ")
            if len(parts) >= 2:
                link = " ".join(parts[2:])
                cmd = f"mysql -h {DB_HOST} -u {DB_USER} -e 'select DB_ILY.m_staging.database_name, DB_ILY.m_staging.project_name from DB_ILY.m_staging where project_name like \"%{link}%\";'"
                # print(cmd)
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
    elif message.content.startswith(f"{perintah}backup"):
        database_name = message.content.split(" ")[2]
        path_file = f"/Users/rafiizzatulrizqufaris/Documents/python_upi/{database_name}.sql"
        cmd = f"mysqldump -h {DB_HOST} -u {DB_USER} {database_name} > {path_file}"
        try:
            # Run the backup command
            result = subprocess.run(
                cmd, shell=True, text=True, check=True)

        # Send a success message
            await message.channel.send(f"Sir {message.author.mention} \n Database backup completed successfully.")

        # Send the backup file to the same channel
            backup_file = discord.File(f"{path_file}")
            await message.channel.send(file=backup_file)
            os.remove(path_file)

        except subprocess.CalledProcessError as e:
            # If the command returns a non-zero exit code, there was an error
            await message.channel.send(f"Error during database backup:\n```{e.stderr}```")
    elif message.content.startswith(f"{perintah}run"):
        # Split the message content into parts
        parts = message.content.split(" ")

    # Check if there are at least 3 parts (command, database name, and user query)
        if len(parts) >= 4:
            # Extract the database name and user query
            database_name = parts[2]
        # Join the remaining parts to form the user query
            user_query = " ".join(parts[3:])

        # Construct the MySQL command with proper quoting
            cmd = f"mysql -h {DB_HOST} -u {DB_USER} -e \"{user_query}\" {database_name}"

        try:
            # Run the query command
            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:
                # Send the query result as a message
                await message.channel.send(f"Query result for database '{database_name}':\n```{result.stdout}```")
            else:
                # If there's an error, send an error message
                await message.channel.send(f"Error executing the query:\n```{cmd}```")

        except Exception as e:
            # Handle other exceptions gracefully
            await message.channel.send(f"An error occurred: {e}")

        # Print the executed command for debugging purposes
        # print(cmd)
    elif message.content.startswith(f"{perintah}proto"):
        # Split the message content into parts
        parts = message.content.split(" ")

    # Check if there are at least 3 parts (command, database name, and user query)
        if len(parts) >= 4:
            # Extract the database name and user query
            database_name = parts[2]
        # Join the remaining parts to form the user query
            user_query = " ".join(parts[3:])

        # Construct the MySQL command with proper quoting
        cmd = f"mysql -h {DB_HOST} -u {DB_USER} -e \"{user_query}\" {database_name}"

        try:
            # Run the query command
            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:
                # Assuming the query result is in a tabular format, you can use pandas to read it
                query_result = pd.read_csv(
                    io.StringIO(result.stdout), delimiter="\t")

                # Save the query result to a CSV file
                csv_filename = f"{database_name}_query_result.csv"
                query_result.to_csv(csv_filename, index=False)

                # Send the CSV file
                with open(csv_filename, 'rb') as file:
                    await message.channel.send(f"Query result for database '{database_name}':", file=discord.File(file, csv_filename))

                # Delete the temporary CSV file
                os.remove(csv_filename)

            else:
                # If there's an error, send an error message
                await message.channel.send(f"Error executing the query:\n```{cmd}```")

        except Exception as e:
            # Handle other exceptions gracefully
            await message.channel.send(f"An error occurred: {e}")


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

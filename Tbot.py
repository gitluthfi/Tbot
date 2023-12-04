# fix uploader id error
# watch this bro, this unreal
# https://www.youtube.com/watch?v=Ghe058HpmMk&ab_channel=JaredThomas

import docker
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
import lyricsgenius
from dotenv import load_dotenv
from discord.ext import commands
from urllib.request import build_opener
from youtubesearchpython import VideosSearch
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from collections import deque



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
PATH_FILE= os.getenv('PATH_FILE')
ENV= os.getenv('BOT_ENV')
FOLDER_ID = os.getenv("FOLDER_DRIVE")
GENIUS_API = os.getenv('GENIUS_API_ID')
#docker_client = docker.from_env()
genius = lyricsgenius.Genius(GENIUS_API)
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

queue = deque()


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

@client.event
async def on_message(message):
    global voice_clients
    
    async def play_song(message, video_url):
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
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            }
        ffmpeg_options = {
            'options': '-vn -b:a 256k -af loudnorm',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try:
                    #extract video_url to youtube_dl so discord can play song
                    url1 = video_url['url']
                    info = ydl.extract_info(url1, download=False)
                    # got the real url from extracted url
                    url2 = info['formats'][0]['url']
                except Exception as e:
                    await message.reply(f"An error occurred while fetching song: {e}")
                # play the song
                voice_client.play(discord.FFmpegPCMAudio(url2))
                await message.reply(f"Lagu anda diputar, ENJOY!!! \n {url1}")
                print("Playing music...")  # Add this line for debugging


    async def search_lyric(message, title):
        try:
            song_title = title
            # Fetch lyrics for the song title
            song = genius.search_song(song_title)
            if song:
                lyrics = song.lyrics
                file_name = f"{song_title}_lyrics.txt"
                with open(file_name, "w", encoding="utf-8") as lyrics_file:
                    lyrics_file.write(lyrics)
                with open(file_name, "rb") as lyrics_file:
                    await message.channel.send(f"**Lyrics for {song_title}:**", file=discord.File(lyrics_file, file_name))
                os.remove(file_name)
            else:
                await message.channel.send("Lirik tidak ditemukan.")
        except Exception as e:
            await message.reply(f"An error occurred while fetching lyrics: {e}")
        

    async def parse_lagu(url):
        videosSearch = VideosSearch(url, limit=1)
    #Data hasil pencarian
        results = videosSearch.result()
        video_url = results['result'][0]['link']
        if not results:
            await message.reply("Lagu tidak ditemukan")
            return
        return video_url
    
    async def song_handler(message):
        voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
        try:
            message = await client.wait_for('message', timeout=1)
            if message.content.startswith(f"{perintah} pause"):
                if voice_client.is_playing():
                    voice_client.pause()
                    print('music paused')
                    await message.reply("Music paused.")
                else:
                    await message.reply("There is no music playing to pause.")
            
            elif message.content.startswith(f"{perintah} start"):
                if voice_client.is_paused():
                    voice_client.resume()
                    print('music resumed')
                    await message.reply("Music resumed.")
                else:
                    await message.reply("Music is not paused.")
                
            elif message.content.startswith(f"{perintah} stop"):
                if voice_client.is_playing():
                    voice_client.stop()
                    await message.reply("Music stopped.")
                else:
                    await message.reply("There is no music playing to stop.")
            
            elif message.content.startswith(f"{perintah} skip"):
                await skip_song(message)
            
            elif message.content.startswith(f"{perintah} add"):
                queue_url = message.content[len(f"{perintah} add"):].strip()
                queue_video_url = await parse_lagu(queue_url)
                new_song = {"title": queue_url, "url": queue_video_url}
                queue.append(new_song)
                #debugging
                # print(new_song)
                # print('batas')
                # print(queue)
                await message.reply(f"Musik masuk ke antrian {queue_video_url}")
        
        except asyncio.TimeoutError:
            pass
    
    async def play_next_song(message):
        voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
        while queue:
            song = queue.popleft()
            await search_lyric(message, song['title'])
            await play_song(message, song)

            # Wait for the current song to finish
            while voice_client.is_playing() or voice_client.is_paused():
                await asyncio.sleep(1)
                #song handler request
                await song_handler(message)

        await voice_client.disconnect()

    async def skip_song(message):
        voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
        
        if voice_client.is_playing():
            voice_client.stop()
            await message.reply("Song skipped.")
            await play_next_song(message)
        else:
            await message.reply("There is no song playing to skip.")
    if (ENV == "production"):
        perintah = '!ILY'
    elif (ENV == "develop"):
        perintah = '!ILO'
    if message.author == client.user:
        return

    if message.content.startswith(f"{perintah} hello"):
        await message.reply("Hello")
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
        await message.reply(f'hai, {message.author.mention}')
    elif message.content.startswith('hai, ra!'):
        await message.reply('hai, ali')

    elif message.content.startswith(f"{perintah} play"):
        #connect ke voice channel
        if message.author.voice is None:
            await message.reply("Anda harus bergabung dengan channel suara terlebih dahulu.")
            return

        voice_channel = message.author.voice.channel
        voice_client = await voice_channel.connect()

        # Parse search
        url = message.content[len(f"{perintah} play"):].strip()
        video_url = await parse_lagu(url)
        #Ambil link lagu dari data pencarian
        await message.reply('Tunggu sebentar pesanan anda sedang di proses')
        new_song = {"title": url, "url": video_url}
        queue.append(new_song)
        song = queue.popleft()
        await search_lyric(message, song['title'])
        await play_song(message, song)
        while voice_client.is_playing() or voice_client.is_paused():
            await asyncio.sleep(1)
            #song handler request
            await song_handler(message)
        if queue:
            #debugging
            #print("next song")
            await play_next_song(message)
        else:
            await voice_client.disconnect()
        
    elif message.content.startswith(f"{perintah} lirik"):
        title = message.content[len(f"{perintah} lirik"):].strip()
        await search_lyric(message, title)

    elif message.content.startswith(f"{perintah} show_databases"):
        cmd = f"mysql -h {DB_HOST} -u {DB_USER} -e 'select DB_ILY.m_staging.database_name, DB_ILY.m_staging.project_name from DB_ILY.m_staging;'"
        
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

        await message.reply(output)
    elif message.content.startswith(f"{perintah} backup"):
        database_name = message.content.split(" ")[2]
        cmd = f"mysqldump -h {DB_HOST} -u {DB_USER} -p{DB_PW} {database_name} > {PATH_FILE}/{database_name}.sql"
        await message.reply(f"Mohon tunggu sebentar pesanan mu sedang di proses {message.author.mention}")
        try:
            # Run the backup command
            result = subprocess.run(cmd, shell=True, text=True, check=True)

            # Authenticate with Google Drive using the service account key file
            gauth = GoogleAuth()
            gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                './ily-bot-405907-3118d738aca8.json', ['https://www.googleapis.com/auth/drive']
            )

            # Create a GoogleDrive client
            drive = GoogleDrive(gauth)
            print(f"Authenticated as: {gauth.credentials.service_account_email}")

            destination_folder_id = FOLDER_ID
            file = drive.CreateFile({'title': f'{database_name}.sql', 'parents': [{'id': destination_folder_id}]})
            path_backup = f"{PATH_FILE}/{database_name}.sql"
            file.SetContentFile(path_backup)
            file.Upload()
            file_link = file['alternateLink']

            # Send a success message
            await message.reply(f"Sir {message.author.mention} \n Database backup completed successfully. \n Here {file_link}")

            # Send the backup file to the same channel
            backup_file = discord.File(f"{PATH_FILE}/{database_name}.sql")
            # await message.reply(file=backup_file)
            os.remove(f"{PATH_FILE}/{database_name}.sql")

        except subprocess.CalledProcessError as e:
            # If the command returns a non-zero exit code, there was an error
            await message.reply(f"Error during database backup:\n```{e.stderr}```")

    elif message.content.startswith(f"{perintah} run"):
        # Split the message content into parts
        parts = message.content.split(" ")

    # Check if there are at least 3 parts (command, database name, and user query)
        if len(parts) >= 4:
            # Extract the database name and user query
            database_name = parts[2]
        # Join the remaining parts to form the user query
            user_query = " ".join(parts[3:])

        # Construct the MySQL command with proper quoting
            cmd = f"mysql -h {DB_HOST} -u {DB_USER} -p{DB_PW} -e \"{user_query}\" {database_name}"
        else:
            await message.reply(f"Sir {message.author.mention}, perintah tidak lengkap mohon lenkapi seperti ini \n `!ILY run database_name your_query`")

        try:
            # Run the query command
            result = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:
                # Send the query result as a message
                await message.reply(f"Query result for database '{database_name}':\n```{result.stdout}```")
            else:
                # If there's an error, send an error message
                await message.reply(f"Error executing the query:\n```{cmd}```")

        except Exception as e:
            # Handle other exceptions gracefully
            await message.reply(f"An error occurred: {e}")

        # Print the executed command for debugging purposes
        # print(cmd)
    elif message.content.startswith(f"{perintah} get"):
        # Split the message content into parts
        parts = message.content.split(" ")

    # Check if there are at least 3 parts (command, database name, and user query)
        if len(parts) >= 4:
            # Extract the database name and user query
            database_name = parts[2]
        # Join the remaining parts to form the user query
            user_query = " ".join(parts[3:])

        # Construct the MySQL command with proper quoting
        cmd = f"mysql -h {DB_HOST} -u {DB_USER} -p{DB_PW} -e \"{user_query}\" {database_name}"

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
                    await message.reply(f"Query result for database '{database_name}':", file=discord.File(file, csv_filename))

                # Delete the temporary CSV file
                os.remove(csv_filename)

            else:
                # If there's an error, send an error message
                await message.reply(f"Error executing the query:\n```{cmd}```")

        except Exception as e:
            # Handle other exceptions gracefully
            await message.reply(f"An error occurred: {e}")
    elif message.content.startswith(f"{perintah} deploy"):

        if len(message.content.split(" ")) == 4:

        # parse
            project_name = message.content.split(" ")[2]
            environment = message.content.split(" ")[3]        

            if (environment == "staging"):
                tag = "latest"

            print(f"Project Name: {project_name}")
            print(f"Tag: {tag}")
            print(f"Environment: {environment}")

            await message.reply(f"Mohon tunggu sir {message.author.mention}, pesanan anda sedang di proses")
        else:
            await message.reply(f"Sir {message.author.mention}, perintah tidak lengkap mohon lenkapi seperti ini \n `!ILY deploy project_name environment`")    
            return

        # Check if a container with the specified project name and tag exists
        container_name = f"{project_name}-{environment}"
        existing_container = None

        for container in docker_client.containers.list(all=True):
            if container.name == container_name:
                existing_container = container
                break

        # Stop and remove the existing container if it exists
        if existing_container:
            existing_container.stop()
            existing_container.remove()

        # Check and cleanup docker image    
        image_name = f"{project_name}:{tag}"
        existing_image = None
        print(image_name)

        for img in docker_client.images.list(name=project_name):
            existing_image = img
            break
        
        if existing_image:
            docker_client.images.remove(project_name)
        await message.reply(f"Sir {message.author.mention}, Pesananmu sedang dalam proses build, tunggu sebentar ya!! \n Sambil menunggu proses build, nikmati layanan musik saya, dapat diakses dengan command {perintah} play judul_lagu_anda")
        #build docker file
        if (project_name == ('sitrendy')):
            build_path = '/var/lib/jenkins/workspace/sitrendy'
            docker_client.images.build(
                path=build_path,
                tag=image_name,
                rm=True
            )
        else:
            await message.reply(f"Sir {message.author.mention} project tidak ditemukan, segera hubungi admin")
        # Run a new container with port mapping and volume attachment
        if (project_name == ('sitrendy')):
            container = docker_client.containers.run(
                image=image_name,
                detach=True,
                ports={'80/tcp': 1010},
                volumes={build_path: {'bind': '/var/www/html/app', 'mode': 'rw'},},
                name=container_name
            )
        else:
            await message.reply(f"Sir {message.author.mention} project tidak ditemukan, segera hubungi admin")
        await message.reply(f"{project_name} berhasil di deploy sir, {message.author.mention} \n Container ID: {container.id} \n Container Name: {container.name} \n Container Image: {container.image.tags[0]}")

    elif message.content.startswith(f"{perintah} exec"):
        # parse
        parts = message.content.split(" ")
        base_path = '/var/lib/jenkins/workspace/'

        # Check if there are at least 3 parts (command, database name, and user query)
        if len(parts) >= 5 and parts[3] == "--command=":
            # Extract the database name and user command
            project_name = parts[2]
            user_command = " ".join(parts[4:])

            # Map project names to directory names
            project_mapping = {
                "pusaka_bantuan": "pusaka_bantuan",
                "math_be": "math_be",
                "siaapp": "siaapp",
                "sitren": "sitren_new",
                "ijop_mdt": "ijop_mdt",
                "kemenag_lpdp": "kemenag_lpdp",
                "lpdp_ongoing": "lpdp_ongoing",
                "sitrendy": "sitrendy",
                "cbt_iw": "cbt_iw_2023",
                "simba": "pontren_bantuan"
            }

            # Check if the project_name is valid
            if project_name in project_mapping:
                dir_project = base_path + project_mapping[project_name]

                # Construct the command
                cmd = f"cd {dir_project} && {user_command}"
                try:
                    result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
                    chunks = [result.stdout[i:i + 2000] for i in range(0, len(result.stdout), 2000)]
                    for chunk in chunks:
                        await message.reply(f"Command executed successfully:\n```{chunk}```")
                except subprocess.CalledProcessError as e:
                    await message.reply(f"Command failed with error:\n```{e.stderr}```")
            else:
                await message.reply(f"Invalid project name: {project_name}")
        else:
            await message.reply("Invalid command format, `!ILO exec --command= your_command_here`")

        

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

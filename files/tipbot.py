import discord
from discord.ext import commands
import json
import os
import asyncio
from dotenv import load_dotenv
import yt_dlp
import logging
import sys
from datetime import datetime, time
import requests
import random

load_dotenv()

# Load configuration from config.json
with open('files/config.json', 'r') as f:
    config = json.load(f)

# Set up the bot with command prefix and intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent if needed
intents.guilds = True
intents.members = True  # Enable intents to use member data for commands

bot = commands.Bot(command_prefix="!", intents=intents)

SCORES_FILE = "files/scores.json"
FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}

song_queue = {}      # Dictionary to hold queues for each guild
current_song = {}    # Dictionary to hold the current song for each guild
user_scores = {}     # Dictionary to hold user scores
start_time = datetime.utcnow()  # Initialize start time

def ensure_opus():
    if not discord.opus.is_loaded():
        try:
            # Try different locations based on platform/environment
            discord.opus.load_opus("libopus.so.0")  # Linux
            logging.info("Opus library loaded successfully.")
        except OSError:
            try:
                discord.opus.load_opus("opus.dll")  # Windows
                logging.info("Opus library loaded successfully on Windows.")
            except Exception as e:
                logging.error(f"Failed to load Opus: {e}")
                print(f"Failed to load Opus: {e}")

# Load scores from a file
def load_scores():
    global user_scores
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r") as file:
                user_scores = {int(user_id): score for user_id, score in json.load(file).items()}
                print("Loaded scores:", user_scores)
        except json.JSONDecodeError:
            logging.error("Error: Invalid JSON format. Starting with an empty score.")
            print("Error: Invalid JSON format. Starting with an empty score.")
            user_scores = {}
        except Exception as error:
            logging.error(f"Error loading scores: {error}")
            print(f"Error loading scores: {error}")
            user_scores = {}
    else:
        print("Score file not found, starting with an empty score.")
        user_scores = {}

# Save scores to a file
def save_scores():
    with open(SCORES_FILE, "w") as file:
        json.dump(user_scores, file)
        print("Saved scores:", user_scores)

# TIP Command
@bot.slash_command(name="tip")
async def award(ctx: discord.ApplicationContext, member: discord.Member):
    user_id = member.id
    user_scores[user_id] = user_scores.get(user_id, 0) + 1
    save_scores()
    await ctx.respond(f"{member.mention} has received 1 point!", ephemeral=True)

# SCORECHECK Command
@bot.slash_command(name="score")
async def score(ctx: discord.ApplicationContext, member: discord.Member):
    user_id = member.id
    score = user_scores.get(user_id, 0)
    await ctx.respond(f"{member.mention} has {score} points.", ephemeral=True)

# LEADERBOARD Command
@bot.slash_command(name="leaderboard")
async def leaderboard(ctx: discord.ApplicationContext):
    sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    leaderboard_message = "Leaderboard:\n"
    for i, (user_id, score) in enumerate(sorted_scores):
        member = ctx.guild.get_member(user_id)
        leaderboard_message += f"{i + 1}. {member.mention if member else '[Unknown Member]'} - {score} points\n"
    await ctx.respond(leaderboard_message, ephemeral=True)

# KICK FROM VOICE CHANNEL
@bot.slash_command(name="sigma")
@commands.has_permissions(kick_members=True)
async def kick_voice(ctx: discord.ApplicationContext, member: discord.Member):
    if member.voice and member.voice.channel:
        await member.move_to(None)  # Kick the member from the voice channel
        await ctx.respond(f"{member.mention} has been removed from the voice channel.", ephemeral=True)
    else:
        await ctx.respond(f"{member.mention} is not in a voice channel.", ephemeral=True)

# Spam ping command (disabled to prevent abuse)
# @bot.slash_command(name="wolf")
# @commands.has_permissions(administrator=True)
# async def wolf(ctx: discord.ApplicationContext, member: discord.Member, times: int):
#     if times < 1 or times > 10:
#         await ctx.respond("Please enter a number between 1 and 10.", ephemeral=True)
#         return
#
#     await ctx.respond(f"Pinging {member.mention} {times} times.", ephemeral=True)
#     for i in range(times):
#         await ctx.send(f"{member.mention}")
#         await asyncio.sleep(0.5)

@bot.slash_command(name="gn")
async def gn(ctx: discord.ApplicationContext):
    await ctx.respond("https://tenor.com/view/goodnight-goodnight-cro-crow-team-crow-animal-gif-12348871433112850239")

@bot.slash_command(name="frog")
async def frog(ctx: discord.ApplicationContext):
    await ctx.respond("https://cdn.discordapp.com/attachments/1128773296150810674/1298684627870814258/togif.gif")

# Big Ben Bong Function
audio_file_gong = "../BONG.mp3"
audio_file_foreplay = "../bigben_foreplay.mp3"

async def bigben_bong(times):
    voice_channel_id = config['voice_channel_id']  # Replace with your voice channel ID from config
    channel = bot.get_channel(voice_channel_id)

    if channel is None:
        print("Voice channel not found.")
        return

    voice_client = None
    if bot.voice_clients:
        voice_client = bot.voice_clients[0]
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
    else:
        voice_client = await channel.connect()

    if voice_client.is_playing():
        voice_client.stop()

    # Begin the GONG
    if os.path.isfile(audio_file_foreplay):
        source = discord.FFmpegPCMAudio(audio_file_foreplay)
        voice_client.play(source)
        while voice_client.is_playing():
            await asyncio.sleep(1)

    for _ in range(times):
        if os.path.isfile(audio_file_gong):
            source = discord.FFmpegPCMAudio(audio_file_gong)
            voice_client.play(source)
            while voice_client.is_playing():
                await asyncio.sleep(1)

    await voice_client.disconnect()

async def bigben_time():
    while True:
        now = datetime.now()
        # Replace with your target times
        if now.hour == 12 and now.minute == 0:
            await bigben_bong(12)
        elif now.hour == 0 and now.minute == 0:
            await bigben_bong(12)
        else:
            await asyncio.sleep(60)

# Slovník
slovnik1path = "files/slovnik1.txt"
slovnik2path = "files/slovnik2.txt"

@bot.slash_command(name="slovnik")
async def slovnik(ctx):
    with open(slovnik1path, 'r', encoding='utf-8') as file:
        text1 = file.read()
        await ctx.respond(text1)
    with open(slovnik2path, 'r', encoding='utf-8') as file:
        text2 = file.read()
        await ctx.send(text2)
    # Removed the @everyone mention to prevent unwanted pings

@bot.slash_command(name="uptime")
async def uptime(ctx: discord.ApplicationContext):
    current_time = datetime.utcnow()  # Get the current time
    uptime_duration = current_time - start_time  # Calculate the difference
    hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.respond(f"Bot has been online for {hours} hours, {minutes} minutes, and {seconds} seconds.")

# MUSIC Commands
# JOIN Voice Channel Command
@bot.slash_command(name="join")
async def join(ctx: discord.ApplicationContext):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
        ensure_opus()
        await ctx.respond(f"Joined {channel}", ephemeral=True)
    else:
        await ctx.respond("You need to be in a voice channel to use this command.", ephemeral=True)

# LEAVE Voice Channel Command
@bot.slash_command(name="leave")
async def leave(ctx: discord.ApplicationContext):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.respond("Left the voice channel.", ephemeral=True)
    else:
        await ctx.respond("I'm not in a voice channel.", ephemeral=True)

# PLAY Command
@bot.slash_command(name="play")
async def play(ctx: discord.ApplicationContext, query: str):
    await ctx.defer()  # Defer response to prevent timeout

    guild_id = ctx.guild.id
    voice_client = ctx.guild.voice_client

    # Create a queue for the guild if it doesn't exist
    if guild_id not in song_queue:
        song_queue[guild_id] = []

    # If the bot is not connected to a voice channel, try to join the user's channel
    if not voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            voice_client = ctx.guild.voice_client  # Update the reference after connecting
        else:
            await ctx.respond("You need to be in a voice channel to use this command.", ephemeral=True)
            return

    ensure_opus()
    url, webpage_url, title = search_youtube(query)

    if not url:
        await ctx.respond(f"Could not find the song: {query}", ephemeral=True)
        return

    # Check if a song is currently playing
    if voice_client.is_playing() or voice_client.is_paused():
        # Add the song to the queue and notify the user
        song_queue[guild_id].append((url, title))
        await ctx.respond(f"Added to queue: {title}", ephemeral=True)
    else:
        # Play the song immediately if no other song is playing
        await start_playing(ctx, voice_client, url, title)

def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'auto',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                # It's a search result
                video = info['entries'][0]
            else:
                # It's a direct URL
                video = info
            return video['url'], video['webpage_url'], video['title']
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None, None, None

async def start_playing(ctx, voice_client, url, title):
    guild_id = voice_client.guild.id
    current_song[guild_id] = title  # Store the current song title
    try:
        source = discord.FFmpegPCMAudio(url)
        voice_client.play(source, after=lambda e: after_playing(e, guild_id, voice_client))
        if ctx:
            await ctx.followup.send(f"Now playing: {title}")
    except Exception as e:
        logging.error(f"Error playing the song: {e}")
        if ctx:
            await ctx.followup.send(f"Error playing the song: {e}")
        else:
            print(f"Error playing the song: {e}")

def after_playing(error, guild_id, voice_client):
    if error:
        print(f"Error: {error}")

    coro = play_next_song(guild_id, voice_client)
    fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    try:
        fut.result()
    except Exception as e:
        logging.error(f"Error in after_playing: {e}")

async def play_next_song(guild_id, voice_client):
    if song_queue[guild_id]:
        next_url, next_title = song_queue[guild_id].pop(0)
        current_song[guild_id] = next_title  # Update current song
        await start_playing(None, voice_client, next_url, next_title)
    else:
        current_song.pop(guild_id, None)  # Remove current song if no songs left
        await voice_client.disconnect()

# Skip Command
@bot.slash_command(name="skip")
async def skip(ctx: discord.ApplicationContext):
    voice_client = ctx.guild.voice_client
    guild_id = ctx.guild.id

    if not voice_client or not voice_client.is_playing():
        await ctx.respond("No song is currently playing to skip.", ephemeral=True)
        return

    # Stop the current song, triggering the next one to play
    voice_client.stop()
    await ctx.respond("Skipped the current song.", ephemeral=True)

# Show Queue Command
@bot.slash_command(name="queue")
async def show_queue(ctx: discord.ApplicationContext):
    guild_id = ctx.guild.id

    if guild_id not in song_queue or not song_queue[guild_id]:
        await ctx.respond("The queue is empty.", ephemeral=True)
        return

    queue_message = "Current Queue:\n"
    for i, (_, title) in enumerate(song_queue[guild_id]):
        queue_message += f"{i + 1}. {title}\n"

    await ctx.respond(queue_message, ephemeral=True)

# Now Playing Command
@bot.slash_command(name="np")
async def np(ctx: discord.ApplicationContext):
    guild_id = ctx.guild.id
    if guild_id in current_song and current_song[guild_id]:
        await ctx.respond(f"Now playing: {current_song[guild_id]}", ephemeral=True)
    else:
        await ctx.respond("Not playing anything.", ephemeral=True)

# Helper function to get a random GIF
async def get_gif(tag):
    url = "https://tenor.googleapis.com/v2/search"
    params = {
        "q": tag,
        "key": os.getenv('TENOR_API_KEY'),
        "limit": 20,
        "media_filter": "gif"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if not data.get('results'):
            return "No GIFs found for this tag."

        gif_url = random.choice(data['results'])['media_formats']['gif']['url']
        return gif_url

    except Exception as e:
        print(f"Error fetching GIF: {e}")
        return "Error fetching GIF."

@bot.slash_command(name="fooly_cooly")
async def fooly_cooly(ctx: discord.ApplicationContext):
    tag = "fooly cooly"
    gif_url = await get_gif(tag)
    await ctx.respond(gif_url)

@bot.slash_command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx: discord.ApplicationContext, amount: int):
    if amount < 1:
        await ctx.respond("Please specify a positive number of messages to delete.", ephemeral=True)
        return

    deleted = await ctx.channel.purge(limit=amount)
    await ctx.respond(f"Deleted {len(deleted)} messages.", ephemeral=True)

@bot.slash_command(name="is_this_real")
async def is_this_real(ctx: discord.ApplicationContext):
    chance = random.randint(1, 100)
    if chance <= 50:
        await ctx.respond("REAL")
        await ctx.send(":white_check_mark: :white_check_mark: :white_check_mark: :white_check_mark: :white_check_mark: :white_check_mark:")
    else:
        await ctx.respond("FAKE")
        await ctx.send(":x: :x: :x: :x: :x: :x: :x: :x: :x:")

# Event when the bot is ready
@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.playing, name="with honík")
    await bot.change_presence(activity=activity)
    load_scores()
    # Set up logging to a file
    logging.basicConfig(
        level=logging.DEBUG,  # Set the logging level (INFO, DEBUG, etc.)
        format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
        handlers=[
            logging.FileHandler('bot.log'),  # Log to the file
            logging.StreamHandler(sys.stdout)  # Log to the console
        ]
    )
    ensure_opus()
    global start_time
    start_time = datetime.utcnow()
    # Example log entry to test
    logging.info("Bot started")
    print(f"{bot.user} is online!")
    # Start the Big Ben task
    bot.loop.create_task(bigben_time())

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.respond("You don't have permission to use this command.", ephemeral=True)
    elif isinstance(error, commands.CommandNotFound):
        await ctx.respond("This command does not exist.", ephemeral=True)
    else:
        await ctx.respond("An error occurred while executing the command.", ephemeral=True)
        logging.error(f"An error occurred: {error}")

# Running the bot with your token
def runBot():
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))

print("Bot starting...")
runBot()

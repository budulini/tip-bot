import discord
from discord.ext import commands
import json
import os
import asyncio
from dotenv import load_dotenv
import yt_dlp
import logging
import sys

load_dotenv()

# Set up the bot with command prefix and intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent if needed
intents.guilds = True
intents.members = True  # Enable intents to use member data for commands

bot = commands.Bot(command_prefix="!", intents=intents)

SCORES_FILE = "files/scores.json"
FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}

def ensure_opus():
    if not discord.opus.is_loaded():
        try:
            discord.opus.load_opus()
            print("Opus library loaded successfully.")
        except Exception as e:
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
            print("Error: Invalid JSON format. Starting with an empty score.")
            user_scores = {}
        except Exception as error:
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
async def kick_voice(ctx: discord.ApplicationContext, member: discord.Member):
    allowed_user_id = 587316682364813323  # Replace with actual allowed user ID
    if ctx.user.id != allowed_user_id:
        await ctx.respond("You do not have permission to use this command.", ephemeral=True)
        return

    if member.voice and member.voice.channel:
        await member.move_to(None)  # Kick the member from the voice channel
        await ctx.respond(f"{member.mention} has been removed from the voice channel.", ephemeral=True)
    else:
        await ctx.respond(f"{member.mention} is not in a voice channel.", ephemeral=True)


# spam ping
@bot.slash_command(name="wolf")
async def wolf(ctx: discord.ApplicationContext, member: discord.Member, times: int):
    banned_user_id = 529381659208974346  # wolf
    if ctx.user.id == banned_user_id:
        await ctx.respond("You are not allowed to use this command.", ephemeral=True)
        return

    if times < 1 or times > 10:
        await ctx.respond("Please enter a number between 1 and 10.", ephemeral=True)
        return

    await ctx.respond(f"Pinging {member.mention} {times} times.", ephemeral=True)
    for i in range(times):
        await ctx.send(f"{member.mention}")
        await asyncio.sleep(0.5)


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
        

# JOIN Voice Channel Command
@bot.slash_command(name="join")
async def join(ctx: discord.ApplicationContext):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
        ensure_opus()
        await ctx.respond(f"Joined {channel}")
    else:
        await ctx.respond("You need to be in a voice channel to use this command.")


# LEAVE Voice Channel Command
@bot.slash_command(name="leave")
async def leave(ctx: discord.ApplicationContext):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.respond("Left the voice channel.")
    else:
        await ctx.respond("I'm not in a voice channel.")


# Play Music Command
@bot.slash_command(name="play")
async def play(ctx: discord.ApplicationContext, query: str):
    # Defer the interaction to give the bot time to process the request
    await ctx.defer()

    voice_client = ctx.guild.voice_client

    if not voice_client:
        await join(ctx)  # Automatically join the voice channel if not connected
        voice_client = ctx.guild.voice_client  # Update the voice_client variable

    ensure_opus()
    url = search_youtube(query)

    if not url:
        await ctx.followup.send(f"Could not find the song: {query}")
        return

    if voice_client.is_playing():
        voice_client.stop()

    try:
        voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: print(f"Error: {e}") if e else None)
        await ctx.followup.send(f"Now playing: {query}")
    except Exception as e:
        await ctx.followup.send(f"Error playing the song: {e}")


# Helper function to search YouTube using yt_dlp
def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                return info['entries'][0]['url']
            else:
                print(f"No results found for query: {query}")
                return None
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None


# Event when the bot is ready
@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.playing, name="with honík")
    await bot.change_presence(activity=activity)
    load_scores()
    # Set up logging to a file
    logging.basicConfig(
        level=logging.NOTSET,  # Set the logging level (INFO, DEBUG, etc.)
        format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
        handlers=[
            logging.FileHandler('bot.log'),  # Log to the file
            logging.StreamHandler(sys.stdout)  # Log to the console
        ]
    )
    ensure_opus()

    # Example log entry to test
    logging.info("Bot started")
    print(f"{bot.user} is online!")


# Running the bot with your token
def runBot():
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))


print("Bot starting...")
runBot()
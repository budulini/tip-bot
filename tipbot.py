from pydoc import describe
from time import sleep

import discord
from discord.ext import commands
import json
import os
import asyncio
from dotenv import load_dotenv
import yt_dlp
import logging
import sys
from datetime import datetime, timedelta, timezone, time
import requests
import random
import Steam_chart
import matplotlib.pyplot as plt
import csv

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

target_times = [time(23, 0), time(11, 00)]  # 12:00 AM and 12:00 PM

song_queue = {}  # Dictionary to hold queues for each guild
current_song = {}  # Dictionary to hold the current song for each guild

allowed_user_id = [587316682364813323, 457885645155729409]


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
async def kick_voice(ctx: discord.ApplicationContext, member: discord.Member):
    allowed_user_id = [587316682364813323, 457885645155729409]  # Repl]ace with actual allowed user ID
    if ctx.user.id not in allowed_user_id:
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


@bot.slash_command(name="gn")
async def gn(ctx: discord.ApplicationContext):
    await ctx.respond("https://tenor.com/view/goodnight-goodnight-cro-crow-team-crow-animal-gif-12348871433112850239")


@bot.slash_command(name="frog")
async def frog(ctx: discord.ApplicationContext):
    await ctx.respond("https://cdn.discordapp.com/attachments/1128773296150810674/1298684627870814258/togif.gif?ex=671a75cf&is=6719244f&hm=75e5de86dc5320c23c9e716e25c91af4aac3db9cd7ea0bc8540d441be4bcb1a8&")


"""
async def bigben():
    voice_channel_id = 1128735809776910349 # Replace with your voice channel ID
    channel = bot.get_channel(voice_channel_id)

    if channel is None:
        print("Voice channel not found.")
        return

    if bot.voice_clients:
        voice_client = bot.voice_clients[0]
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
    else:
        await channel.connect()

    voice_client = bot.voice_clients[0]

    url = "https://www.youtube.com/watch?v=E9wWBjnaEck"

    if voice_client.is_playing():
        voice_client.stop()

    try:
        voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: print(f"Error: {e}") if e else None)

        #time.sleep(10)
        await asyncio.sleep(180)
        voice_client.move_to(None)
    except Exception as e:
        logging.error(f"Error playing Big Ben sound: {e}")
        print(f"Error playing Big Ben sound: {e}")

"""
audio_file_gong = "BONG.mp3"
audio_file_foreplay = "bigben_foreplay.mp3"


async def bigben_bong(times):
    voice_channel_id = 1128735809776910349  # Replace with your voice channel ID
    channel = bot.get_channel(voice_channel_id)

    if channel is None:
        print("Voice channel not found.")
        return

    if bot.voice_clients:
        voice_client = bot.voice_clients[0]
        if voice_client.channel != channel:
            await voice_client.move_to(channel)
    else:
        await channel.connect()

    if voice_client.is_playing():
        voice_client.stop()

    # begin tha GONG
    if os.path.isfile(audio_file_foreplay):
        source = discord.FFmpegPCMAudio(audio_file_foreplay)
        voice_client.play(source, after=lambda e: print(f"Finished playing: {e}"))
        while voice_client.is_playing():
            await asyncio.sleep(1)

    for i in range(times):
        if os.path.isfile(audio_file_gong):
            source = discord.FFmpegPCMAudio(audio_file_gong)
            voice_client.play(source, after=lambda e: print(f"Finished playing: {e}"))
            while voice_client.is_playing():
                await asyncio.sleep(1)

    await asyncio.sleep(5)
    voice_client.move_to(None)

"""
async def bigben_time():
    while True:
        now = datetime.now()
        if now.hour == 11 and now.minute == 00:
            bigben_bong(12)
        elif now.hour == 23 and now.minute == 00:
            bigben_bong(12)
        elif now.hour == 0 and now.minute == 00:
            bigben_bong(13)
        elif now.hour == 1 and now.minute == 00:
            bigben_bong(14)
        elif now.hour == 2 and now.minute == 00:
            bigben_bong(15)
        elif now.hour == 3 and now.minute == 00:
            bigben_bong(16)
        elif now.hour == 4 and now.minute == 00:
            bigben_bong(17)
        elif now.hour == 17 and now.minute == 15:  # test time
            bigben_bong(4)
        else:
            sleep(60)



async def time_based_trigger():
    global target_times

    while True:
        now = datetime.now().time()
        current_minutes = now.hour * 60 + now.minute

        target_minutes = [
            target_time.hour * 60 + target_time.minute for target_time in target_times
        ]

        next_target = min(target_minutes, key=lambda t: (t - current_minutes) % (24 * 60))  # Find the next time event

        if next_target == current_minutes:
            print("Triggering Big Ben function")
            await bigben()

        sleep_for = (next_target - current_minutes) % (24 * 60)  # Handle time differences crossing midnight
        await asyncio.sleep(sleep_for * 60)  # Convert to seconds

"""
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
    await ctx.respond("<@everyone>")


@bot.slash_command(name="uptime")
async def uptime(ctx: discord.ApplicationContext):
    await ctx.defer()
    current_time = datetime.now().astimezone()  # Get the current time
    uptime_duration = current_time - start_time  # Calculate the difference
    hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.respond(f"Bot has been online for {hours} hours, {minutes} minutes, and {seconds} seconds.")
    await ctx.send(f"now is {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}")


# Function to add, remove, or show target times
@bot.slash_command(name="time_manager", description="Manage the target times for the bot")
async def time_manager(ctx: discord.ApplicationContext, action: str, hour: int = None, minute: int = None):
    """
    Manage target times: add, remove, or show.

    :param ctx: Discord command context.
    :param action: 'add', 'remove', or 'show'.
    :param hour: Optional, hour for the time (required for 'add' or 'remove').
    :param minute: Optional, minute for the time (required for 'add' or 'remove').
    """
    global target_times

    if action.lower() == 'show':
        # Show the current target times
        times_list = ', '.join([f"{t.hour:02d}:{t.minute:02d}" for t in target_times])
        if times_list:
            await ctx.respond(f"Current target times are: {times_list}")
        else:
            await ctx.respond("There are no target times set.")

    elif action.lower() == 'add':
        if hour is None or minute is None:
            await ctx.respond("Please provide both an hour and a minute to add a new time.", ephemeral=True)
            return

        new_time = time(hour, minute)
        if new_time in target_times:
            await ctx.respond(f"Time {new_time.strftime('%H:%M')} is already in the list.", ephemeral=True)
        else:
            target_times.append(new_time)
            target_times.sort()  # Keep the times sorted
            await ctx.respond(f"Added new time: {new_time.strftime('%H:%M')}")

    elif action.lower() == 'remove':
        if hour is None or minute is None:
            await ctx.respond("Please provide both an hour and a minute to remove a time.", ephemeral=True)
            return

        remove_time = time(hour, minute)
        if remove_time in target_times:
            target_times.remove(remove_time)
            await ctx.respond(f"Removed time: {remove_time.strftime('%H:%M')}")
        else:
            await ctx.respond(f"Time {remove_time.strftime('%H:%M')} not found in the list.", ephemeral=True)

    else:
        await ctx.respond("Invalid action. Please use 'add', 'remove', or 'show'.", ephemeral=True)


#   MUSIC
# ///////////////////////////////////////////////////////////////////
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
            await ctx.respond("You need to be in a voice channel to use this command.")
            return

    ensure_opus()
    url, webpage_url, title = await search_youtube(query)

    if not url:
        await ctx.respond(f"Could not find the song: {query}")
        return

    # Check if a song is currently playing
    if voice_client.is_playing() or voice_client.is_paused():
        # Add the song to the queue and notify the user
        song_queue[guild_id].append((url, title))
        await ctx.respond(f"Added to queue: {title}")
    else:
        # Play the song immediately if no other song is playing
        await start_playing(ctx, voice_client, url, title)


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


def after_playing(error, guild_id, voice_client):
    if error:
        print(f"Error: {error}")

    coro = play_next_song(guild_id, voice_client)
    fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    try:
        fut.result()
    except Exception as e:
        print(f"Error in after_playing: {e}")


async def play_next_song(guild_id, voice_client):
    if song_queue[guild_id]:
        next_url, next_title = song_queue[guild_id].pop(0)
        current_song[guild_id] = next_title  # Update current song
        await start_playing(None, voice_client, next_url, next_title)
    else:
        current_song.pop(guild_id, None)  # Remove current song if no songs left
        await voice_client.disconnect()


'''
def handle_after(ctx, error):
    guild_id = ctx.guild.id
    voice_client = ctx.guild.voice_client

    if error:
        print(f"Error: {error}")

    # Play the next song in the queue, if any
    if song_queue[guild_id]:
        next_url, next_query = song_queue[guild_id].pop(0)
        current_song[guild_id] = next_query  # Update current song
        ctx.bot.loop.create_task(start_playing(ctx, voice_client, next_url, next_query))
    else:
        current_song.pop(guild_id, None)  # Remove current song if no songs left
        ctx.bot.loop.create_task(voice_client.disconnect())
'''


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
    for i, (_, query) in enumerate(song_queue[guild_id]):
        queue_message += f"{i + 1}. {query}\n"

    await ctx.respond(queue_message, ephemeral=True)


# Now Playing Command
@bot.slash_command(name="np")
async def np(ctx: discord.ApplicationContext):
    guild_id = ctx.guild.id
    if guild_id in current_song and current_song[guild_id]:
        await ctx.respond(f"Now playing: {current_song[guild_id]}")
    else:
        await ctx.respond("Not playing anything.")


# Helper function to search YouTube using yt_dlp
async def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'auto',  # Automatically detect if input is URL or search term
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


# ///////////////////////////////////////////////////////////////////

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
async def clear(ctx: discord.ApplicationContext, amount: int):
    if ctx.user.id not in allowed_user_id:
        await ctx.respond("kys nigga.", ephemeral=True)
        return

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
        await ctx.send(":white_check_mark: :white_check_mark: :white_check_mark:")
    else:
        await ctx.respond("FAKE")
        await ctx.send(":x: :x: :x:")





@bot.slash_command(name="strip")
async def strip(ctx, user_id: int, target_guild_id: int):

    if ctx.user.id not in allowed_user_id:
        await ctx.respond("kys nigga.", ephemeral=True)
        return

    target_guild = bot.get_guild(target_guild_id)
    if not target_guild:
        await ctx.respond(f"Could not find the server with ID {target_guild_id}.", ephemeral=True)
        return

    # Ensure the bot has a role higher than the user's roles

    try:
        # Fetch the user in the target server
        member = await target_guild.fetch_member(user_id)
        if not member:
            await ctx.respond("User not found in the target server.", ephemeral=True)
            return

        if ctx.guild.me.top_role <= member.top_role:
            await ctx.respond("I cannot strip roles from this user due to role hierarchy.", ephemeral=True)
            return

        # Strip all roles
        roles_to_remove = [role for role in member.roles if role != target_guild.default_role]
        if not roles_to_remove:
            await ctx.respond(f"{member} has no roles to remove in {target_guild.name}.", ephemeral=True)
            return

        for role in roles_to_remove:
            await member.remove_roles(role, reason=f"Roles removed via remote command by {ctx.author}")

        await ctx.respond(f"All roles have been removed from {member} in {target_guild.name}.")

    except Exception as e:
        await ctx.respond(f"Failed to strip roles: {e}", ephemeral=True)


LOG_FILE = os.getenv("STEAM_LOG_FILE", "steam_activity.csv")
TARGET_GAME = os.getenv("TARGET_GAME", "Marvel Rivals")
STEAM_DAILY_TOTAL_LOG = os.getenv("STEAM_DAILY_LOG_FILE", "steam_daily_totals.csv")

@bot.slash_command(name="ticovi")
async def ticovi(
        ctx: discord.ApplicationContext,
        operation: discord.Option(
            str,
            "Choose what to display",
            choices=["session_graph", "daily_total_graph", "sessions_text", "daily_total_text"]
        )
):
    """Shows Marvel Rivals playtime statistics with different views"""
    await ctx.defer()
    current_date = datetime.now(timezone.utc).date()
    cutoff_date = current_date - timedelta(days=30)

    if operation == "session_graph":
        sessions = {}
        if not os.path.isfile(LOG_FILE):  # Uses module-level LOG_FILE from tipbot.py
            return await ctx.respond(
                f"No session data found for **{TARGET_GAME}**.")  # Uses module-level TARGET_GAME from tipbot.py

        with open(LOG_FILE, "r") as f:  # Uses module-level LOG_FILE from tipbot.py
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = datetime.fromisoformat(row["date"]).date()
                    dur = int(row["duration_seconds"])
                    if date not in sessions:
                        sessions[date] = 0
                    sessions[date] += dur
                except (ValueError, KeyError) as e:
                    print(f"Skipping malformed row in {LOG_FILE}: {row} - Error: {e}")
                    continue

        num_days = (current_date - cutoff_date).days + 1
        all_dates = [cutoff_date + timedelta(days=i) for i in range(num_days)]
        dates = []
        durations = []
        for date_iter in all_dates:  # Renamed 'date' to 'date_iter' to avoid conflict
            duration = sessions.get(date_iter, 0) / 3600
            dates.append(date_iter)
            durations.append(duration)

        if not any(d > 0 for d in durations):  # Check if any duration is actually greater than 0
            return await ctx.respond(
                f"No play records for **{TARGET_GAME}** in the last 30 days.")  # Uses module-level TARGET_GAME

        plt.figure(figsize=(15, 6))
        plt.bar(range(len(dates)), durations, align='center')
        plt.xlabel("Den")
        plt.ylabel("hodiny goonění")
        plt.title(f"Sessions - degenerace (posledních 30 days)")
        plt.xticks(ticks=range(len(dates)), labels=[d.strftime("%Y-%m-%d") for d in dates], rotation=45,
                   ha='right')
        plt.tight_layout()
        path = "marvel_graph.png"
        plt.savefig(path)
        plt.close()

        await ctx.respond(file=discord.File(path))

        total_duration_sum = sum(durations)
        active_days = sum(1 for d in durations if d > 0)
        avg_duration = total_duration_sum / active_days if active_days > 0 else 0
        await ctx.send(f"Average goon time (sessions): {avg_duration:.2f} hours per day over the last 30 days.")

    elif operation == "daily_total_graph":
        daily_totals = {}
        if not os.path.isfile(STEAM_DAILY_TOTAL_LOG):  # Uses module-level STEAM_DAILY_TOTAL_LOG from tipbot.py
            return await ctx.respond(
                f"No daily total data found for **{TARGET_GAME}**.")  # Uses module-level TARGET_GAME

        with open(STEAM_DAILY_TOTAL_LOG, "r") as f:  # Uses module-level STEAM_DAILY_TOTAL_LOG
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = datetime.fromisoformat(row["date"]).date()
                    minutes = float(row["minutes_played"])
                    daily_totals[date] = minutes / 60
                except (ValueError, KeyError) as e:
                    print(f"Skipping malformed row in {STEAM_DAILY_TOTAL_LOG}: {row} - Error: {e}")
                    continue

        dates_filtered = []  # Renamed to avoid conflict
        daily_hours = []
        # Iterate through all dates in the last 30 days to ensure consistent plotting
        num_days = (current_date - cutoff_date).days + 1
        all_plot_dates = [cutoff_date + timedelta(days=i) for i in range(num_days)]

        for plot_date in all_plot_dates:
            dates_filtered.append(plot_date)
            daily_hours.append(daily_totals.get(plot_date, 0))

        if not any(h > 0 for h in daily_hours):  # Check if any hours are actually greater than 0
            return await ctx.respond(
                f"No daily total records for **{TARGET_GAME}** in the last 30 days.")  # Uses module-level TARGET_GAME

        plt.figure(figsize=(15, 6))
        plt.bar(range(len(dates_filtered)), daily_hours, align='center', color='orange')
        plt.xlabel("Den")
        plt.ylabel("hodiny goonění")
        plt.title(f"Daily Totals - degenerace (last 30 days)")
        plt.xticks(ticks=range(len(dates_filtered)), labels=[d.strftime("%Y-%m-%d") for d in dates_filtered],
                   rotation=45,
                   ha='right')
        plt.tight_layout()
        path = "daily_totals_graph.png"
        plt.savefig(path)
        plt.close()

        await ctx.respond(file=discord.File(path))

        if daily_hours:  # This will always be true if the above check passed
            avg_daily = sum(h for h in daily_hours if h > 0) / sum(1 for h in daily_hours if h > 0) if sum(
                1 for h in daily_hours if h > 0) > 0 else 0
            await ctx.send(
                f"Average goon time (daily totals for active days): {avg_daily:.2f} hours per day over the last 30 days.")

    elif operation == "sessions_text":
        sessions = {}
        if not os.path.isfile(LOG_FILE):  # Uses module-level LOG_FILE
            return await ctx.respond(f"No session data found for **{TARGET_GAME}**.")  # Uses module-level TARGET_GAME

        with open(LOG_FILE, "r") as f:  # Uses module-level LOG_FILE
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = datetime.fromisoformat(row["date"]).date()
                    dur = int(row["duration_seconds"])
                    if date not in sessions:
                        sessions[date] = 0
                    sessions[date] += dur
                except (ValueError, KeyError) as e:
                    print(f"Skipping malformed row in {LOG_FILE}: {row} - Error: {e}")
                    continue

        if not sessions:  # Should be caught by isfile, but good practice
            return await ctx.respond(f"No session data found for **{TARGET_GAME}**.")  # Uses module-level TARGET_GAME

        message = f"**{TARGET_GAME} Session Data (Hours) - Last 30 Days**\n```\nDate       | Hours\n-----------+-------\n"  # Uses module-level TARGET_GAME

        # Filter for the last 30 days and sort
        recent_sessions_data = []
        for date_entry, total_seconds in sorted(sessions.items(), reverse=True):
            if date_entry >= cutoff_date:
                hours = total_seconds / 3600
                recent_sessions_data.append((date_entry, hours))

        if not recent_sessions_data:
            message += "No session data in the last 30 days.\n"
        else:
            for date_entry, hours in recent_sessions_data:
                message += f"{date_entry.strftime('%Y-%m-%d')} | {hours:.2f}\n"

        message += "```"
        await ctx.respond(message)

        if recent_sessions_data:
            total_hours_sum = sum(h for _, h in recent_sessions_data)
            active_days_count = len(recent_sessions_data)
            avg_hours_calc = total_hours_sum / active_days_count if active_days_count > 0 else 0
            await ctx.send(
                f"Total: {total_hours_sum:.2f} hours over {active_days_count} active days (avg: {avg_hours_calc:.2f} h/day) in the last 30 days.")
        elif not sessions:  # If no sessions at all
            await ctx.send("No session data available to calculate statistics.")


    elif operation == "daily_total_text":
        daily_totals = {}
        if not os.path.isfile(STEAM_DAILY_TOTAL_LOG):  # Uses module-level STEAM_DAILY_TOTAL_LOG
            return await ctx.respond(
                f"No daily total data found for **{TARGET_GAME}**.")  # Uses module-level TARGET_GAME

        with open(STEAM_DAILY_TOTAL_LOG, "r") as f:  # Uses module-level STEAM_DAILY_TOTAL_LOG
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = datetime.fromisoformat(row["date"]).date()
                    minutes = float(row["minutes_played"])
                    daily_totals[date] = minutes / 60
                except (ValueError, KeyError) as e:
                    print(f"Skipping malformed row in {STEAM_DAILY_TOTAL_LOG}: {row} - Error: {e}")
                    continue

        if not daily_totals:  # Should be caught by isfile
            return await ctx.respond(
                f"No daily total data found for **{TARGET_GAME}**.")  # Uses module-level TARGET_GAME

        message = f"**{TARGET_GAME} Daily Total Data (Hours) - Last 30 Days**\n```\nDate       | Hours\n-----------+-------\n"  # Uses module-level TARGET_GAME

        recent_totals_data = []
        for date_entry, hours_val in sorted(daily_totals.items(), reverse=True):
            if date_entry >= cutoff_date:
                recent_totals_data.append((date_entry, hours_val))

        if not recent_totals_data:
            message += "No daily total data in the last 30 days.\n"
        else:
            for date_entry, hours_val in recent_totals_data:
                message += f"{date_entry.strftime('%Y-%m-%d')} | {hours_val:.2f}\n"

        message += "```"
        await ctx.respond(message)

        if recent_totals_data:
            total_hours_sum = sum(h for _, h in recent_totals_data)
            days_count = len(recent_totals_data)
            avg_hours_calc = total_hours_sum / days_count if days_count > 0 else 0
            await ctx.send(
                f"Total: {total_hours_sum:.2f} hours over {days_count} recorded days (avg: {avg_hours_calc:.2f} h/day) in the last 30 days.")
        elif not daily_totals:
            await ctx.send("No daily total data available to calculate statistics.")

@bot.slash_command(name="add_goon")
async def add_entry(ctx: discord.ApplicationContext, date: str, duration: int):
    """
    Adds an entry to the CSV file with a date and duration in seconds.
    """
    if ctx.user.id not in allowed_user_id:
        await ctx.respond("kys nigga.", ephemeral=True)
        return

    # Validate the date input (should be in YYYY-MM-DD format)
    try:
        entry_date = datetime.fromisoformat(date).date()
    except Exception as e:
        return await ctx.respond("Invalid date format. Please use ISO format (YYYY-MM-DD).", ephemeral=True)

    file_exists = os.path.isfile(LOG_FILE)
    # Append the new entry into the CSV file
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "duration_seconds"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({"date": entry_date.isoformat(), "duration_seconds": duration})

    await ctx.respond("Entry added to CSV file.", ephemeral=True)



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
            logging.FileHandler('files/bot.log'),  # Log to the file
            logging.StreamHandler(sys.stdout)  # Log to the console
        ]
    )
    ensure_opus()
    global start_time
    start_time = datetime.now().astimezone()
    # Example log entry to test
    logging.info("Bot started")
    print(f"{bot.user} is online!")
    # await bigben_time()
    Steam_chart.setup(bot)



# Running the bot with your token
def runBot():
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))


print("Bot starting...")
runBot()
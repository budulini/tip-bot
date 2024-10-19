import discord
from discord.ext import commands
import json
import os
import asyncio  # For asynchronous sleep
from dotenv import load_dotenv
import yt_dlp

load_dotenv()
bot = discord.Bot()
SCORES_FILE = "stats/scores.json"
slovnikfile = "slovnik.json"
FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}


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


# KICK FROM VOICE CHANNEL Command
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
    banned_user_id = 529381659208974346  # Replace with actual banned user ID
    if ctx.user.id == banned_user_id:
        await ctx.respond("You are not allowed to use this command.", ephemeral=True)
        return

    if times < 1 or times > 10:
        await ctx.respond("Please enter a number between 1 and 10.", ephemeral=True)
        return

    await ctx.respond(f"Pinging {member.mention} {times} times.", ephemeral=True)
    for i in range(times):
        await ctx.send(f"{member.mention}")
        await asyncio.sleep(0.5)  # Non-blocking sleep to avoid spam detection


# Slovník
@bot.slash_command(name="slovnik")
async def slovnik(ctx):
    await ctx.respond("The Classics: Skibidi, Grimace Shake, Fanum Tax, Doomscrolling, Chat, Kai Cenat, Edging, Rizzing, Gooning, Rizz, Rizzing, Sigma, Only in Ohio, 19 Dollar Fortnite card, Double Pump, Hitting the Griddy, Ice Spice, Level 100 Gyatt, Gooning cave, Discord Kitten, You make my heart burn\n \n Adjectives: Sus, Sussy, Sussy baka, Rizzler, Alpha, Beta, Sigma, Based, Chuds, Thot, Skibidi Sigma, Simp, Soyboy, Chads, Sturdy, Gamer, Incel, Cringe/Cringey, Furry, Discord Kitten, Streamer, Zesty, Boomer, Doomer, Coomer, Zoomer, Gooner, Goofy, Silly, Cracked at fortnite\n \n Brands/Franchises: Fortnite, Reddit, Youtube Shorts, TikTok, Mc Donalds, Gucci, Supreme, Discord, Roblox, Subway Surfers shorts, Family guy shorts, Tinder, Uber Eats,\n \n Streamers/People: Mr beast, Ice Spice, Kai cenat, Fanum, Caseoh, DaFuqBoom, Baby gronk, Master Oogway, Peter Griffin, Raven Team leader, Andrew tate, Ben Shapiro, Jordan Peterson, Elon Musk, Dababy, Lebron James, Kanye West.\n \n Sounds: Yeet, Oof, Leroy Jenkins, gyatt, Happy Happy Happy, Oh no!!\n \n Catchphrases: Leroy Jenkins, Hell naw, What the dog doin?, imma head out, Upgrades, people, more upgrades, Zoo wee mama, Deez Nuts, Shikanoko nokonoko Koshitantan, Only a spoonful, POV:, IS THAT A JOJO REFERENCE???, How bad can i be?, Why do i hear boss music, Aw shit here we go again, No, you are not a gamer\n \n Still water + adrenaline + noradrenaline + hawk tuah + anger issues + balkan parents + english or Spanish + german stare + Balkan rage + jonkler laugh +phonk + those who know=")


def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': 'True'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None
    return info['url']


@bot.slash_command(name="join")
async def join(ctx: discord.ApplicationContext):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
        await ctx.respond(f"Joined {channel}")
    else:
        await ctx.respond("You need to be in a voice channel to use this command.")


@bot.slash_command(name="leave")
async def leave(ctx: discord.ApplicationContext):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.respond("Left the voice channel.")
    else:
        await ctx.respond("I'm not in a voice channel.")


@bot.slash_command(name="play")
async def play(ctx: discord.ApplicationContext, query: str):
    voice_client = ctx.guild.voice_client

    if not voice_client:
        await ctx.respond("I'm not connected to a voice channel.")
        return

    url = search_youtube(query)

    if not url:
        await ctx.respond("Could not find the song.")
        return

    if voice_client.is_playing():
        voice_client.stop()

    try:
        voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: print(f"Error: {e}") if e else None)
        await ctx.respond(f"Now playing: {query}")
    except Exception as e:
        await ctx.respond(f"Error playing the song: {e}")


@bot.slash_command(name="pause")
async def pause(ctx: discord.ApplicationContext):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.respond("Paused the song.")
    else:
        await ctx.respond("No song is currently playing.")


@bot.slash_command(name="resume")
async def resume(ctx: discord.ApplicationContext):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.respond("Resumed the song.")
    else:
        await ctx.respond("No song is currently paused.")


@bot.slash_command(name="stop")
async def stop(ctx: discord.ApplicationContext):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.respond("Stopped the song.")
    else:
        await ctx.respond("No song is currently playing.")


# cross server kicking
@bot.slash_command(name="super_sigma", guild=discord.Object(id=876802324192952320))
async def super_sigma(ctx: discord.ApplicationContext, target_guild_id: str, user_id: str):
    allowed_user_id = 587316682364813323  # Replace with actual allowed user ID
    if ctx.user.id != allowed_user_id:
        await ctx.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    target_guild = bot.get_guild(int(target_guild_id))
    if target_guild is None:
        await ctx.respond("Bot is not in the target server or cannot find the server.", ephemeral=True)
        return

    member = target_guild.get_member(int(user_id))
    if member is None:
        await ctx.respond("Target user is not in the target server or cannot be found.", ephemeral=True)
        return

    if member.voice and member.voice.channel:
        try:
            await member.move_to(None)  # Kick from voice channel
            await ctx.respond(f"{member.name} has been removed from voice channel in {target_guild.name}.",
                              ephemeral=True)
        except discord.Forbidden:
            await ctx.respond("I do not have permission to move this user.", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"An error occurred: {e}", ephemeral=True)
    else:
        await ctx.respond(f"{member.name} is not in a voice channel on {target_guild.name}.", ephemeral=True)


# Event when bot is ready
@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.playing, name="with honík")
    await bot.change_presence(activity=activity)
    load_scores()
    await bot.sync_commands()
    print(f"{bot.user} is online!")


def runBot():
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))


print("Bot starting...")
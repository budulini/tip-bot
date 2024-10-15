import discord
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()
bot = discord.Bot()
SCORES_FILE = "scores.json"


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


# WOLF Command for pinging multiple times
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
        time.sleep(0.5)  # Delay to avoid spam detection


# SUPER SIGMA: Kick from another server's voice channel
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
    activity = discord.Activity(type=discord.ActivityType.watching, name="over the server")
    await bot.change_presence(activity=activity)
    load_scores()
    print(f"{bot.user} is online!")


def runBot():
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))


print("Bot starting...")
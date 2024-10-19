import discord
from discord.ext import commands
import json
import os
import time
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
        time.sleep(0.5)  # Delay to avoid spam detection

# Slovník
@bot.slash_command(name="slovnik")
async def slovnik(ctx):
        await ctx.respond("The Classics: Skibidi, Grimace Shake, Fanum Tax, Doomscrolling, Chat, Kai Cenat, Edging, Rizzing, Gooning, Rizz, Rizzing, Sigma, Only in Ohio, 19 Dollar Fortnite card, Double Pump, Hitting the Griddy, Ice Spice, Level 100 Gyatt, Gooning cave, Discord Kitten, You make my heart burn\n \n Adjectives: Sus, Sussy, Sussy baka, Rizzler, Alpha, Beta, Sigma, Based, Chuds, Thot, Skibidi Sigma, Simp, Soyboy, Chads, Sturdy, Gamer, Incel, Cringe/Cringey, Furry, Discord Kitten, Streamer, Zesty, Boomer, Doomer, Coomer, Zoomer, Gooner, Goofy, Silly, Cracked at fortnite\n \n Brands/Franchises: Fortnite, Reddit, Youtube Shorts, TikTok, Mc Donalds, Gucci, Supreme, Discord, Roblox, Subway Surfers shorts, Family guy shorts, Tinder, Uber Eats,\n \n Streamers/People: Mr beast, Ice Spice, Kai cenat, Fanum, Caseoh, DaFuqBoom, Baby gronk, Master Oogway, Peter Griffin, Raven Team leader, Andrew tate, Ben Shapiro, Jordan Peterson, Elon Musk, Dababy, Lebron James, Kanye West.\n \n Sounds: Yeet, Oof, Leroy Jenkins, gyatt, Happy Happy Happy, Oh no!!\n \n Catchphrases: Leroy Jenkins, Hell naw, What the dog doin?, imma head out, Upgrades, people, more upgrades, Zoo wee mama, Deez Nuts, Shikanoko nokonoko Koshitantan, Only a spoonful, POV:, IS THAT A JOJO REFERENCE???, How bad can i be?, Why do i hear boss music, Aw shit here we go again, No, you are not a gamer\n \n Still water + adrenaline + noradrenaline + hawk tuah + anger issues + balkan parents + english or Spanish + german stare + Balkan rage + jonkler laugh +phonk + those who know=")
        await ctx.send("Ksi music + lunchly + winter arc + still water baths + nonadrenaline + flow state + MANGO MANGO phonk + Prime + Balkan\n \n Skibidi gyatt rizz only in ohio duke dennis did you pray today livvy dunne rizzing up baby gronk sussy imposter pibby glitch in real life sigma alpha omega male grindset andrew tate goon cave freddy fazbear colleen ballinger smurf cat vs strawberry elephant blud dawg shmlawg ishowspeed a whole bunch of turbulence ambatukam bro really thinks he s carti literally hitting the griddy the ocky way kai cenat fanum tax garten of banban no edging in class not the mosquito again bussing axel in harlem whopper whopper whopper whopper 1 2 buckle my shoe goofy ahh aiden ross sin city monday left me broken quirked up white boy busting it down sexual style goated with the sauce john pork grimace shake kiki do you love me huggy wuggy nathaniel b lightskin stare biggest bird omar the referee amogus uncanny wholesome reddit chungus keanu reeves pizza tower zesty poggers kumalala savesta quandale dingle glizzy rose toy ankha zone thug shaker morbin time dj khaled sisyphus oceangate shadow wizard money gang ayo the pizza here PLUH nair butthole waxing t-pose ugandan knuckles family guy funny moments compilation with subway surfers gameplay at the bottom nickeh30 ratio uwu delulu opium bird cg5 mewing fortnite battle pass all my fellas gta 6 backrooms gigachad based cringe kino redpilled no nut november pokénut november foot fetish F in the chat i love lean looksmaxxing gassy social credit bing chilling xbox live mrbeast kid named finger better caul saul i am a surgeon hit or miss i guess they never miss huh i like ya cut g ice spice gooning fr we go gym kevin james josh hutcherson coffin of andy and leyley metal pipe falling")

music = bot.create_group("music")

class musicbot(commands.Cog):
    def __int__(self, client):
        self.client = client
        self.queue = []

    @music.command()
    async def play(self, ctx, *, search):
        voice_channel = ctx.author.voice.channel if ctx.autohr.voice else None
        if not voice_channel:
            return await ctx.send("You are not connected to a voice channel")
        if not ctx.voice_client:
            await voice_channel.connect()

        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                url = info['url']
                title = info['title']
                self.queue.append(url, title)
                await ctx.send(f"Added to queue: **{title}**")
        if not ctx.voice_client.is_playing():
            await self.playnext(ctx)

    async def playnext(self, ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda _:self.client.loop.create_task(self.playnext(ctx)))
            await ctx.send(f"Now playing: **{title}**")
        elif not ctx.voice_client.is_playing():
            await ctx.send("queue is empty")

    @music.command()
    async def skip(self, ctx: discord.ApplicationContext):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("skipped")






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

import os
import csv
import aiohttp
import asyncio
from datetime import datetime, timedelta


from dotenv import load_dotenv
load_dotenv()

# Configuration via environment variables
STEAM_API_KEY  = os.getenv("STEAM_API_KEY")
STEAM_ID       = os.getenv("STEAM_ID")
CHANNEL_ID     = int(os.getenv("STEAM_CHANNEL_ID", "0"))
TARGET_GAME    = os.getenv("TARGET_GAME", "Marvel Rivals")
LOG_FILE = os.getenv("STEAM_LOG_FILE", "steam_activity.csv")

async def get_steam_status():
    # Fetch current game being played by the Steam user; returns game name or None
    url = (
        f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        f"?key={STEAM_API_KEY}&steamids={STEAM_ID}"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            player = data["response"]["players"][0]
            return player.get("gameextrainfo")


def log_session(start_time: datetime, duration: timedelta):
    # Log a completed play session with date and duration in seconds
    first = not os.path.isfile(LOG_FILE)
    date_str = start_time.date().isoformat()
    duration_sec = int(duration.total_seconds())
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if first:
            writer.writerow(["date", "duration_seconds"])
        writer.writerow([date_str, duration_sec])

async def monitor_steam(bot):
    # Background task: check every minute for play start/stop of TARGET_GAME
    last_playing = False
    start_time = None
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while True:
        try:
            game = await get_steam_status()
            playing = (game == TARGET_GAME)
            now = datetime.now()

            # Log the current status to the console
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Monitoring Steam: "
                  f"Game: {game if game else 'None'}, Playing Target: {playing}")

            # Started playing
            if playing and not last_playing:
                start_time = now
                await channel.send(f"negr zacal hrat **{TARGET_GAME}**")

            # Stopped playing
            if not playing and last_playing and start_time:
                duration = now - start_time
                log_session(start_time, duration)
                await channel.send(
                    f"negr prestal hrat **{TARGET_GAME}**; session duration {int(duration.total_seconds()/60)} min"
                )
                start_time = None

            last_playing = playing
        except Exception as e:
            print("Steam monitor error:", e)

        await asyncio.sleep(60)


def setup(bot):
    # Initialize the Steam tracker: start monitor and register slash command
    bot.loop.create_task(monitor_steam(bot))


import os
import csv
import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration via environment variables
STEAM_API_KEY  = os.getenv("STEAM_API_KEY")
STEAM_ID       = os.getenv("STEAM_ID")
CHANNEL_ID     = int(os.getenv("STEAM_CHANNEL_ID", "0"))
TARGET_GAME    = os.getenv("TARGET_GAME", "Marvel Rivals")
LOG_FILE       = os.getenv("STEAM_LOG_FILE", "steam_activity.csv")


async def get_steam_status():
    # Fetch current game being played by the Steam user; returns game name or None.
    url = (
        f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        f"?key={STEAM_API_KEY}&steamids={STEAM_ID}"
    )
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url) as resp:
                if resp.status == 429:
                    retry_after = int(resp.headers.get("Retry-After", 1))
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    continue
                elif resp.status != 200:
                    raise Exception(f"Error: {resp.status}, {await resp.text()}")
                data = await resp.json()
                player = data["response"]["players"][0]
                game = player.get("gameextrainfo")
                logger.debug(f"Fetched Steam status: {game}")
                return game


def log_session(start_time: datetime, duration: timedelta):
    """Log a completed play session with date and duration in seconds."""
    first = not os.path.isfile(LOG_FILE)
    date_str = start_time.date().isoformat()
    duration_sec = int(duration.total_seconds())

    try:
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if first:
                writer.writerow(["date", "duration_seconds"])
                logger.info(f"Created new log file and header: {LOG_FILE}")
            writer.writerow([date_str, duration_sec])
            logger.info(f"Logged session: {date_str}, {duration_sec} seconds")
    except Exception as e:
        logger.error(f"Failed to write session to log file: {e}")


async def monitor_steam(bot):
    """
    Background task: check every minute for play start/stop of TARGET_GAME
    and log accordingly.
    """
    last_playing = False
    start_time = None
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    logger.info(f"Starting Steam monitor for game: {TARGET_GAME}")

    while True:
        try:
            game = await get_steam_status()
            playing = (game == TARGET_GAME)
            now = datetime.now()

            logger.debug(f"Monitoring Steam: game={game}, playing={playing}")

            # Started playing and wasn't before
            if playing and not last_playing:
                start_time = now
                logger.info(f"Detected start of '{TARGET_GAME}' at {now.isoformat()}")
                if channel:
                    await channel.send(f"negr zacal hrat **{TARGET_GAME}**")
                else:
                    logger.warning(f"Channel ID {CHANNEL_ID} not found; cannot send start message")

            # Stopped playing with a required offline duration
            elif not playing and last_playing and start_time:
                if (now - start_time) > timedelta(minutes=2):  # Threshold of 2 minutes
                    duration = now - start_time
                    logger.info(f"Detected stop of '{TARGET_GAME}' at {now.isoformat()}, duration {duration}")
                    log_session(start_time, duration)
                    if channel:
                        minutes = int(duration.total_seconds() / 60)
                        await channel.send(
                            f"přestal goonovat nad  **{TARGET_GAME}**; goonil {minutes} min"
                        )
                    else:
                        logger.warning(f"Channel ID {CHANNEL_ID} not found; cannot send stop message")
                    start_time = None

            last_playing = playing

        except Exception as e:
            logger.error(f"Steam monitor error: {e}", exc_info=True)

        await asyncio.sleep(60)


def setup(bot):
    """Initialize the Steam tracker: start monitor task."""
    bot.loop.create_task(monitor_steam(bot))
    logger.info("Steam monitor task scheduled")

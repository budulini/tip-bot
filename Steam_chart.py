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
STEAM_DAILY_TOTAL_LOG = os.getenv("STEAM_DAILY_TOTAL_LOG_FILE", "steam_daily_total_totals.csv")

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





async def get_total_playtime():
    """Get the total playtime for TARGET_GAME from Steam API"""
    url = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={STEAM_API_KEY}&steamid={STEAM_ID}&format=json&include_appinfo=true"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                logger.error(f"Error getting total playtime: {resp.status}")
                return None

            data = await resp.json()
            games = data.get("response", {}).get("games", [])

            for game in games:
                if game.get("name") == TARGET_GAME:
                    # Steam returns playtime in minutes
                    return game.get("playtime_forever", 0)

    return None


def log_daily_total(date, minutes_played):
    """Log the daily total playtime to a separate CSV file"""
    file_exists = os.path.isfile(STEAM_DAILY_TOTAL_LOG)

    with open(STEAM_DAILY_TOTAL_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "minutes_played"])
        writer.writerow([date.isoformat(), minutes_played])
        logger.info(f"Logged daily total: {date.isoformat()}, {minutes_played} minutes")


async def daily_tracker(bot):
    """Task that records total playtime at start and end of day"""
    await bot.wait_until_ready()
    morning_total = None
    evening_total = None
    current_date = datetime.now().date()
    channel = bot.get_channel(CHANNEL_ID)

    logger.info(f"Starting daily total playtime tracker for game: {TARGET_GAME}")

    while True:
        try:
            now = datetime.now()
            current_time = now.time()

            # If the date changed, reset the tracking
            if now.date() != current_date:
                if morning_total is not None and evening_total is not None:
                    # Calculate and log the difference if we have both measurements
                    daily_minutes = evening_total - morning_total
                    log_daily_total(current_date, daily_minutes)

                    if channel and daily_minutes > 0:
                        await channel.send(
                            f"**{TARGET_GAME}** daily total: {daily_minutes / 60:.2f} hours"
                        )

                # Reset for the new day
                current_date = now.date()
                morning_total = None
                evening_total = None
                logger.info(f"Reset daily tracker for new date: {current_date}")

            # Morning measurement (00:00-00:05)
            if current_time.hour == 0 and current_time.minute <= 5 and morning_total is None:
                morning_total = await get_total_playtime()
                logger.info(f"Recorded morning total: {morning_total} minutes")

            # Evening measurement (23:55-23:59)
            elif current_time.hour == 23 and current_time.minute >= 55 and evening_total is None:
                evening_total = await get_total_playtime()
                logger.info(f"Recorded evening total: {evening_total} minutes")

        except Exception as e:
            logger.error(f"Daily tracker error: {e}", exc_info=True)

        await asyncio.sleep(60)  # Check every minute



def setup(bot):
    """Initialize the Steam trackers, ensuring only one instance runs."""
    global _setup_complete
    if _setup_complete:
        logger.info("Steam monitor setup already complete, skipping.")
        return

    logger.info("Performing Steam monitor setup...")
    bot.loop.create_task(monitor_steam(bot))
    bot.loop.create_task(daily_tracker(bot))
    _setup_complete = True # Mark setup as complete
    logger.info("Steam monitor tasks scheduled")

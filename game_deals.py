import aiohttp
import asyncio
import discord
from discord.ext import tasks
import logging
from datetime import datetime
import json
import os

# Configuration - you can modify these variables
REDDIT_SUBREDDIT = "GameDeals"  # The subreddit to monitor
DEALS_CHANNEL_ID = 1364245813533868122  # Replace with your channel ID
CHECK_INTERVAL_MINUTES = 30  # How often to check for new deals
USER_AGENT = "GameDeals/1.0"  # User agent for Reddit API

class GameDealsClient:
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.last_deal_id = None
        self.is_monitoring = False  # Flag to prevent multiple instances
        self.load_last_deal_id()

    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"User-Agent": USER_AGENT}
            )
        return self.session

    def load_last_deal_id(self):
        """Load the last deal ID from file to avoid duplicate notifications"""
        try:
            # Create files directory if it doesn't exist
            os.makedirs('files', exist_ok=True)
            with open('files/last_deal.json', 'r') as f:
                data = json.load(f)
                self.last_deal_id = data.get('last_deal_id')
                logging.info(f"Loaded last deal ID: {self.last_deal_id}")
        except (FileNotFoundError, json.JSONDecodeError):
            self.last_deal_id = None
            logging.info("No previous deal ID found, starting fresh")

    def save_last_deal_id(self, deal_id):
        """Save the last deal ID to file"""
        try:
            os.makedirs('files', exist_ok=True)
            with open('files/last_deal.json', 'w') as f:
                json.dump({'last_deal_id': deal_id}, f)
            self.last_deal_id = deal_id
            logging.info(f"Saved last deal ID: {deal_id}")
        except Exception as e:
            logging.error(f"Error saving last deal ID: {e}")

    async def get_latest_deal_from_reddit(self):
        """Fetch the latest game deal from Reddit"""
        try:
            session = await self.get_session()
            url = f"https://www.reddit.com/r/{REDDIT_SUBREDDIT}/new.json?limit=10"

            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = data.get('data', {}).get('children', [])

                    for post in posts:
                        post_data = post.get('data', {})
                        title = post_data.get('title', '').lower()

                        # Filter for actual deals (you can adjust these filters)
                        deal_keywords = ['free', 'sale', 'deal', 'discount', '%', 'off', 'steam', 'epic', 'gog', 'humble']
                        if any(keyword in title for keyword in deal_keywords):
                            return {
                                'redditId': post_data.get('id'),
                                'redditTitle': post_data.get('title', 'No title'),
                                'gameUrl': post_data.get('url', ''),
                                'createdAt': datetime.fromtimestamp(post_data.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                                'permalink': f"https://reddit.com{post_data.get('permalink', '')}"
                            }

                    logging.info("No new deals found in recent posts")
                    return None
                else:
                    logging.error(f"Reddit API returned status {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Error fetching latest deal from Reddit: {e}")
            return None

    def format_deal_message(self, deal):
        """Format a deal into a Discord message"""
        created_at = deal.get('createdAt', 'Unknown')
        title = deal.get('redditTitle', 'No title')
        game_url = deal.get('gameUrl', '')
        permalink = deal.get('permalink', '')

        message = f"🎮 **New Game Deal Found!**\n\n"
        message += f"📅 **Found at:** {created_at}\n"
        message += f"**{title}**\n"
        if game_url and game_url != permalink:
            message += f"🔗 **Store:** <{game_url}>\n"

        return message

    async def send_deal_notification(self, deal):
        """Send a deal notification to the specified channel"""
        try:
            channel = self.bot.get_channel(DEALS_CHANNEL_ID)
            if not channel:
                logging.error(f"Could not find channel with ID {DEALS_CHANNEL_ID}")
                return

            message = self.format_deal_message(deal)
            await channel.send(message)
            logging.info(f"Sent deal notification: {deal.get('redditTitle', 'Unknown')}")

        except Exception as e:
            logging.error(f"Error sending deal notification: {e}")

    @tasks.loop(minutes=CHECK_INTERVAL_MINUTES)
    async def check_for_new_deals(self):
        """Periodically check for new deals and send notifications"""
        try:
            logging.info("Checking for new game deals...")
            deal = await self.get_latest_deal_from_reddit()
            if not deal:
                logging.info("No new deals found")
                return

            deal_id = deal.get('redditId')
            if deal_id and deal_id != self.last_deal_id:
                await self.send_deal_notification(deal)
                self.save_last_deal_id(deal_id)
            else:
                logging.info(f"Deal {deal_id} already processed")

        except Exception as e:
            logging.error(f"Error in check_for_new_deals: {e}")

    @check_for_new_deals.before_loop
    async def before_check_for_new_deals(self):
        """Wait for the bot to be ready before starting the loop"""
        await self.bot.wait_until_ready()
        logging.info("Game deals monitoring is ready to start")

    def start_monitoring(self):
        """Start monitoring for new deals (only if not already running)"""
        if not self.is_monitoring and not self.check_for_new_deals.is_running():
            self.check_for_new_deals.start()
            self.is_monitoring = True
            logging.info(f"Started automatic game deals monitoring from r/{REDDIT_SUBREDDIT}")
            logging.info(f"Will check every {CHECK_INTERVAL_MINUTES} minutes")
            logging.info(f"Will post to channel ID: {DEALS_CHANNEL_ID}")
        else:
            logging.info("Game deals monitoring is already running")

    def stop_monitoring(self):
        """Stop monitoring for new deals"""
        if self.check_for_new_deals.is_running():
            self.check_for_new_deals.cancel()
        self.is_monitoring = False
        logging.info("Stopped game deals monitoring")

    async def close(self):
        """Clean up resources"""
        self.stop_monitoring()
        if self.session and not self.session.closed:
            await self.session.close()

def setup_game_deals(bot):
    """Set up game deals monitoring and return the client instance"""
    logging.info("Setting up game deals monitoring...")
    deals_client = GameDealsClient(bot)

    # Start monitoring automatically
    deals_client.start_monitoring()

    return deals_client

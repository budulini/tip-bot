import asyncio
import json
import logging
import aiohttp
import discord
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

class FreeStuffBot:
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.last_check = datetime.now()
        self.sent_deals = set()  # Track sent deals to avoid duplicates

        # CONFIGURE THESE SETTINGS:
        self.TARGET_CHANNEL_ID = 1364245813533868122  # Replace with your channel ID
        self.CHECK_INTERVAL = 300  # Check every 5 minutes (300 seconds)

        # File to store last deals to prevent duplicates on restart
        self.LAST_DEALS_FILE = "files/last_deal.json"

        # APIs for free game deals
        self.apis = {
            'epic_games': 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions',
            'steam_free': 'https://store.steampowered.com/api/featuredcategories/',
            'gog_free': 'https://www.gog.com/games/ajax/filtered?mediaType=game&price=free',
            'itch_free': 'https://itch.io/api/1/search?q=free&classification=game',
        }

        self.load_last_deals()

    def load_last_deals(self):
        """Load previously sent deals from file"""
        try:
            if os.path.exists(self.LAST_DEALS_FILE):
                with open(self.LAST_DEALS_FILE, 'r') as f:
                    data = json.load(f)
                    self.sent_deals = set(data.get('sent_deals', []))
                    last_check_str = data.get('last_check')
                    if last_check_str:
                        self.last_check = datetime.fromisoformat(last_check_str)
        except Exception as e:
            logging.error(f"Error loading last deals: {e}")
            self.sent_deals = set()

    def save_last_deals(self):
        """Save sent deals to file"""
        try:
            os.makedirs(os.path.dirname(self.LAST_DEALS_FILE), exist_ok=True)
            with open(self.LAST_DEALS_FILE, 'w') as f:
                json.dump({
                    'sent_deals': list(self.sent_deals),
                    'last_check': self.last_check.isoformat()
                }, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving last deals: {e}")

    async def start_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    async def fetch_epic_games_deals(self) -> List[Dict]:
        """Fetch free games from Epic Games Store"""
        try:
            async with self.session.get(self.apis['epic_games']) as response:
                if response.status == 200:
                    data = await response.json()
                    deals = []

                    games = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])
                    for game in games:
                        promotions = game.get('promotions', {})
                        promotional_offers = promotions.get('promotionalOffers', [])

                        if promotional_offers:
                            for offer in promotional_offers:
                                for promo in offer.get('promotionalOffers', []):
                                    discount_percentage = promo.get('discountSetting', {}).get('discountPercentage', 0)
                                    if discount_percentage == 0:  # Free game
                                        deals.append({
                                            'title': game.get('title', 'Unknown'),
                                            'description': game.get('description', ''),
                                            'url': f"https://store.epicgames.com/en-US/p/{game.get('catalogNs', {}).get('mappings', [{}])[0].get('pageSlug', '')}" if game.get('catalogNs', {}).get('mappings') else '',
                                            'image': game.get('keyImages', [{}])[0].get('url', '') if game.get('keyImages') else '',
                                            'end_date': promo.get('endDate'),
                                            'platform': 'Epic Games Store',
                                            'original_price': game.get('price', {}).get('totalPrice', {}).get('fmtPrice', {}).get('originalPrice', 'Unknown'),
                                            'id': f"epic_{game.get('id', '')}"
                                        })
                    return deals
        except Exception as e:
            logging.error(f"Error fetching Epic Games deals: {e}")
        return []

    async def fetch_steam_deals(self) -> List[Dict]:
        """Fetch free games from Steam"""
        try:
            # Steam free to play games
            steam_free_url = "https://store.steampowered.com/api/appdetails?appids=730&filters=basic"  # Example
            # Note: Steam's API is limited, this is a simplified example
            # For a full implementation, you'd need to scrape or use unofficial APIs
            return []
        except Exception as e:
            logging.error(f"Error fetching Steam deals: {e}")
        return []

    async def fetch_itch_deals(self) -> List[Dict]:
        """Fetch free games from itch.io"""
        try:
            # Note: itch.io doesn't have a public API for this
            # This would require web scraping in a real implementation
            return []
        except Exception as e:
            logging.error(f"Error fetching itch.io deals: {e}")
        return []

    async def create_deal_embed(self, deal: Dict) -> discord.Embed:
        """Create a Discord embed for a deal"""
        embed = discord.Embed(
            title=f"🎮 FREE: {deal['title']}",
            description=deal.get('description', '')[:2048],  # Discord embed description limit
            color=0x00ff00,  # Green color for free deals
            timestamp=datetime.now()
        )

        if deal.get('url'):
            embed.url = deal['url']

        if deal.get('image'):
            embed.set_image(url=deal['image'])

        embed.add_field(
            name="Platform",
            value=deal.get('platform', 'Unknown'),
            inline=True
        )

        if deal.get('original_price'):
            embed.add_field(
                name="Original Price",
                value=deal['original_price'],
                inline=True
            )

        if deal.get('end_date'):
            try:
                end_date = datetime.fromisoformat(deal['end_date'].replace('Z', '+00:00'))
                embed.add_field(
                    name="Ends",
                    value=f"<t:{int(end_date.timestamp())}:R>",
                    inline=True
                )
            except:
                pass

        embed.set_footer(text="FreeStuff Bot • Get these deals while they last!")

        return embed

    async def check_for_deals(self):
        """Check all sources for new free game deals"""
        try:
            await self.start_session()

            all_deals = []

            # Fetch from Epic Games
            epic_deals = await self.fetch_epic_games_deals()
            all_deals.extend(epic_deals)

            # Add other sources here
            # steam_deals = await self.fetch_steam_deals()
            # all_deals.extend(steam_deals)

            # Filter out deals we've already sent
            new_deals = [deal for deal in all_deals if deal.get('id') not in self.sent_deals]

            if new_deals:
                channel = self.bot.get_channel(self.TARGET_CHANNEL_ID)
                if channel:
                    for deal in new_deals:
                        try:
                            embed = await self.create_deal_embed(deal)
                            await channel.send(embed=embed)

                            # Mark as sent
                            if deal.get('id'):
                                self.sent_deals.add(deal['id'])

                            logging.info(f"Sent deal: {deal['title']}")

                            # Small delay between messages
                            await asyncio.sleep(1)

                        except Exception as e:
                            logging.error(f"Error sending deal {deal.get('title', 'Unknown')}: {e}")

                    # Save sent deals
                    self.save_last_deals()
                else:
                    logging.error(f"Could not find channel with ID: {self.TARGET_CHANNEL_ID}")

            self.last_check = datetime.now()

        except Exception as e:
            logging.error(f"Error in check_for_deals: {e}")

    async def deals_loop(self):
        """Main loop for checking deals"""
        await self.bot.wait_until_ready()
        logging.info("FreeStuff Bot started - checking for deals...")

        while not self.bot.is_closed():
            try:
                await self.check_for_deals()
                await asyncio.sleep(self.CHECK_INTERVAL)
            except Exception as e:
                logging.error(f"Error in deals loop: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying

class ManualDealsAPI:
    """Alternative API sources that can be added"""

    @staticmethod
    async def fetch_gamerpower_deals(session) -> List[Dict]:
        """Fetch from GamerPower API (free games and DLC)"""
        try:
            url = "https://www.gamerpower.com/api/giveaways?platform=pc&type=game"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    deals = []

                    for giveaway in data:
                        if 'free' in giveaway.get('worth', '').lower() or giveaway.get('worth') == '$0.00':
                            deals.append({
                                'title': giveaway.get('title', 'Unknown'),
                                'description': giveaway.get('description', ''),
                                'url': giveaway.get('gamerpower_url', ''),
                                'image': giveaway.get('image', ''),
                                'end_date': giveaway.get('end_date'),
                                'platform': 'Multiple Platforms',
                                'original_price': giveaway.get('worth', 'Unknown'),
                                'id': f"gamerpower_{giveaway.get('id', '')}"
                            })
                    return deals
        except Exception as e:
            logging.error(f"Error fetching GamerPower deals: {e}")
        return []

def setup_game_deals(bot):
    """Setup function called from main bot"""
    free_stuff_bot = FreeStuffBot(bot)

    # Start the deals checking loop
    bot.loop.create_task(free_stuff_bot.deals_loop())

    # Add cleanup when bot shuts down
    @bot.event
    async def on_disconnect():
        await free_stuff_bot.close_session()

    return free_stuff_bot

# Example manual command to force check (optional)
async def manual_check_command(ctx, free_stuff_bot):
    """Manual command to force check for deals"""
    await ctx.send("🔍 Checking for new free game deals...")
    await free_stuff_bot.check_for_deals()
    await ctx.send("✅ Deal check completed!")

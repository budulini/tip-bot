import discord
from discord.ext import commands
import yt_dlp

# Music cog for handling music commands
class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}

    # Helper function to extract audio stream URL from YouTube
    def search_youtube(self, query):
        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': 'True'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            except Exception:
                return False
        return info['url']

    # Join voice channel command
    @commands.slash_command(name="join")
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.respond(f"Joined {channel}")
        else:
            await ctx.respond("You need to be in a voice channel to use this command.")

    # Leave voice channel command
    @commands.slash_command(name="leave")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.guild.voice_client.disconnect()
            await ctx.respond("Left the voice channel.")
        else:
            await ctx.respond("I'm not in a voice channel.")

    # Play music command
    @commands.slash_command(name="play")
    async def play(self, ctx, query: str):
        voice_client = ctx.guild.voice_client

        if not voice_client:
            await ctx.respond("I'm not connected to a voice channel.")
            return

        url = self.search_youtube(query)

        if not url:
            await ctx.respond("Could not find the song.")
            return

        # Stop any existing audio playing
        if voice_client.is_playing():
            voice_client.stop()

        # Play the audio stream from the URL
        voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: print(f"Error: {e}") if e else None)
        await ctx.respond(f"Now playing: {query}")

    # Pause the current song
    @commands.slash_command(name="pause")
    async def pause(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.respond("Paused the song.")
        else:
            await ctx.respond("No song is currently playing.")

    # Resume the paused song
    @commands.slash_command(name="resume")
    async def resume(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.respond("Resumed the song.")
        else:
            await ctx.respond("No song is currently paused.")

    # Stop the current song
    @commands.slash_command(name="stop")
    async def stop(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.respond("Stopped the song.")
        else:
            await ctx.respond("No song is currently playing.")

# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(MusicCog(bot))
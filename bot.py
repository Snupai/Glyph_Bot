import asyncio
import logging
from pathlib import Path
import uuid
import validators
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from dotenv import load_dotenv
import os
import yt_dlp as youtube_dl
import subprocess
import datetime

make_ephemeral = False

# Load the environment variables from .env file
load_dotenv()

# Create a new bot instance
intents = discord.Intents()
intents.members = True
intents.message_content = True

bot = commands.AutoShardedBot(intents=intents, sync_commands=False, help_command=None)


# Create a logger with timestamp in the file name

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"bot_{timestamp}.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler and set the log level
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create a formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

activity: str = "/help"

@bot.event
async def on_command_error(ctx, error):
    """
    Event triggered when a command fails.
    """
    logger.error(f"Command {ctx.command} failed with error: {str(error)}")

@bot.event
async def on_ready():
    """
    Event triggered when the bot is ready.
    """
    logger.info(f'Logged in as {bot.user.name}')
    logger.info(f'ID: {bot.user.id}')

    activity = "/help"

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=activity))

    # delete all commands and recreate them
    await bot.sync_commands()

@tasks.loop(minutes=1)
async def change_activity():
    """
    Change the bot's activity every 60 seconds.
    """
    # Set the activity
    global activity # make 'activity' a global variable so it can be accessed by the function

    
    if activity == "/help":
        activity = "Having fun"
    elif activity == "Having fun":
        activity = "Nya"
    elif activity == "Nya":
        activity = "/help"

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=activity))

change_activity.start()


@bot.slash_command()
async def ping(ctx):
    """
    Command to check if the bot is online.
    """
    logger.info(f"{ctx.author} used /ping command in {ctx.channel} on {ctx.guild}.")
    await ctx.respond(f'Pong! {round(bot.latency * 1000)}ms', ephemeral=make_ephemeral)

@bot.slash_command()
async def about(ctx):
    """
    Command to display information about the bot.
    """
    logger.info(f"{ctx.author} used /about command in {ctx.channel} on {ctx.guild}.")

    # Create an embed
    embed = discord.Embed(title="About the bot")
    embed.description = "This discord bot is an easy interface for the Custom Glyph tools. It uses the scripts created by <@429776328833761280> to create and visualize custom glyphs. You can find the source code for the tools at the following links:"
    embed.set_footer(text="Click a button to navigate to the according Github Repo.")

    # Create a button row
    row = View()

    # Create buttons
    button1 = Button(style=discord.ButtonStyle.primary, label="SebiAi/custom-nothing-glyph-tools", url="https://github.com/SebiAi/custom-nothing-glyph-tools", emoji="🔧")
    button2 = Button(style=discord.ButtonStyle.primary, label="SebiAi/GlyphVisualizer", url="https://github.com/SebiAi/GlyphVisualizer", emoji="🔍")

    # Add buttons to the row
    row.add_item(button1)
    row.add_item(button2)

    # Add the button row to the embed
    await ctx.respond(embed=embed, view=row, ephemeral=make_ephemeral)

@bot.slash_command(name="help")
async def help(ctx):
    """
    Command to display the help message.
    """
    logger.info(f"{ctx.author} used /help command in {ctx.channel} on {ctx.guild}.")

    # Create an embed
    embed = discord.Embed(title="Help")
    embed.description = "This bot provides an easy interface for the Custom Glyph tools. You can use the following commands to create and visualize custom glyphs:"
    embed.add_field(name="/ping", value="Check if the bot is online.", inline=False)
    embed.add_field(name="/about", value="Display information about the bot.", inline=False)
    embed.add_field(name="/create", value="Create a custom glyph.", inline=False)
    embed.add_field(name="/visualize", value="Visualize a custom glyph.", inline=False)
    embed.add_field(name="/publish", value="Publish a custom glyph to our database.", inline=False)
    embed.add_field(name="/search", value="Search for a custom glyph.", inline=False)
    embed.add_field(name="/help", value="Display this help message.", inline=False)

    # Send the embed
    await ctx.respond(embed=embed, ephemeral=make_ephemeral)

@bot.slash_command(name="dl_trim", description="Plays audio from a URL at a specific time")
async def dl_trim(ctx,
                   url: str = discord.Option(name="audio_url", description="The audio file URL", required=True),
                   begin: float = discord.Option(name="start_time", description="The time to start playing the audio in seconds", default=0.0),
                   end: float = discord.Option(name="end_time", description="The time to stop playing the audio in seconds", default=None)):
    """
    Command to play audio from a URL at a specific time.
    """
    logger.info(f"{ctx.author} used /dl_trim command in {ctx.channel} on {ctx.guild}.")

    # acknowledge the command without sending a response
    await ctx.defer()

    try:
        if not validators.url(url):
            await ctx.respond(content="Invalid URL provided.")
            return
    except Exception as e:
        await ctx.respond(content=f"Error validating URL: {str(e)}", ephemeral=True)
        return

    ydl = youtube_dl.YoutubeDL()
    try:
        info = ydl.extract_info(url, download=False)
    except youtube_dl.DownloadError:
        await ctx.respond(content="Error extracting info from the URL.", ephemeral=True)
        return

    if end is None:
        end = info['duration']
    title = info['title']

    title += f"_{uuid.uuid4()}"

    # Validate begin and end times
    try:
        begin = float(begin)
        end = float(end)
    except ValueError:
        await ctx.respond(content="Invalid begin or end time.", ephemeral=True)
        return

    if begin < 0.0 or end < 0.0 or begin > end or end > info['duration']:
        await ctx.respond(content="Invalid begin or end time.", ephemeral=True)
        return

    # use youtube-dl to download the audio file from the url and trim it to the specified time range
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{title}.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nooverwrites': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
            'preferredquality': '192',
        }],
    }
    loop = asyncio.get_event_loop()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            await loop.run_in_executor(None, lambda: ydl.download([url]))
        except youtube_dl.DownloadError as e:
            await ctx.respond(content=f"Error downloading the audio file: {e}", ephemeral=True)
            return

    # Run ffmpeg using asyncio.create_subprocess_exec
    ffmpeg_cmd = ['ffmpeg', '-i', f'{title}.opus', '-ab', '189k', '-ss', str(begin), '-t', str(end - begin), '-acodec', 'libopus', f'{title}.ogg']
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        # Handle the error if ffmpeg failed
        await ctx.respond(content=f"Error trimming the audio file: {stderr.decode()}", ephemeral=True)
        return

    # Send the audio file
    try:
        await ctx.respond(content="Here's your audio! Enjoy! 🎵", file=discord.File(f'{title}.ogg'))
    finally:
        # Clean up files
        for extension in ['.opus', '.ogg']:
            audio_file = Path(f'{title}{extension}')
            if audio_file.is_file():
                audio_file.unlink()

@bot.slash_command(name="create", description="Create a custom glyph")
async def create(ctx: commands.Context, name: str = discord.Option(name="name", description="The name of the custom glyph", required=True)):
    """
    Command to create a custom glyph
    """
    logger.info(f"{ctx.author} used /create command in {ctx.channel} on {ctx.guild}.")

    # acknowledge the command without sending a response
    await ctx.respond(content="Not done yet...")


# Run the bot
bot.run(os.getenv('BOT_TOKEN'))
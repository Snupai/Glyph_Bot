import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import os

make_ephemeral = False

# Load the environment variables from .env file
load_dotenv()

# Create a new bot instance
intents = discord.Intents.all()
intents.members = True
intents.integrations = True
intents.dm_typing = True
intents.dm_reactions = True
intents.dm_messages = True
intents.moderation = False
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents, sync_commands=True, help_command=None)


@bot.event
async def on_ready():
    """
    Event triggered when the bot is ready.
    """
    print(f'Logged in as {bot.user.name}')
    print(f'ID: {bot.user.id}')

    # Set the activity
    await bot.change_presence(activity=discord.Game(name="/help"))

    # delete all commands and recreate them
    await bot.sync_commands()

@bot.slash_command()
async def ping(ctx):
    """
    Command to check if the bot is online.
    """
    print(f"{ctx.author} used /ping command in {ctx.channel} on {ctx.guild}.")
    await ctx.respond(f'Pong! {round(bot.latency * 1000)}ms', ephemeral=make_ephemeral)

@bot.slash_command()
async def about(ctx):
    """
    Command to display information about the bot.
    """
    print(f"{ctx.author} used /about command in {ctx.channel} on {ctx.guild}.")

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
    print(f"{ctx.author} used /help command in {ctx.channel} on {ctx.guild}.")

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




 # Cooldown Management
@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(error)
    else:
        raise error

# Run the bot
bot.run(os.getenv('BOT_TOKEN'))
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import os
from discord.app_commands import Choice
from discord import app_commands

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

bot = commands.Bot(command_prefix='!', intents=intents, sync_commands=True, sync_commands_debug=True)


@bot.event
async def on_ready():
    """
    Event triggered when the bot is ready.
    """
    print(f'Logged in as {bot.user.name}')
    print(f'ID: {bot.user.id}')

    # Set the activity
    await bot.change_presence(activity=discord.Game(name="!help"))

    # Add the commands to the bot
    await bot.tree.sync()

@bot.hybrid_command(ephemeral=True)
async def ping(ctx):
    """
    Command to check if the bot is online.
    """
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms', ephemeral=True)

@bot.hybrid_command(ephemeral=True)
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
    await ctx.send(embed=embed, view=row, ephemeral=True)

@bot.hybrid_command(ephemeral=True)
@app_commands.describe(name="The name of the composition", phone="The phone for the composition")
@app_commands.choices(phone=[Choice(name="NP1", value="A063"), Choice(name="NP2", value="A065"), Choice(name="NP2a", value="A142")])
async def upload_composition(ctx, name: str, phone: str):
    await ctx.send(f"Option: {phone}, Name: {name}", ephemeral=True)

# Run the bot
bot.run(os.getenv('BOT_TOKEN'))



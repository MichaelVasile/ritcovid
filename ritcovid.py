from dotenv import load_dotenv
import os
import requests
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import time
import logging

# Bot version number
VERSION = "3.1"

# Load .env
load_dotenv()

# Load API Token from .env
TOKEN = os.getenv("API_TOKEN")

# Set Logger Channel for Debugging in .env
LOGGER_CHANNEL = os.getenv("LOGGER_CHANNEL")

# Set client parameters1
client = commands.Bot(command_prefix=".", intents=discord.Intents.all())
client.remove_command('help')

# to get uptime
startTime = time.time()

# Configure logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='logger.log', encoding='utf-8', mode='a+')
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(handler)


# Startup message
print(f"RIT COVID-19 Tracking Bot v{VERSION} by Michael Vasile\n")


def get_data_from_api():
    url = "https://ritcoviddashboard.com/api/v0/latest"
    response = requests.get(url)
    data = response.json()
    
    return data


def get_historical_data_from_api():
    url = "https://ritcoviddashboard.com/api/v0/history"
    response = requests.get(url)
    data = response.json()
    
    return data


def get_statistics():

    # Call API for latest statistics
    data = get_data_from_api()
    
    # Statistics from API
    last_updated = data["last_updated"]
    total_students = data["total_students"]
    total_staff = data["total_staff"]
    new_students = data["new_students"]
    new_staff = data["new_staff"]

    return last_updated, total_students, total_staff, new_students, new_staff


def get_difference():

    # Call API for latest and historical statistics
    latest = get_data_from_api()
    historical = get_historical_data_from_api()
    previous_day = historical[-2]

    new_students = latest["new_students"] - previous_day["new_students"]
    new_staff = latest["new_staff"] - previous_day["new_staff"]
    total_students = latest["total_students"] - previous_day["total_students"]
    total_staff = latest["total_staff"] - previous_day["total_staff"]

    return new_students, new_staff, total_students, total_staff


@client.command(pass_context=True)
async def stats(ctx):
    statistics = get_statistics()
    difference = get_difference()

    embed = discord.Embed(
        title="Latest RIT COVID-19 Statistics",
        description=(f"Current statistics as of: {statistics[0]}\n[Source](https://ritcoviddashboard.com)"),
        colour=0xF6BE00,
        timestamp=datetime.now()
    )

    embed.add_field(name="New Cases from Past 14 Days", value=(f"{statistics[3]} students ({difference[0]:+g}), {statistics[4]} employees ({difference[1]:+g})"), inline=False)
    embed.add_field(name="All Confirmed Cases",
                    value=(f"{statistics[1]} students ({difference[2]:+g}), {statistics[2]} employees ({difference[3]:+g})"), inline=False)

    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def alertlevel(ctx):

    embed = discord.Embed(
        title="RIT COVID-19 Alert Level",
        description='RIT has discontinued the COVID-19 Alert Level.',
        colour=0xd42828,
    )

    await ctx.send(embed=embed)

# Get the bot's current uptime from load
def get_uptime():
    uptime = timedelta(seconds=(time.time() - startTime))
    days = uptime.days
    hours = uptime.seconds // 3600
    minutes = (uptime.seconds // 60) % 60
    seconds = uptime.seconds % 60

    return "%dd %dh %dm %ds" % (days, hours, minutes, seconds)


@client.command(pass_context=True)
async def botinfo(ctx):
    embed = discord.Embed(
        title="RIT COVID-19 Tracking Bot",
        description=f"Created by Mike Vasile - Version {VERSION}\nSpecial Thanks to [Galen Guyer](https://galenguyer.com) & [Shantanav Saurav](https://shantanav.com)",
    )

    embed.add_field(name="Uptime", value=f"{get_uptime()}")

    await ctx.send(embed=embed)

# The help command
@client.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(
        title="RIT COVID-19 Tracking Bot",
        description=f"Help Menu\nAll commands are prefixed with '.'\nNOTE: RIT has discontinued the Alert Level system, so the bot's Alert functionality has been discontinued.",
    )

    embed.add_field(name=".help", value="Displays this message", inline=False)
    embed.add_field(name=".stats", value="Displays the latest statistics from RIT's COVID-19 Dashboard", inline=False)
    embed.add_field(name=".botinfo", value="Displays bot information, including version number and uptime.",
                    inline=False)

    await ctx.send(embed=embed)


@client.event
async def on_ready():
    print("Starting bot...")

    # Set status
    await client.change_presence(status=discord.Status.online, activity=discord.Game("RIT COVID Stats | .stats"))

    # Send ready message
    print("Bot is ready.")

    with open("logger.log", "a+") as f:
            f.write(f"** Bot initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} **\n")


# Launch client
client.run(TOKEN)

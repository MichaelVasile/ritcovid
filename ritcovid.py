from dotenv import load_dotenv
import os
import urllib.request
import json
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import time

# Bot version number
VERSION = "3.0"

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

# Startup message
print(f"RIT COVID-19 Tracking Bot v{VERSION} by Michael Vasile\n")


def get_data_from_api():
    url = "https://ritcoviddashboard.com/api/v0/latest"
    user_agent = 'covidbot'
    headers={'User-Agent':user_agent,} 

    request = urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(request)
    data = json.loads(response.read())

    return data


def get_historical_data_from_api():
    url = "https://ritcoviddashboard.com/api/v0/history"
    user_agent = 'covidbot'
    headers = {'User-Agent': user_agent, }

    request = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(request)
    data = json.loads(response.read())

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


@client.command(pass_context=True)
async def stats(ctx):
    statistics = get_statistics()

    embed = discord.Embed(
        title="Latest RIT COVID-19 Statistics",
        description=(f"Current statistics as of: {statistics[0]}\n[Source](https://ritcoviddashboard.com)"),
        colour=0xF6BE00,
        timestamp=datetime.now()
    )

    embed.add_field(name="New Cases from Past 14 Days", value=(f"{statistics[3]} students, {statistics[4]} employees"), inline=False)
    embed.add_field(name="All Confirmed Cases",
                    value=(f"{statistics[1]} students, {statistics[2]} employees"), inline=False)

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


@tasks.loop(seconds=300)
async def logger_check():
    # Get the last modified time of the file
    mod_time = os.path.getmtime("logger.log")
    file_age = time.time() - os.path.getmtime("logger.log")

    if file_age > 120:
        embed = discord.Embed(
            title="Logger error",
            description=f"No logger output since {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))}",
            colour=0x009CBD,
        )

        # Send to the test server's logger channel
        await LOGGER_CHANNEL.send(embed=embed)

@client.event
async def on_ready():
    print("Starting bot...")

    # Set status
    await client.change_presence(status=discord.Status.online, activity=discord.Game("RIT COVID Stats | .stats"))

    # Send ready message
    print("Bot is ready.")

    with open("logger.log", "a+") as f:
            f.write(f"** Bot initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} **\n")

    # logger_check.start()


# Launch client
client.run(TOKEN)

from dotenv import load_dotenv
import os
import urllib.request, json
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import time

# Bot version number
VERSION = "2.0 BETA"

# Load .env
load_dotenv()

# Load API Token from .env
TOKEN = os.getenv("API_TOKEN")

# Set client parameters1
client = commands.Bot(command_prefix=".")
client.remove_command('help')

# Load channel IDs from .env
ENV_VARS = ["TEST", "DISCO", "RIT", "NATE", "EEEE", "LGBT"]
KEYS = [int(os.getenv(key)) for key in ENV_VARS]

# Declare channels list for referencing
CHANNELS = []

# to get uptime
startTime = time.time()

# Startup message
print(f"RIT COVID-19 Tracking Bot v{VERSION} by Michael Vasile\n")


def get_data_from_api():
    url = "https://ritcoviddashboard.com/api/v0/latest"
    user_agent = 'covidbot-test'
    headers={'User-Agent':user_agent,} 

    request = urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(request)
    data = json.loads(response.read())

    return data

def get_alert_level():
    data = get_data_from_api()

    alert_level = data["alert_level"]

    color = 0x000000

    if "green" in alert_level:
        alert_level = "Green (Low Risk with Vigilance)"
        color = 0x60c10c
    elif "yellow" in alert_level:
        alert_level = "Yellow (Moderate Risk)"
        color = 0xf6be00
    elif "orange" in alert_level:
        alert_level = "Orange (Moderate to High Risk)"
        color = 0xf76902
    elif "Red" in alert_level:
        alert_level = "Red (High to Severe Risk)"
        color = 0xda291c

    return alert_level, color


def get_statistics():

    # Call API for latest statistics
    data = get_data_from_api()
    
    # Statistics from API
    last_updated = data["last_updated"]
    total_students = data["total_students"]
    total_staff = data["total_staff"]
    new_students = data["new_students"]
    new_staff = data["new_staff"]
    campus_quarantine = data["quarantine_on_campus"]
    offcampus_quarantine = data["quarantine_off_campus"]
    campus_isolated = data["isolation_on_campus"]
    offcampus_isolated = data["isolation_off_campus"]
    tests_administered = data["tests_administered"]
    beds_available = data["beds_available"]

    return last_updated, total_students, total_staff, new_students, new_staff, campus_quarantine, offcampus_isolated, \
            campus_isolated, offcampus_isolated, tests_administered, beds_available


def check_last_known():
    # Check to see if the file does not exist or is empty.
    if os.path.exists("last_known.txt") == False or os.path.getsize("last_known.txt") == 0:

        print("last_known.txt does not exist or is empty. Will create it now...")

        with open("last_known.txt", "w+") as f:
            # Populate the file
            f.write(get_alert_level()[0])

    else:
        print("last_known.txt has valid data.")


def get_last_known():
    last_known = str()
    # Open the file for reading
    with open("last_known.txt", "r") as f:
        # Read first line into the file
        last_known = f.readline()

    # Return the last known alert level as a string
    return last_known


def update_last_known():
    # Open text file containing the last known alert level for editing
    with open("last_known.txt", "w+") as f:
        # Write the new alert level to the file
        f.write(get_alert_level()[0])


@client.command(pass_context=True)
async def stats(ctx):
    alert_level = get_alert_level()
    statistics = get_statistics()

    embed = discord.Embed(
        title="Latest RIT COVID-19 Statistics",
        description=(f"Current statistics as of: {statistics[0]}\n[Source](https://ritcoviddashboard.com)"),
        colour=alert_level[1],
        timestamp=datetime.now()
    )

    embed.add_field(name="RIT COVID-19 Alert Level", value=alert_level[0], inline=False)
    embed.add_field(name="All Confirmed Cases",
                    value=(f"{statistics[1]} students, {statistics[2]} employees"), inline=False)
    embed.add_field(name="New Cases from Past 14 Days", value=(f"{statistics[3]} students, {statistics[4]} employees"), inline=False)
    embed.add_field(name="Students Quarantined", value=(f"{statistics[5]} on campus, {statistics[6]} off campus ({str(int(statistics[5]) + int(statistics[6]))} total)"), inline=False)
    embed.add_field(name="Students Isolated", value=(f"{statistics[7]} on campus, {statistics[8]} off campus ({str(int(statistics[7]) + int(statistics[8]))} total)"),
                    inline=False)
    embed.add_field(name="Tests Administered (to date)", value=(f"{statistics[9]}"), inline=False)
    embed.add_field(name="Campus Quarantine/Isolation Bed Capacity", value=(f"{statistics[10]}% available"), inline=False)

    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def alertlevel(ctx):
    alert_level = get_alert_level()

    embed = discord.Embed(
        title="Current RIT COVID-19 Alert Level",
        description=alert_level[0],
        colour=alert_level[1],
        timestamp=datetime.now()
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
        description=f"Created by Michael Vasile - Version {VERSION}\nUptime: {get_uptime()}\nActive Alert Channels: {len(CHANNELS)}",
    )

    await ctx.send(embed=embed)

# The help command
@client.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(
        title="RIT COVID-19 Tracking Bot",
        description=f"Help Menu\nAll commands are prefixed with '.'",
    )

    embed.add_field(name=".alertlevel", value="Displays the current RIT COVID-19 alert level", inline=False)
    embed.add_field(name=".help", value="Displays this message", inline=False)
    embed.add_field(name=".stats", value="Displays the latest statistics from RIT's COVID-19 Dashboard", inline=False)
    embed.add_field(name=".botinfo", value="Displays bot information, including version number and uptime.",
                    inline=False)

    await ctx.send(embed=embed)

# Checks to see if the alert level changed, will send an alert if it has
@tasks.loop(seconds=120)
async def alert_message():
    # Get the latest alert level
    alert = get_alert_level()

    # Get the last known alert level
    last_known_level = get_last_known()

    # Result boolean for logger
    result = bool(False)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if last_known_level != alert[0]:
        embed = discord.Embed(
            title="RIT COVID-19 Alert Level Changed",
            colour=alert[1],
            timestamp=datetime.now()
        )
        embed.add_field(name="New Alert Level", value=alert[0], inline=False)
        embed.add_field(name="Previous Alert Level", value=last_known_level, inline=False)

        # Log to console
        print(f"[{timestamp}] ALERT LEVEL CHANGED! Current Level: {alert[0]}. Previous: {last_known_level}.\n")

        # Log to file
        with open("alerts.log", "a+") as f:
            f.write(f"[{timestamp}] ALERT LEVEL CHANGED! Current Level: {alert[0]}. Previous: {last_known_level}.\n")

        # Send an alert to all registered Discord channels
        for channel in CHANNELS:
            await channel.send(embed=embed)

        # Update the last known text file
        update_last_known()
    else:
        print(f"[{timestamp}] No updates at this time.")

    with open("logger.log", "a+") as f:
        if result == True:
            f.write(f"[{timestamp}] Checked for updates. Alert level was updated.\n")
        else:
            f.write(f"[{timestamp}] Checked for updates. Alert level was not updated.\n")

@tasks.loop(seconds=300)
async def logger_check():
    # Get the last modified time of the file
    mod_time = os.path.getmtime("logger.log")
    file_age = time.time() - os.path.getmtime("logger.log")

    if file_age > 120:
        embed = discord.Embed(
            title="Logger error",
            description=f"No logger output since {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))}",
            colour=0xffee70,
        )

        # Send to the test server's logger channel
        await CHANNELS[0].send(embed=embed)

@client.event
async def on_ready():
    print("Starting bot...")

    # Load channels into the bot from the KEYS list
    for key in KEYS:
        CHANNELS.append(client.get_channel(key))

    # Send load message for verbosity
    print(f"Loaded {len(CHANNELS)} channels.")

    # Verify that the last known text file is present and not empty
    # Create one if it doesn't exist
    check_last_known()

    # Set status
    await client.change_presence(status=discord.Status.online, activity=discord.Game("RIT COVID Stats | .stats"))

    # Send ready message
    print("Bot is ready.")

    with open("logger.log", "a+") as f:
            f.write(f"** Bot initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} **\n")

    alert_message.start()
    logger_check.start()


# Launch client
client.run(TOKEN)

from dotenv import load_dotenv
import requests
import os
from bs4 import BeautifulSoup
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import time

# Bot version number
VERSION = "1.3.6"

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


def get_alert_level():
    url = 'https://www.rit.edu/ready/dashboard'
    page = requests.get(url, headers={'Cache-Control': 'no-cache'})

    soup = BeautifulSoup(page.content, 'html.parser')
    container = soup.find('div', attrs={'id': 'pandemic-message-container'})

    alert_level = container.find("a").text

    color = 0x000000

    if "Green" in alert_level:
        color = 0x60c10c
    elif "Yellow" in alert_level:
        color = 0xf6be00
    elif "Orange" in alert_level:
        color = 0xf76902
    elif "Red" in alert_level:
        color = 0xda291c

    return alert_level, color


def get_statistics():
    url = 'https://www.rit.edu/ready/dashboard'
    page = requests.get(url, headers={'Cache-Control': 'no-cache'})

    soup = BeautifulSoup(page.content, 'html.parser')
    all_students = str(
        soup.find('div', attrs={'class': 'statistic-12481'}).find_all("p", attrs={'class': 'card-header'})[
            0].text.strip())
    all_staff = str(soup.find('div', attrs={'class': 'statistic-12484'}).find_all("p", attrs={'class': 'card-header'})[
                        0].text.strip())
    new_students = str(
        soup.find('div', attrs={'class': 'statistic-12202'}).find_all("p", attrs={'class': 'card-header'})[
            0].text.strip())
    new_staff = str(soup.find('div', attrs={'class': 'statistic-12205'}).find_all("p", attrs={'class': 'card-header'})[
                        0].text.strip())
    campus_quarantine = str(
        soup.find('div', attrs={'class': 'statistic-12190'}).find_all("p", attrs={'class': 'card-header'})[
            0].text.strip())
    offcampus_quarantine = str(
        soup.find('div', attrs={'class': 'statistic-12193'}).find_all("p", attrs={'class': 'card-header'})[
            0].text.strip())
    campus_isolated = str(
        soup.find('div', attrs={'class': 'statistic-12226'}).find_all("p", attrs={'class': 'card-header'})[
            0].text.strip())
    offcampus_isolated = str(
        soup.find('div', attrs={'class': 'statistic-12229'}).find_all("p", attrs={'class': 'card-header'})[
            0].text.strip())
    isolation_beds = str(
        soup.find('div', attrs={'class': 'statistic-12214'}).find_all("p", attrs={'class': 'card-header'})[
            0].text.strip())
    last_updated = str(soup.find('strong').text)
    new_case_stat = str(soup.find('p', attrs={'class': 'h2'}).text)
    tests_administered = str(
        soup.find('div', attrs={'class': 'statistic-12829'}).find_all("p", attrs={'class': 'card-header'})[
            0].text.strip().replace("*", " "))

    return all_students, all_staff, new_students, new_staff, campus_quarantine, offcampus_quarantine, campus_isolated, \
           offcampus_isolated, isolation_beds, last_updated, new_case_stat, tests_administered

def check_last_known():
    # to anyone looking at this, this is probably not the best way to do this
    # but it's temporary so shhh.

    if os.path.exists("last_known.txt") == False or os.path.getsize("last_known.txt") == 0:

        print("last_known.txt does not exist or is empty. Will create it now...")
        f = open("last_known.txt", "w+")

        # If the file is blank, populate it
        f.write(str(get_alert_level()[0]))
        # Read in the data
        last_known = f.readline()
        # Close the file
        f.close()

    else:
        print("last_known.txt has valid data.")


def get_last_known():
    # Open text file containing the last known alert level
    f = open("last_known.txt", "r")

    # Read first line into the file
    last_known = f.readline()

    # Close file
    f.close()

    # Return the last known alert level as a string
    return last_known


def set_last_known(new_level):
    # Open text file containing the last known alert level for editing
    f = open("last_known.txt", "w+")
    # Write to the file
    f.write(new_level)
    # Close the file
    f.close()


@client.command(pass_context=True)
async def stats(ctx):
    alert_level = get_alert_level()
    statistics = get_statistics()

    embed = discord.Embed(
        title="Latest Statistics from RIT COVID-19 Dashboard",
        description=("Last updated: " + statistics[9]),
        colour=alert_level[1],
        timestamp=datetime.now()
    )

    embed.add_field(name="RIT COVID-19 Alert Level", value=alert_level[0], inline=False)
    embed.add_field(name="All Confirmed Cases",
                    value=(statistics[0] + " student(s), " + statistics[1] + " employee(s)"), inline=False)
    embed.add_field(name=statistics[10], value=(statistics[2] + " student(s), " + statistics[3] + " employee(s)"),
                    inline=False)
    embed.add_field(name="Tests Administered On Campus", value=(statistics[11]), inline=False)
    embed.add_field(name="Students Quarantined", value=(
                statistics[4] + " on campus, " + statistics[5] + " off campus (" + str(
                    int(statistics[4]) + int(statistics[5])) + " total)"),
                    inline=False)
    embed.add_field(name="Students Isolated", value=(
                statistics[6] + " on campus, " + statistics[7] + " off campus (" + str(
                    int(statistics[6]) + int(statistics[7])) + " total)"),
                    inline=False)
    embed.add_field(name="Campus Quarantine/Isolation Bed Capacity", value=(statistics[8] + " available"), inline=False)

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


def get_uptime():
    uptime = timedelta(seconds=(time.time() - startTime))
    days = uptime.days
    hours = uptime.seconds//3600
    minutes = (uptime.seconds//60)%60
    seconds = uptime.seconds

    return "%dd %dh %dm %ds" % (days, hours, minutes, seconds)


@client.command(pass_context=True)
async def botinfo(ctx):
    embed = discord.Embed(
        title="RIT COVID-19 Tracking Bot",
        description=f"Created by Michael Vasile - Version {VERSION}\nUptime: {get_uptime()}\nActive Alert Channels: {len(CHANNELS)}",
    )

    await ctx.send(embed=embed)


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


@tasks.loop(seconds=120)
async def alert_message():
    # Log file
    log = open("alerts.log", "a+")

    alert = get_alert_level()

    last_known_level = get_last_known()

    if last_known_level != alert[0]:
        embed = discord.Embed(
            title="RIT COVID-19 Alert Level Changed",
            colour=alert[1],
            timestamp=datetime.now()
        )
        embed.add_field(name="New Alert Level", value=alert[0], inline=False)
        embed.add_field(name="Previous Alert Level", value=last_known_level, inline=False)

        # Log to console
        print(f"[{datetime.now()}] ALERT LEVEL CHANGED! Current Level: {alert[0]} (was: {last_known_level})")

        # Log to file
        log.write(f"[{datetime.now()}] ALERT LEVEL CHANGED! Current Level: {alert[0]} (was: {last_known_level})")

        # Close log
        log.close()

        if last_known_level == "test":
            await CHANNELS[0].send(embed=embed)
        else:
            for channel in CHANNELS:
                await channel.send(embed=embed)

        set_last_known(alert[0])
    else:
        print(f"[{datetime.now()}] No updates at this time.")


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
    await client.change_presence(status=discord.Status.online, activity=discord.Game("COVID Stats | .stats"))

    # Send ready message
    print("Bot is ready.")

    alert_message.start()


# Launch client
client.run(TOKEN)

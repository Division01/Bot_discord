import discord
from discord.ext import tasks, commands
from datetime import datetime
import os
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_DATE = datetime(2024, 6, 12, 12, 0)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

def compute_days_left(time_difference):
    return time_difference.days +1

def countdown_to_date():
    now = datetime.now()
    time_difference = TARGET_DATE - now
    days = compute_days_left(time_difference=time_difference)
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"Days left: {days} before temporis."
    elif days == 0:
        return f"Hours left: {hours}, Minutes left: {minutes}"
    else:
        return "The target date has passed, bot is now useless."

@tasks.loop(hours=1)
async def countdown_task():
    now = datetime.now()
    days_left = compute_days_left(time_difference=(TARGET_DATE - now))
    print(now)
    print(days_left)
    if now.hour == 15 and days_left != 0:  # Adjust the hour as needed to set the time for the daily message
        print("It's decompte time")
        message = countdown_to_date()
        for guild in bot.guilds:
            print(f"It's decompte time : {message}")
            for channel in guild.text_channels:
                print(f"Canal : {channel}")
                if channel.permissions_for(guild.me).send_messages:
                    print("Permission had !")
                    await channel.send(message)
                    print("Message sent !")
                    break

    if days_left == 0:
        message = countdown_to_date()
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(message)
                    break

@countdown_task.before_loop
async def before():
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    countdown_task.start()  # Start the countdown task once the bot is ready

# Start the bot
bot.run(TOKEN)

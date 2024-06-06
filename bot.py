import discord
from discord.ext import tasks, commands
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI


### Load tokens from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_DATE = datetime(2024, 6, 12, 12, 0)

### Load the libraries classes
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

def compute_days_left(time_difference):
    """
    Needed the same way to compute days in both coutdown_to_date
    and countdown_task. Might be uneeded when the +1 is corrected.


    Args:
        time_difference (datetime): TARGET_DATE - now

    Returns:
        days_left: The correct number of days left
    """
    return time_difference.days + 1

def countdown_to_date():
    """
    Generates a message of the countdown. It adapts for the last
    24 hours to make an hourly countdown message.

    Returns:
        countdown_message(string): Countdown message.
    """
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


def generate_image(days_left):
    import requests
    import base64

    # Define the URL and the payload to send.
    url = "http://127.0.0.1:7860"

    payload = {
        "prompt": f"{days_left} crusader knights, flag with 'Deus Vult' on it",
        "steps": 50
    }

    # Send said payload to said URL through the API.
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()

    # Decode and save the image.
    with open(f"images/output{days_left}.png", 'wb') as f:
        f.write(base64.b64decode(r['images'][0]))




@tasks.loop(hours=1)
async def countdown_task():
    """
    Main task of the bot. It check how many days are left 
    and generate a countdown message, an associated image 
    and then post it in the first channel available to him.
    """

    now = datetime.now()
    days_left = compute_days_left(time_difference=(TARGET_DATE - now))
    print(now)
    print(days_left)
    if now.hour == 14 and days_left != 0:  # Adjust the hour as needed to set the time for the daily message
        print("It's decompte time")
        message = countdown_to_date()
        generate_image(days_left)
        for guild in bot.guilds:
            print(f"It's decompte time : {message}")
            for channel in guild.text_channels:
                print(f"Canal : {channel}")
                if channel.permissions_for(guild.me).send_messages:
                    print("Permission had !")
                    await channel.send(message)
                    await channel.send(file=discord.File(f'images/output{days_left}.png', f'image{days_left}.png'))
                    print("Message and image sent!")
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
    """
    Function that makes the bot wait for the hourly loop
    before running the task.
    """
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    """
    Necessary on_ready function to know when we can start
    giving instructions to the discord bot.
    """
    print(f'Logged in as {bot.user}')
    countdown_task.start()  # Start the countdown task once the bot is ready

### Start the bot
bot.run(DISCORD_TOKEN)

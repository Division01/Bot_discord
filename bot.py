import discord
from discord.ext import tasks, commands
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from openai import OpenAI
import asyncio

### Load tokens from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_DATE = datetime(2024, 6, 12, 14, 0)
TARGET_HOUR = 13

### Load the libraries classes
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

def compute_time_difference():
    now = datetime.now()
    time_difference=TARGET_DATE - now
    return time_difference

def countdown_to_date():
    """
    Generates a message of the countdown. It adapts for the last
    24 hours to make an hourly countdown message.

    Returns:
        countdown_message(string): Countdown message.
    """
    time_difference = compute_time_difference()
    days = time_difference.days
    print(time_difference.seconds)
    hours, remainder = divmod(time_difference.seconds, 3600)

    if days > 0:
        return f"Days left before temporis: {days}"
    elif days == 0 and hours > 0:
        return f"Hours left before temporis: {hours}"
    elif days == 0 and hours == 0:
        return "It's go time !"
    else:
        return "The target date has passed, bot is now useless."


def generate_image(days_left):
    import requests
    import base64

    # Define the URL and the payload to send.
    url = "http://127.0.0.1:7860"

    payload = {
        "prompt": f"""{days_left} crusader knights, they are holding a flag with 'Deus Vult' on it. 
        The image has to look like an old painting of templars. Templars are knights in armor with a white cloath and a red cross on it. 
        The painting looks quite realistic.""",
        "steps": 100
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
    time_difference=compute_time_difference()
    days_left = time_difference.days
    print(days_left)
    if now.hour == TARGET_HOUR and days_left != 0:  # Adjust the hour as needed to set the time for the daily message
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

    if days_left == 0 :
        message = countdown_to_date()
        generate_image(days_left)
        for guild in bot.guilds:
            print(f"In {guild} decompte time : {message}")
            for channel in guild.text_channels:
                print(f"Canal : {channel}")
                if channel.permissions_for(guild.me).send_messages:
                    print("Permission had !")
                    await channel.send(message)
                    await channel.send(file=discord.File(f'images/output{days_left}.png', f'image{days_left}.png'))
                    print("Message and image sent!")
                    break

@countdown_task.before_loop
async def before():
    await bot.wait_until_ready()
    now = datetime.now()
    seconds_until_next_hour = (60 - now.minute) * 60 - now.second - 15
    print(f"Waiting {60 - now.minute} minutes and {now.second} seconds before running the bot.")
    await asyncio.sleep(seconds_until_next_hour)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    countdown_task.start()  # Start the countdown task once the bot is ready

### Start the bot
bot.run(DISCORD_TOKEN)

import discord
from discord.ext import tasks, commands
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI


# Load tokens from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TARGET_DATE = datetime(2024, 6, 12, 12, 0)
IMAGE_THEME = " Deus Vult "


client = OpenAI(api_key=OPENAI_API_KEY)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

def compute_days_left(time_difference):
    return time_difference.days + 1

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

def generate_image(days_left):
    text = f"Related to {IMAGE_THEME} and the fact that there is {days_left}. It can be a meme."
    response = client.images.generate(prompt=text,
    n=1,
    size="1024x1024")
    image_url = response.data[0].url
    return image_url

@tasks.loop(hours=1)
async def countdown_task():
    now = datetime.now()
    days_left = compute_days_left(time_difference=(TARGET_DATE - now))
    print(now)
    print(days_left)
    message = countdown_to_date()
    image_url = generate_image(days_left)
    if now.hour == 15 and days_left != 0:  # Adjust the hour as needed to set the time for the daily message
        print("It's decompte time")
        message = countdown_to_date()
        image_url = generate_image(days_left)
        for guild in bot.guilds:
            print(f"It's decompte time : {message}")
            for channel in guild.text_channels:
                print(f"Canal : {channel}")
                if channel.permissions_for(guild.me).send_messages:
                    print("Permission had !")
                    await channel.send(message)
                    await channel.send(image_url)
                    print("Message and image sent!")
                    break

    if days_left == 0:
        message = countdown_to_date()
        image_url = generate_image(message)
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(message)
                    await channel.send(image_url)
                    break

@countdown_task.before_loop
async def before():
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    countdown_task.start()  # Start the countdown task once the bot is ready

# Start the bot
bot.run(DISCORD_TOKEN)

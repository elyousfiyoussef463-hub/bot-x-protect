import sys
import os
import json
import asyncio
import traceback
import logging
import aiohttp
from itertools import cycle

try:
    import discord
except ImportError:
    print("Le package discord.py n'est pas installé. Exécutez 'pip install discord.py' puis relancez.")
    sys.exit(1)

from discord.ext import commands

from Tools.utils import getGuildPrefix, getConfig
from Tools.translate import Translate
from Tools.style import BRAND_NAME, VERSION, COLORS

# ------------------------ INTENTS ------------------------ #

intents = discord.Intents.default()
intents.members = True

try:
    intents.message_content = True
except AttributeError:
    pass

# ------------------------ BOT ------------------------ #

bot = commands.Bot(
    command_prefix=getGuildPrefix,
    intents=intents,
)

bot.remove_command("help")
bot.translate = Translate()

# ------------------------ ANTI-CRASH ------------------------ #

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("crash.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("shinjuku")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Unhandled error in '{event}':\n{traceback.format_exc()}")

status_task = None

@bot.event
async def on_disconnect():
    global status_task
    logger.warning("Bot disconnected from Discord Gateway (auto-reconnect in progress)")
    if status_task:
        status_task.cancel()
        status_task = None

@bot.event
async def on_connect():
    global status_task
    if status_task is None or status_task.done():
        status_task = bot.loop.create_task(update_status())

# ------------------------ EVENTS ------------------------ #

async def update_status():
    status_cycle = cycle([
        lambda: "/empire-x",
        lambda: "[+] EMPIRE-X | PROTECT",
        lambda: f"{sum(g.member_count for g in bot.guilds)} membres",
    ])

    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            current_status = next(status_cycle)()
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=current_status,
                )
            )
        except asyncio.CancelledError:
            break
        except (discord.errors.ConnectionClosed, aiohttp.ClientConnectionResetError, ConnectionResetError):
            break
        except Exception:
            logger.error(f"Status update error:\n{traceback.format_exc()}")
        await asyncio.sleep(20)

@bot.event
async def on_ready():
    global status_task
    print(f"  Connected as: {bot.user}")
    print(f"  Discord.py:   {discord.__version__}")
    print(f"  Servers:      {len(bot.guilds)}")
    print(f"  Users:        {sum(g.member_count for g in bot.guilds)}")
    print("─" * 45)

    if status_task is None or status_task.done():
        status_task = bot.loop.create_task(update_status())

# ------------------------ LOAD .ENV ------------------------ #

def load_token():
    token = os.environ.get("BOT_TOKEN")
    if token:
        return token

    try:
        from dotenv import load_dotenv
        load_dotenv()
        token = os.environ.get("BOT_TOKEN")
        if token:
            return token
    except ImportError:
        pass

    return None

# ------------------------ RUN ------------------------ #

async def main():
    banner = f"""
    ╔══════════════════════════════════════════╗
    ║           {BRAND_NAME} v{VERSION}           ║
    ║        Discord Protection System          ║
    ╚══════════════════════════════════════════╝
    """
    print(banner)
    for filename in os.listdir("Cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"Cogs.{filename[:-3]}")
                print(f"  [+] Loaded: {filename}")
            except Exception as e:
                print(f"  [-] Error in {filename}: {e}")
    print("─" * 45)

    token = load_token()
    if not token:
        print("  No token found. Create a .env file with BOT_TOKEN=your_token or set the BOT_TOKEN environment variable.")
        print("  Example .env file:")
        print("    BOT_TOKEN=MTX...")
        return

    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Fatal error: {e}\n{traceback.format_exc()}")
        print("  Bot crashed. Check crash.log for details.")

if __name__ == "__main__":
    asyncio.run(main())

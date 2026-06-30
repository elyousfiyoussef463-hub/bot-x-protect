import sys, os, json, asyncio, discord
from discord.ext import commands

sys.path.insert(0, os.path.dirname(__file__))
from Tools.utils import getConfig, updateConfig
from Tools.style import BRAND_NAME, VERSION

GUILD_ID = 1512994707603718165

async def fix():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        from dotenv import load_dotenv
        load_dotenv()
        token = os.environ.get("BOT_TOKEN")

    if not token:
        print("Token not found.")
        return

    intents = discord.Intents.default()
    intents.guilds = True
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Connected as {bot.user}")
        guild = bot.get_guild(GUILD_ID)
        if not guild:
            print(f"Server {GUILD_ID} not found.")
            await bot.close()
            return

        print(f"Fixing permissions for: {guild.name}")

        for channel in guild.channels:
            try:
                overwrites = channel.overwrites_for(guild.default_role)
                overwrites.read_messages = None
                overwrites.read_message_history = None
                overwrites.view_channel = None
                overwrites.send_messages = None
                overwrites.connect = None
                overwrites.speak = None
                await channel.set_permissions(guild.default_role, overwrite=overwrites)
                print(f"  Reset @everyone: #{channel.name}")
            except Exception as e:
                print(f"  Failed #{channel.name}: {e}")

        print("Done! All channels fixed.")
        await bot.close()

    try:
        await bot.start(token)
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(fix())

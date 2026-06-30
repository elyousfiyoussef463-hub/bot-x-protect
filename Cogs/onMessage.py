import discord
import json
import aiohttp
from discord.ext import commands
from datetime import datetime, timezone
from collections import defaultdict, deque
try:
    from nude import Nude
    NUDE_AVAILABLE = True
except ImportError:
    NUDE_AVAILABLE = False
from io import BytesIO
try:
    from profanity_check import predict
    PROFANITY_AVAILABLE = True
except ImportError:
    PROFANITY_AVAILABLE = False
from Tools.utils import getConfig
from Tools.logMessage import sendLogMessage
from Tools.style import branded_embed, COLORS, user_info_field


class OnMessageCog(commands.Cog, name="on message"):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = defaultdict(lambda: deque(maxlen=30))

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return

        if not isinstance(message.author, discord.Member):
            return

        is_bot = message.author.bot
        author = message.author

        if not message.content and len(message.attachments) == 0:
            return

        channel_is_nsfw = getattr(message.channel, "nsfw", False)

        if not channel_is_nsfw and message.attachments and NUDE_AVAILABLE:
            for i in message.attachments:
                if i.filename.endswith((".png", ".jpg", ".jpeg", ".gif")):
                    data = getConfig(message.guild.id)
                    if data.get("antiNudity"):
                        logChannel = data["logChannel"]
                        async with aiohttp.ClientSession() as session:
                            async with session.get(i.url) as response:
                                image_bytes = await response.read()
                        image_bytes = BytesIO(image_bytes)
                        n = Nude(image_bytes)
                        n.parse()
                        if n.result:
                            i.filename = f"SPOILER_{i.filename}"
                            spoiler = await i.to_file()
                            embed = branded_embed(
                                title=self.bot.translate.msg(message.guild.id, "onMessage", "USER_HAS_SENT_NUDITY").format(message.author),
                                description=self.bot.translate.msg(message.guild.id, "onMessage", "USER_HAS_SENT_NUDITY_DESCRIPTION").format(
                                    message.channel.mention, message.author, message.author.id
                                ),
                                color="error",
                            )
                            await sendLogMessage(self, event=message, channel=logChannel, embed=embed, messageFile=spoiler)
                            await message.delete()
                            embed = branded_embed(
                                description=self.bot.translate.msg(message.guild.id, "onMessage", "DO_NOT_SEND_NUDITY").format(message.author.mention),
                                color="error",
                            )
                            await message.channel.send(embed=embed)

        data = getConfig(message.guild.id)
        antiProfanity = data.get("antiProfanity", True)
        antiSpam = data.get("antiSpam", True)
        allowSpam = data.get("allowSpam", [])
        logChannel = data.get("logChannel", 1)
        if is_bot:
            spamWarn = 999
            spamKick = 2
            spamWindow = 10
        else:
            spamWarn = data.get("spamWarnCount", 5)
            spamKick = data.get("spamKickCount", 8)
            spamWindow = data.get("spamWindow", 10)

        if antiProfanity and PROFANITY_AVAILABLE:
            profanity = predict([message.content])
            if profanity[0] == 1:
                await message.delete()
                embed = branded_embed(
                    description=self.bot.translate.msg(message.guild.id, "onMessage", "DO_NOT_INSULT").format(message.author.mention),
                    color="error",
                )
                await message.channel.send(embed=embed)
                content = message.content[:1600]
                embed = branded_embed(
                    title=self.bot.translate.msg(message.guild.id, "onMessage", "USER_HAS_SENT_PROFANITY").format(message.author),
                    description=self.bot.translate.msg(message.guild.id, "onMessage", "USER_HAS_SENT_PROFANITY_DESCRIPTION").format(
                        message.channel.mention, message.author, message.author.id, content
                    ),
                    color="error",
                )
                await sendLogMessage(self, event=message, channel=logChannel, embed=embed)

        if antiSpam:
            if message.channel.id in allowSpam:
                return
            if not is_bot and (author.guild_permissions.kick_members or author.guild_permissions.ban_members or author.guild_permissions.manage_messages):
                return

            now = datetime.now(timezone.utc)
            cache = self.message_cache[author.id]
            cache.append((now, message))

            while cache and (now - cache[0][0]).total_seconds() > spamWindow:
                cache.popleft()

            recent_count = len(cache)

            if recent_count >= spamKick:
                try:
                    await author.kick(reason="Spamming - Auto-kicked by anti-spam")
                except Exception as e:
                    print(f"Anti-spam kick failed: {e}")
                    return

                embed = branded_embed(
                    description=self.bot.translate.msg(message.guild.id, "onMessage", "USER_HAS_BEEN_KICKED_FOR_SPAMMING").format(author.mention),
                    color="error",
                )
                await message.channel.send(embed=embed)

                logTime = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
                logs = f"[LOGS] [+] EMPIRE-X | PROTECT - ANTI-SPAM\n\n{author} ({author.id}) spammed in \"{message.channel}\" the {logTime}\n\n"
                for i, (_, m) in enumerate(list(cache)[-10:], 1):
                    logs = f"{logs}\n[{i}] {m.content}"

                url = "https://hastebin.com"
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(f"{url}/documents", data=logs) as resp:
                            hastebin_data = await resp.json()
                            hastbinUrl = url + "/" + hastebin_data["key"]
                except Exception:
                    hastbinUrl = "Hastebin unavailable"

                embed = branded_embed(
                    title=self.bot.translate.msg(message.guild.id, "onMessage", "MEMBER_HAS_BEEN_KICKED").format(author),
                    description=self.bot.translate.msg(message.guild.id, "onMessage", "USER_HAS_BEEN_KICKED_FOR_SPAMMING_LOG").format(
                        message.channel.mention, author, author.id, hastbinUrl
                    ),
                    color="error",
                )
                await sendLogMessage(self, event=message, channel=logChannel, embed=embed)

            elif recent_count >= spamWarn:
                embed = branded_embed(
                    description=self.bot.translate.msg(message.guild.id, "onMessage", "STOP_SPAM").format(author.mention),
                    color="warning",
                )
                await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(OnMessageCog(bot))

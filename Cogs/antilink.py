import re
import discord
from discord.ext import commands
from Tools.style import branded_embed

INVITE_REGEX = re.compile(
    r"(https?://)?(www\.)?(discord\.gg|discord\.com/invite)/[A-Za-z0-9]+",
    re.IGNORECASE,
)

LINK_REGEX = re.compile(
    r"https?://\S+|www\.\S+",
    re.IGNORECASE,
)


class AntiLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.guild:
            return

        if not isinstance(message.author, discord.Member):
            return

        if message.author.guild_permissions.administrator:
            return

        if message.author.guild_permissions.manage_messages or message.author.guild_permissions.kick_members:
            return

        from Tools.utils import getConfig
        config = getConfig(message.guild.id)
        link_whitelist = config.get("allowSpam", [])
        if message.channel.id in link_whitelist:
            return

        if INVITE_REGEX.search(message.content):
            try:
                await message.delete()
            except (discord.Forbidden, discord.HTTPException):
                pass

            embed = branded_embed(
                description=self.bot.translate.msg(message.guild.id, "antilink", "NO_DISCORD_INVITES").format(
                    message.author.mention
                ),
                color="error",
            )
            await message.channel.send(embed=embed, delete_after=5)
            return

        if LINK_REGEX.search(message.content):
            try:
                await message.delete()
            except (discord.Forbidden, discord.HTTPException):
                pass

            embed = branded_embed(
                description=self.bot.translate.msg(message.guild.id, "antilink", "NO_LINKS").format(
                    message.author.mention
                ),
                color="error",
            )
            await message.channel.send(embed=embed, delete_after=5)


async def setup(bot):
    await bot.add_cog(AntiLink(bot))

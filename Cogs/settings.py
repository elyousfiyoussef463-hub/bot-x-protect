import discord
from Tools.utils import getConfig, getGuildPrefix
from Tools.style import branded_embed, format_bool, BRAND_NAME, VERSION
from discord.ext import commands

class SettingsCog(commands.Cog, name="settings command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="settings",
        description="Display the server settings.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def settings(self, ctx):
        data = getConfig(ctx.guild.id)
        prefix = await getGuildPrefix(self.bot, ctx)

        captcha = data["captcha"]
        captchaChannel = data["captchaChannel"]
        logChannel = data["logChannel"]
        temporaryRole = data["temporaryRole"]
        roleGivenAfterCaptcha = data["roleGivenAfterCaptcha"]
        minAccountAge = data["minAccountDate"]
        antispam = data["antiSpam"]
        allowSpam = data["allowSpam"]
        antiNudity = data["antiNudity"]
        antiProfanity = data["antiProfanity"]
        language = data["language"]

        if minAccountAge is not False:
            minAccountAge = f"{int(minAccountAge / 3600)} hours"
        else:
            minAccountAge = "Disabled"

        allowSpamStr = ", ".join(f"<#{x}>" for x in allowSpam) if allowSpam else "None"
        roleStr = f"<@&{roleGivenAfterCaptcha}>" if roleGivenAfterCaptcha else "None"
        captchaStr = f"<#{captchaChannel}>" if captchaChannel else "None"
        logStr = f"<#{logChannel}>" if logChannel is not False and logChannel != 1 else "None"

        embed = branded_embed(
            title=f"Server Settings — {ctx.guild.name}",
            color="primary",
        )
        embed.add_field(
            name="Captcha Protection",
            value=(
                f"**Status:** {format_bool(captcha)}\n"
                f"**Channel:** {captchaStr}\n"
                f"**Logs:** {logStr}\n"
                f"**Temp Role:** <@&{temporaryRole}>"
            ),
            inline=False,
        )
        embed.add_field(
            name="Post-Captcha Role",
            value=f"**Role:** {roleStr}",
            inline=True,
        )
        embed.add_field(
            name="Minimum Account Age",
            value=f"**Age:** {minAccountAge}",
            inline=True,
        )
        embed.add_field(
            name="Anti-Spam",
            value=f"**Status:** {format_bool(antispam)}",
            inline=True,
        )
        embed.add_field(
            name="Spam Exemptions",
            value=f"**Channels:** {allowSpamStr}",
            inline=True,
        )
        embed.add_field(
            name="Anti-Nudity",
            value=f"**Status:** {format_bool(antiNudity)}",
            inline=True,
        )
        embed.add_field(
            name="Anti-Profanity",
            value=f"**Status:** {format_bool(antiProfanity)}",
            inline=True,
        )
        embed.add_field(
            name="Language",
            value=f"`{language}`",
            inline=True,
        )
        embed.add_field(
            name="Bot Protection",
            value=f"**Status:** {format_bool(data.get('botProtection', False))}",
            inline=True,
        )
        embed.add_field(
            name="Staff Protection",
            value=f"**Status:** {format_bool(data.get('staffProtection', False))}",
            inline=True,
        )
        protected_count = len(data.get("protectedChannels", []))
        embed.add_field(
            name="Protected Channels",
            value=f"**Count:** {protected_count}",
            inline=True,
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(SettingsCog(bot))

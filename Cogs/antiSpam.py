import discord
from discord.ext import commands
from Tools.utils import getConfig, updateConfig
from Tools.style import branded_embed, COLORS

class AntiSpamCog(commands.Cog, name="change setting from anti spam command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="antispam",
        usage="<true/false>",
        description="Enable or disable the spam protection.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def antispam(self, ctx, antiSpam):
        antiSpam = antiSpam.lower()

        if antiSpam == "true":
            data = getConfig(ctx.guild.id)
            data["antiSpam"] = True
            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "antiSpam", "ANTI_SPAM_ENABLED"),
                description=self.bot.translate.msg(ctx.guild.id, "antiSpam", "ANTI_SPAM_ENABLED_DESCRIPTION"),
                color="success",
            )
        else:
            data = getConfig(ctx.guild.id)
            data["antiSpam"] = False
            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "antiSpam", "ANTI_SPAM_DISABLED"),
                description=self.bot.translate.msg(ctx.guild.id, "antiSpam", "ANTI_SPAM_DISABLED_DESCRIPTION"),
                color="error",
            )

        await ctx.send(embed=embed)
        updateConfig(ctx.guild.id, data)


async def setup(bot):
    await bot.add_cog(AntiSpamCog(bot))

import discord
from discord.ext import commands
from Tools.utils import getConfig, updateConfig
from Tools.style import branded_embed, COLORS

class AntiProfanityCog(commands.Cog, name="change setting from anti profanity command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="antiprofanity",
        aliases=["profanity"],
        usage="<true/false>",
        description="Enable or disable the anti profanity.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def antiprofanity(self, ctx, antiProfanity):
        antiProfanity = antiProfanity.lower()

        if antiProfanity == "true":
            data = getConfig(ctx.guild.id)
            data["antiProfanity"] = True
            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "profanity", "ANTI_PROFANITY_ENABLED"),
                description=self.bot.translate.msg(ctx.guild.id, "profanity", "ANTI_PROFANITY_ENABLED_DESCRIPTION"),
                color="success",
            )
        else:
            data = getConfig(ctx.guild.id)
            data["antiProfanity"] = False
            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "profanity", "ANTI_PROFANITY_DISABLED"),
                description=self.bot.translate.msg(ctx.guild.id, "profanity", "ANTI_PROFANITY_DISABLED_DESCRIPTION"),
                color="error",
            )

        await ctx.send(embed=embed)
        updateConfig(ctx.guild.id, data)


async def setup(bot):
    await bot.add_cog(AntiProfanityCog(bot))

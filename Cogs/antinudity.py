import discord
from discord.ext import commands
from Tools.utils import getConfig, updateConfig
from Tools.style import branded_embed, COLORS

class AntiNudityCog(commands.Cog, name="change setting from anti nudity command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="antinudity",
        aliases=["nudity", "porn"],
        usage="<true/false>",
        description="Enable or disable the nudity image protection.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def antinudity(self, ctx, antiNudity):
        antiNudity = antiNudity.lower()

        if antiNudity == "true":
            data = getConfig(ctx.guild.id)
            data["antiNudity"] = True
            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "antinudity", "ANTI_NUDITY_ENABLED"),
                description=self.bot.translate.msg(ctx.guild.id, "antinudity", "ANTI_NUDITY_ENABLED_DESCRIPTION"),
                color="success",
            )
        else:
            data = getConfig(ctx.guild.id)
            data["antiNudity"] = False
            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "antinudity", "ANTI_NUDITY_DISABLED"),
                description=self.bot.translate.msg(ctx.guild.id, "antinudity", "ANTI_NUDITY_DISABLED_DESCRIPTION"),
                color="error",
            )

        await ctx.send(embed=embed)
        updateConfig(ctx.guild.id, data)


async def setup(bot):
    await bot.add_cog(AntiNudityCog(bot))

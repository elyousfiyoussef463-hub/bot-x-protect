import discord
from discord.ext import commands
from Tools.utils import getConfig, updateConfig
from Tools.style import branded_embed

class ChangePrefixCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="changeprefix",
        aliases=["prefix"],
        usage="<newPrefix>",
        description="Change the bot's prefix.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def changeprefix(self, ctx, prefix):
        data = getConfig(ctx.guild.id)
        data["prefix"] = prefix
        updateConfig(ctx.guild.id, data)

        embed = branded_embed(
            description=self.bot.translate.msg(ctx.guild.id, "changeprefix", "NEW_PREFIX").format(prefix),
            color="success",
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ChangePrefixCog(bot))

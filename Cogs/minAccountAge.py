from Tools.utils import getConfig, updateConfig, getGuildPrefix
from Tools.style import branded_embed, COLORS
from discord.ext import commands

class MinAccountAgeCog(commands.Cog, name="change min account age command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="minaccountage",
        aliases=["minage", "agerequired", "age"],
        usage="<numberInSecond/false>",
        description="Update or disable the minimal account age to join the server.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def minaccountage(self, ctx, accountAge):
        accountAge = accountAge.lower()

        if accountAge == "false":
            data = getConfig(ctx.guild.id)
            data["minAccountDate"] = False
            updateConfig(ctx.guild.id, data)

            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "minAccountAge", "MINIMUM_ACCOUNT_AGE_DISABLED"),
                description=self.bot.translate.msg(ctx.guild.id, "minAccountAge", "MINIMUM_ACCOUNT_AGE_DISABLED_DESCRIPTION"),
                color="success",
            )
            await ctx.send(embed=embed)
        else:
            try:
                accountAge = int(accountAge) * 3600

                data = getConfig(ctx.guild.id)
                data["minAccountDate"] = accountAge
                updateConfig(ctx.guild.id, data)

                embed = branded_embed(
                    title=self.bot.translate.msg(ctx.guild.id, "minAccountAge", "MINIMUM_ACCOUNT_AGE_ENABLED"),
                    description=self.bot.translate.msg(ctx.guild.id, "minAccountAge", "MINIMUM_ACCOUNT_AGE_ENABLED_DESCRIPTION"),
                    color="success",
                )
                await ctx.send(embed=embed)

            except (ValueError, TypeError):
                prefix = await getGuildPrefix(self.bot, ctx.message)
                embed = branded_embed(
                    description=self.bot.translate.msg(ctx.guild.id, "minAccountAge", "INVALID_ARGUMENT").format(prefix),
                    color="error",
                )
                return await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(MinAccountAgeCog(bot))

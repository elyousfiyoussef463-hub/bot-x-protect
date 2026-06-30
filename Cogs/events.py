from discord.ext import commands
from discord.ext.commands import MissingPermissions, CommandNotFound, BotMissingPermissions, MissingRequiredArgument
from Tools.utils import getGuildPrefix
from Tools.style import branded_embed, COLORS

class EventsCog(commands.Cog, name="EventsCog"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            retry = error.retry_after
            day = int(retry / 86400)
            hour = int(retry / 3600)
            minute = int(retry / 60)
            if day > 0:
                msg = f"Please wait {day} day(s) before trying again."
            elif hour > 0:
                msg = f"Please wait {hour} hour(s) before trying again."
            elif minute > 0:
                msg = f"Please wait {minute} minute(s) before trying again."
            else:
                msg = f"Please wait {round(retry)} second(s) before trying again."
            embed = branded_embed(description=msg, color="warning")
            await ctx.send(embed=embed)
        elif isinstance(error, BotMissingPermissions):
            missing = ", ".join(error.missing)
            embed = branded_embed(
                description=f"{ctx.author.mention} I need `{missing}` permission(s) to run this command.",
                color="error",
            )
            await ctx.send(embed=embed)
        elif isinstance(error, MissingPermissions):
            missing = ", ".join(error.missing)
            embed = branded_embed(
                description=f"{ctx.author.mention} You need `{missing}` permission(s) to run this command.",
                color="error",
            )
            await ctx.send(embed=embed)
        elif isinstance(error, MissingRequiredArgument):
            prefix = await getGuildPrefix(self.bot, ctx)
            embed = branded_embed(
                description=f"{ctx.author.mention} Missing required argument.\nUsage: `{prefix}{ctx.command.name} {ctx.command.usage}`",
                color="error",
            )
            await ctx.send(embed=embed)
        else:
            embed = branded_embed(
                description=f"An error occurred: {error}",
                color="error",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(EventsCog(bot))

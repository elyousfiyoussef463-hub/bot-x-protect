import discord
from discord.ext import commands
from Tools.utils import getConfig, updateConfig
from Tools.style import branded_embed, COLORS

class LogsCog(commands.Cog, name="change setting from logs command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="logs",
        aliases=["log", "setlog", "setlogs", "logchannel"],
        usage="<true/false>",
        description="Enable or disable the log system.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def logs(self, ctx, option):
        option = option.lower()

        if option == "true":
            log_channel = await ctx.guild.create_text_channel(f"{self.bot.user.name}-logs")
            perms = log_channel.overwrites_for(ctx.guild.default_role)
            perms.read_messages = False
            await log_channel.set_permissions(ctx.guild.default_role, overwrite=perms)

            data = getConfig(ctx.guild.id)
            data["logChannel"] = log_channel.id

            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "logs", "LOG_CHANNEL_ENABLED"),
                description=self.bot.translate.msg(ctx.guild.id, "logs", "LOG_CHANNEL_ENABLED_DESCRIPTION"),
                color="success",
            )
        else:
            data = getConfig(ctx.guild.id)
            log_channel = self.bot.get_channel(data["logChannel"])
            if log_channel:
                await log_channel.delete()
            data["logChannel"] = False

            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "logs", "LOG_CHANNEL_DISABLED"),
                description=self.bot.translate.msg(ctx.guild.id, "logs", "LOG_CHANNEL_DISABLED_DESCRIPTION"),
                color="error",
            )

        await ctx.send(embed=embed)
        updateConfig(ctx.guild.id, data)


async def setup(bot):
    await bot.add_cog(LogsCog(bot))

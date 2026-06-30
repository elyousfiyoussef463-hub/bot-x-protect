import discord
import re
from Tools.utils import getConfig, updateConfig, getGuildPrefix
from Tools.style import branded_embed, COLORS
from discord.ext import commands

class AllowSpamCog(commands.Cog, name="allow spam command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="allowspam",
        aliases=["spam"],
        usage="<#channel/ID> (False)",
        description="Enable or disable the spam protection in a specific channel.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def allowspam(self, ctx, channel, remove=""):
        channel_id = re.findall(r"\d+", str(channel))
        if not channel_id:
            embed = branded_embed(
                description=self.bot.translate.msg(ctx.guild.id, "allowSpam", "INVALID_CHANNEL_ENABLE").format(await getGuildPrefix(self.bot, ctx)),
                color="error",
            )
            await ctx.send(embed=embed)
            return
        channel = channel_id[0]
        remove = remove.lower()
        prefix = await getGuildPrefix(self.bot, ctx)

        if remove != "false":
            try:
                channel = int(channel)
                spamChannel = self.bot.get_channel(channel)
                data = getConfig(ctx.guild.id)

                if spamChannel.id in data["allowSpam"]:
                    embed = branded_embed(
                        description=self.bot.translate.msg(ctx.guild.id, "allowSpam", "CHANNEL_ALREADY_IGNORED_BY_ANTI_SPAM"),
                        color="warning",
                    )
                    return await ctx.send(embed=embed)

                data["allowSpam"].append(spamChannel.id)
                updateConfig(ctx.guild.id, data)
                embed = branded_embed(
                    title=self.bot.translate.msg(ctx.guild.id, "global", "SUCCESS"),
                    description=self.bot.translate.msg(ctx.guild.id, "allowSpam", "CHANNEL_IGNORED_BY_ANTI_SPAM").format(spamChannel.id),
                    color="success",
                )
                await ctx.send(embed=embed)
            except Exception:
                embed = branded_embed(
                    description=self.bot.translate.msg(ctx.guild.id, "allowSpam", "INVALID_CHANNEL_ENABLE").format(prefix),
                    color="error",
                )
                return await ctx.send(embed=embed)
        else:
            try:
                channel = int(channel)
                spamChannel = self.bot.get_channel(channel)
                data = getConfig(ctx.guild.id)

                if spamChannel.id not in data["allowSpam"]:
                    embed = branded_embed(
                        description=self.bot.translate.msg(ctx.guild.id, "allowSpam", "ANTI_SPAM_ALREADY_DISABLED"),
                        color="warning",
                    )
                    return await ctx.send(embed=embed)

                data["allowSpam"].remove(spamChannel.id)
                updateConfig(ctx.guild.id, data)
                embed = branded_embed(
                    title=self.bot.translate.msg(ctx.guild.id, "global", "SUCCESS"),
                    description=self.bot.translate.msg(ctx.guild.id, "allowSpam", "CHANNEL_NOT_IGNORED_BY_ANTI_SPAM").format(spamChannel.id),
                    color="success",
                )
                await ctx.send(embed=embed)
            except Exception:
                embed = branded_embed(
                    description=self.bot.translate.msg(ctx.guild.id, "allowSpam", "INVALID_CHANNEL_DISABLE").format(prefix),
                    color="error",
                )
                return await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AllowSpamCog(bot))

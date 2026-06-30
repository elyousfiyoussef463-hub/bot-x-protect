import discord
import re
from discord.ext import commands
from Tools.style import branded_embed, COLORS

class LockCog(commands.Cog, name="lock command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="lock",
        usage="(#channel/ID)",
        description="Lock the channel.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def lock(self, ctx, channel=None):
        if channel:
            channel = re.findall(r"\d+", channel)
            channel = self.bot.get_channel(int(channel[0]))
        else:
            channel = ctx.channel

        if channel:
            new_name = channel.name
            if not new_name.startswith("🔒-"):
                new_name = f"🔒-{new_name}"
            await channel.edit(name=new_name)
            perms = channel.overwrites_for(ctx.guild.default_role)
            perms.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=perms)

            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "lock", "LOCKED_WITH_SUCCESS").format(channel.name),
                color="success",
            )
            await ctx.send(embed=embed)
        else:
            embed = branded_embed(
                description=self.bot.translate.msg(ctx.guild.id, "lock", "CHANNEL_NOT_FOUND"),
                color="error",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LockCog(bot))

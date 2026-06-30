import discord
import re
from discord.ext import commands
from Tools.style import branded_embed, COLORS

class UnlockCog(commands.Cog, name="unlock command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="unlock",
        usage="(#channel/ID)",
        description="Unlock the channel.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def unlock(self, ctx, channel=None):
        if channel:
            channel = re.findall(r"\d+", channel)
            channel = self.bot.get_channel(int(channel[0]))
        else:
            channel = ctx.channel

        if channel:
            name = channel.name
            while name.startswith("🔒-"):
                name = name[2:]
            await channel.edit(name=name)

            perms = channel.overwrites_for(ctx.guild.default_role)
            perms.send_messages = True
            perms.read_messages = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=perms)

            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "unlock", "UNLOCKED_WITH_SUCCESS").format(channel.name),
                color="success",
            )
            await ctx.send(embed=embed)
        else:
            embed = branded_embed(
                description=self.bot.translate.msg(ctx.guild.id, "unlock", "CHANNEL_NOT_FOUND"),
                color="error",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(UnlockCog(bot))

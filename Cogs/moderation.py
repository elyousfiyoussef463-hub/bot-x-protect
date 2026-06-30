import discord
from discord.ext import commands
from discord.utils import get
import re
from Tools.style import branded_embed


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="kick",
        usage="<@user/ID>",
        description="Kick a user.",
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def kick(self, ctx: commands.Context, member, *reason):
        member_id = re.findall(r'\d+', str(member))
        if not member_id:
            embed = branded_embed(
                description=self.bot.translate.msg(ctx.guild.id, "moderation", "MEMBER_NOT_FOUND"),
                color="error",
            )
            await ctx.send(embed=embed)
            return
        guild = ctx.guild
        memberToKick = get(guild.members, id=int(member_id[0]))

        if memberToKick:
            reason = " ".join(reason) if reason else "No reason provided"

            try:
                embed = branded_embed(
                    title=self.bot.translate.msg(ctx.guild.id, "moderation", "YOU_HAVE_BEEN_KICKED").format(guild.name),
                    description=self.bot.translate.msg(ctx.guild.id, "moderation", "KICK_REASON").format(reason),
                    color="error",
                )
                try:
                    await memberToKick.send(embed=embed)
                except discord.Forbidden:
                    pass
            except Exception:
                pass

            try:
                await memberToKick.kick(reason=reason)
            except Exception as error:
                embed = branded_embed(
                    description=self.bot.translate.msg(ctx.guild.id, "global", "ERROR_OCCURED").format(error),
                    color="error",
                )
                await ctx.channel.send(embed=embed)
                return

            if reason:
                await ctx.channel.send(
                    self.bot.translate.msg(ctx.guild.id, "moderation", "HAS_BEEN_KICKED_WITH_REASON").format(memberToKick, reason)
                )
            else:
                await ctx.channel.send(
                    self.bot.translate.msg(ctx.guild.id, "moderation", "HAS_BEEN_KICKED_WITHOUT_REASON").format(memberToKick)
                )
        else:
            embed = branded_embed(
                description=self.bot.translate.msg(ctx.guild.id, "moderation", "MEMBER_NOT_FOUND"),
                color="error",
            )
            await ctx.channel.send(embed=embed)

    @commands.command(
        name="ban",
        usage="<@user/ID>",
        description="Ban a user.",
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def ban(self, ctx: commands.Context, member, *reason):
        member_id = re.findall(r'\d+', str(member))
        if not member_id:
            embed = branded_embed(
                description=self.bot.translate.msg(ctx.guild.id, "moderation", "MEMBER_NOT_FOUND"),
                color="error",
            )
            await ctx.send(embed=embed)
            return
        guild = ctx.guild
        memberToBan = get(guild.members, id=int(member_id[0]))

        if memberToBan:
            reason = " ".join(reason) if reason else "No reason provided"

            try:
                embed = branded_embed(
                    title=self.bot.translate.msg(ctx.guild.id, "moderation", "YOU_HAVE_BEEN_BANNED").format(guild.name),
                    description=self.bot.translate.msg(ctx.guild.id, "moderation", "BAN_REASON").format(reason),
                    color="error",
                )
                try:
                    await memberToBan.send(embed=embed)
                except discord.Forbidden:
                    pass
            except Exception:
                pass

            try:
                await memberToBan.ban(reason=reason)
            except Exception as error:
                embed = branded_embed(
                    description=self.bot.translate.msg(ctx.guild.id, "global", "ERROR_OCCURED").format(error),
                    color="error",
                )
                await ctx.channel.send(embed=embed)
                return

            if reason:
                await ctx.channel.send(
                    self.bot.translate.msg(ctx.guild.id, "moderation", "HAS_BEEN_BANNED_WITH_REASON").format(memberToBan, reason)
                )
            else:
                await ctx.channel.send(
                    self.bot.translate.msg(ctx.guild.id, "moderation", "HAS_BEEN_BANNED_WITHOUT_REASON").format(memberToBan)
                )
        else:
            embed = branded_embed(
                description=self.bot.translate.msg(ctx.guild.id, "moderation", "MEMBER_NOT_FOUND"),
                color="error",
            )
            await ctx.channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))

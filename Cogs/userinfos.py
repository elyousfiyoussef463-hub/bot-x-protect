import discord
import re
from discord.ext import commands
from Tools.style import branded_embed, COLORS, BRAND_NAME, VERSION

class UserInfosCog(commands.Cog, name="user infos command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="userinfos",
        aliases=["ui", "userinfo", "info", "infos"],
        usage="<@user/ID>",
        description="Displays data from user.",
    )
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def userinfos(self, ctx, member):
        member_id = re.findall(r"\d+", str(member))
        if not member_id:
            embed = branded_embed(
                description=self.bot.translate.msg(ctx.guild.id, "userinfos", "MEMBER_NOT_FOUND"),
                color="error",
            )
            await ctx.send(embed=embed)
            return
        member = self.bot.get_user(int(member_id[0]))

        if member is not None:
            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "userinfos", "USER_INFORMATIONS").format(member.name),
                color="info",
                thumbnail=member.display_avatar.url,
            )
            embed.add_field(
                name=self.bot.translate.msg(ctx.guild.id, "userinfos", "MEMBER_ID"),
                value=f"`{member.id}`",
                inline=True,
            )
            embed.add_field(
                name=self.bot.translate.msg(ctx.guild.id, "userinfos", "ACCOUNT_CREATION"),
                value=f"{member.created_at.year}-{member.created_at.month}-{member.created_at.day} {member.created_at.hour}:{member.created_at.minute}:{member.created_at.second}",
                inline=True,
            )
            guild_member = ctx.guild.get_member(member.id)
            if guild_member and guild_member.joined_at:
                embed.add_field(
                    name=self.bot.translate.msg(ctx.guild.id, "userinfos", "JOINED_AT"),
                    value=f"{guild_member.joined_at.year}-{guild_member.joined_at.month}-{guild_member.joined_at.day} {guild_member.joined_at.hour}:{guild_member.joined_at.minute}:{guild_member.joined_at.second}",
                    inline=True,
                )
            await ctx.send(embed=embed)
        else:
            embed = branded_embed(
                description=self.bot.translate.msg(ctx.guild.id, "userinfos", "MEMBER_NOT_FOUND"),
                color="error",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(UserInfosCog(bot))

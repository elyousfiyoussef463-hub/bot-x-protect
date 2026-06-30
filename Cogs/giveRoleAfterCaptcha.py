import discord
from Tools.utils import getConfig, updateConfig, getGuildPrefix
from Tools.style import branded_embed, COLORS
from discord.ext import commands

class GiveRoleAfterCaptchaCog(commands.Cog, name="giveRoleAfterCaptcha command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="giveroleaftercaptcha",
        aliases=["grac", "giverole", "captcharole"],
        usage="<ID/off>",
        description="Enable or disable the role given after the captcha.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def giveroleaftercaptcha(self, ctx, roleId):
        try:
            roleId = int(roleId)
            data = getConfig(ctx.guild.id)
            data["roleGivenAfterCaptcha"] = roleId
            updateConfig(ctx.guild.id, data)

            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "global", "SUCCESS"),
                description=self.bot.translate.msg(ctx.guild.id, "giveRoleAfterCaptcha", "ROLE_GIVEN_AFTER_CAPTCHA").format(roleId),
                color="success",
            )
            await ctx.send(embed=embed)

        except Exception as error:
            print(f"giveroleaftercaptcha error : {error}")
            roleId = roleId.lower()
            if roleId == "off":
                data = getConfig(ctx.guild.id)
                data["roleGivenAfterCaptcha"] = False
                updateConfig(ctx.guild.id, data)

                embed = branded_embed(
                    description="Role given after captcha has been disabled.",
                    color="success",
                )
                await ctx.send(embed=embed)
            else:
                prefix = await getGuildPrefix(self.bot, ctx.message)
                embed = branded_embed(
                    description=self.bot.translate.msg(ctx.guild.id, "giveRoleAfterCaptcha", "INVALID_ARGUMENT").format(prefix),
                    color="error",
                )
                await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(GiveRoleAfterCaptchaCog(bot))

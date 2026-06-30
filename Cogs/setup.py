import discord
import asyncio
from discord.ext import commands
from discord.utils import get
from Tools.utils import getConfig, updateConfig, getGuildPrefix
from Tools.style import branded_embed, COLORS

class SetupCog(commands.Cog, name="setup command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="setup",
        aliases=["captcha"],
        usage="<on/off>",
        description="Enable or disable the captcha system.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def setup(self, ctx, onOrOff):
        onOrOff = onOrOff.lower()

        if onOrOff == "on":
            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "setup", "DO_YOU_WANT_TO_SET_UP_THE_CAPTCHA_PROTECTION"),
                description=self.bot.translate.msg(ctx.guild.id, "setup", "DO_YOU_WANT_TO_SET_UP_THE_CAPTCHA_PROTECTION_DESCRIPTION"),
                color="warning",
            )
            await ctx.send(embed=embed)

            def check(message):
                if message.author == ctx.author and message.content in ["yes", "no"]:
                    return message.content

            try:
                msg = await self.bot.wait_for("message", timeout=30.0, check=check)
                if msg.content == "no":
                    embed = branded_embed(
                        description=self.bot.translate.msg(ctx.guild.id, "setup", "SET_UP_ABANDONED"),
                        color="neutral",
                    )
                    await ctx.send(embed=embed)
                else:
                    try:
                        loading = await ctx.send(
                            self.bot.translate.msg(ctx.guild.id, "setup", "CREATION_OF_CAPTCHA_PRETECTION")
                        )

                        data = getConfig(ctx.guild.id)

                        temporaryRole = await ctx.guild.create_role(name="untested")
                        for channel in ctx.guild.channels:
                            if isinstance(channel, discord.TextChannel):
                                perms = channel.overwrites_for(temporaryRole)
                                perms.read_messages = False
                                await channel.set_permissions(temporaryRole, overwrite=perms)
                            elif isinstance(channel, discord.VoiceChannel):
                                perms = channel.overwrites_for(temporaryRole)
                                perms.read_messages = False
                                perms.connect = False
                                await channel.set_permissions(temporaryRole, overwrite=perms)

                        captchaChannel = await ctx.guild.create_text_channel("verification")

                        perms = captchaChannel.overwrites_for(temporaryRole)
                        perms.read_messages = True
                        perms.send_messages = True
                        await captchaChannel.set_permissions(temporaryRole, overwrite=perms)

                        perms = captchaChannel.overwrites_for(ctx.guild.default_role)
                        perms.read_messages = False
                        await captchaChannel.set_permissions(ctx.guild.default_role, overwrite=perms)

                        await captchaChannel.edit(slowmode_delay=5)

                        if data["logChannel"] is False:
                            logChannel = await ctx.guild.create_text_channel(f"{self.bot.user.name}-logs")
                            perms = logChannel.overwrites_for(ctx.guild.default_role)
                            perms.read_messages = False
                            await logChannel.set_permissions(ctx.guild.default_role, overwrite=perms)
                            data["logChannel"] = logChannel.id

                        data["captcha"] = True
                        data["temporaryRole"] = temporaryRole.id
                        data["captchaChannel"] = captchaChannel.id

                        updateConfig(ctx.guild.id, data)

                        await loading.delete()
                        embed = branded_embed(
                            title=self.bot.translate.msg(ctx.guild.id, "setup", "CAPTCHA_WAS_SET_UP_WITH_SUCCESS"),
                            description=self.bot.translate.msg(ctx.guild.id, "setup", "CAPTCHA_WAS_SET_UP_WITH_SUCCESS_DESCRIPTION"),
                            color="success",
                        )
                        await ctx.send(embed=embed)
                    except Exception as error:
                        embed = branded_embed(
                            title=self.bot.translate.msg(ctx.guild.id, "global", "ERROR"),
                            description=self.bot.translate.msg(ctx.guild.id, "global", "ERROR_OCCURED").format(error),
                            color="error",
                        )
                        return await ctx.send(embed=embed)

            except asyncio.TimeoutError:
                embed = branded_embed(
                    title=self.bot.translate.msg(ctx.guild.id, "setup", "TIME_IS_OUT"),
                    description=self.bot.translate.msg(ctx.guild.id, "setup", "USER_HAS_EXCEEDED_THE_RESPONSE_TIME").format(ctx.author.mention),
                    color="error",
                )
                await ctx.send(embed=embed)

        elif onOrOff == "off":
            loading = await ctx.send(
                self.bot.translate.msg(ctx.guild.id, "setup", "DELETION_OF_THE_CAPTCHA_PROETECTION")
            )
            data = getConfig(ctx.guild.id)
            data["captcha"] = False

            noDeleted = []
            try:
                temporaryRole = get(ctx.guild.roles, id=data["temporaryRole"])
                await temporaryRole.delete()
            except Exception as error:
                print(f"Failed to delete temporary role: {error}")
                noDeleted.append("temporaryRole")
            try:
                captchaChannel = self.bot.get_channel(data["captchaChannel"])
                await captchaChannel.delete()
            except Exception as error:
                print(f"Failed to delete captcha channel: {error}")
                noDeleted.append("captchaChannel")

            data["captchaChannel"] = False

            updateConfig(ctx.guild.id, data)

            await loading.delete()
            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "setup", "CAPTCHA_WAS_DELETED_WITH_SUCCESS"),
                description=self.bot.translate.msg(ctx.guild.id, "setup", "CAPTCHA_WAS_DELETED_WITH_SUCCESS_DESCRIPTION"),
                color="success",
            )
            await ctx.send(embed=embed)
            if len(noDeleted) > 0:
                errors = ", ".join(noDeleted)
                embed = branded_embed(
                    title=self.bot.translate.msg(ctx.guild.id, "setup", "CAPTCHA_DELETION_ERROR"),
                    description=self.bot.translate.msg(ctx.guild.id, "setup", "CAPTCHA_DELETION_ERROR_DESCRIPTION").format(errors),
                    color="error",
                )
                await ctx.send(embed=embed)

        else:
            prefix = await getGuildPrefix(self.bot, ctx.message)
            embed = branded_embed(
                title=self.bot.translate.msg(ctx.guild.id, "global", "ERROR"),
                description=self.bot.translate.msg(ctx.guild.id, "setup", "INVALID_ARGUMENT").format(prefix),
                color="error",
            )
            return await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(SetupCog(bot))

import discord
from discord.ext import commands
from Tools.utils import getGuildPrefix
from Tools.style import branded_embed, COLORS, BRAND_NAME, VERSION

class HelpCog(commands.Cog, name="help command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="help",
        usage="(commandName)",
        description="Display the help message.",
    )
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def help(self, ctx, commandName=None):
        prefix = await getGuildPrefix(self.bot, ctx)
        bot_user = self.bot.user

        if commandName is not None:
            cmd = None
            for c in self.bot.commands:
                if c.name == commandName.lower() or commandName.lower() in c.aliases:
                    cmd = c
                    break

            if cmd is None:
                embed = branded_embed(
                    description=f"Command `{commandName}` not found.",
                    color="error",
                )
                return await ctx.send(embed=embed)

            aliases = ", ".join(cmd.aliases) if cmd.aliases else "None"
            usage = f"{prefix}{cmd.name} {cmd.usage or ''}"

            embed = branded_embed(
                title=f"Command: {cmd.name.upper()}",
                description=f"```{usage}```",
                color="primary",
                thumbnail=bot_user.display_avatar.url,
            )
            embed.add_field(name="Aliases", value=f"`{aliases}`", inline=True)
            embed.add_field(name="Description", value=cmd.description, inline=False)
            await ctx.send(embed=embed)
        else:
            embed = branded_embed(
                title=f"{BRAND_NAME} Help",
                description=(
                    f"Use `{prefix}help (command)` for details on a specific command.\n\n"
                    f"**{prefix}help (command)** — Display help for a command"
                ),
                color="primary",
                thumbnail=bot_user.display_avatar.url,
            )
            embed.add_field(
                name="Administration",
                value=(
                    f"`{prefix}setup <on/off>` — Captcha protection\n"
                    f"`{prefix}settings` — Server settings\n"
                    f"`{prefix}panel` — Protection control panel\n"
                    f"`{prefix}setbotrole @role` — Authorized bot role\n"
                    f"`{prefix}giveroleaftercaptcha <ID/off>` — Post-captcha role\n"
                    f"`{prefix}minaccountage <hours>` — Min account age\n"
                    f"`{prefix}antinudity <true/false>` — Nudity filter\n"
                    f"`{prefix}antiprofanity <true/false>` — Profanity filter\n"
                    f"`{prefix}antispam <true/false>` — Spam protection\n"
                    f"`{prefix}allowspam <#channel> [remove]` — Spam exemption\n"
                    f"`{prefix}lock | unlock <#channel>` — Lock/unlock channel\n"
                    f"`{prefix}kick <@user> [reason]` — Kick member\n"
                    f"`{prefix}ban <@user> [reason]` — Ban member\n"
                    f"`{prefix}changeprefix <prefix>` — Change prefix\n"
                    f"`{prefix}changelanguage <lang>` — Change language"
                ),
                inline=False,
            )
            embed.add_field(
                name="Commands",
                value=f"`{prefix}userinfos <@user>` — User information",
                inline=False,
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))

import discord
from discord.ext import commands
from Tools.utils import getConfig, updateConfig
from Tools.style import branded_embed, COLORS
from datetime import datetime

class AntiBotCog(commands.Cog, name="Anti-Bot and Auto Ban Protection"):
    def __init__(self, bot):
        self.bot = bot

    async def send_alert(self, guild, title, description):
        try:
            config = getConfig(guild.id)
            log_channel_id = config.get("logChannel", None)

            if log_channel_id and log_channel_id != 1:
                log_channel = guild.get_channel(log_channel_id)
                if log_channel:
                    embed = branded_embed(
                        title=title,
                        description=description,
                        color="error",
                    )
                    await log_channel.send(embed=embed)
        except Exception as e:
            print(f"send_alert error: {e}")

    async def is_guild_owner(self, guild, user):
        return guild.owner_id == user.id

    async def is_whitelisted(self, guild, user):
        config = getConfig(guild.id)
        whitelist = config.get("whitelist", [])
        if user.id in whitelist:
            return True
        if await self.is_guild_owner(guild, user):
            return True
        return False

    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = getConfig(member.guild.id)
        if not config.get("antiBot", False):
            return

        if member.bot:
            try:
                async for entry in member.guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
                    if entry.target == member and entry.user and not await self.is_whitelisted(member.guild, entry.user):
                        try:
                            await member.ban(reason="Suspicious bot detected - Auto banned by protection system")
                            await self.send_alert(
                                member.guild,
                                "Bot Detected and Banned",
                                f"🤖 **{member.name}** (ID: {member.id}) was banned automatically.\n"
                                f"Added by: {entry.user.mention} ({entry.user.name}#{entry.user.discriminator})\n"
                                f"Reason: Suspicious bot detected",
                            )
                        except Exception as e:
                            print(f"Failed to ban suspicious bot {member.name}: {e}")
            except Exception as e:
                print(f"Failed to check bot_add audit log: {e}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        config = getConfig(guild.id)
        if not config.get("antiRaid", False):
            return

        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
                if entry.target == user and entry.user and not await self.is_whitelisted(guild, entry.user):
                    if user == self.bot.user:
                        try:
                            await guild.ban(entry.user, reason="Attempted to ban protection bot - Auto banned")
                            await self.send_alert(
                                guild,
                                "Bot Ban Attempt Detected",
                                f"🚫 **{entry.user.name}** ({entry.user.mention}) tried to ban the protection bot.\n"
                                f"Action: **Auto-banned** for attempting sabotage",
                            )
                        except Exception as e:
                            print(f"Failed to ban bot banisher: {e}")
                    elif entry.user.guild_permissions.administrator or entry.user.guild_permissions.ban_members:
                        if user.guild_permissions.administrator or user.guild_permissions.ban_members:
                            try:
                                await guild.ban(entry.user, reason="Attempted to ban admin/mod - Auto banned")
                                await self.send_alert(
                                    guild,
                                    "Admin Ban Attempt Detected",
                                    f"🚫 **{entry.user.name}** ({entry.user.mention}) tried to ban **{user.name}** (Admin/Mod).\n"
                                    f"Action: **Auto-banned** for attempting sabotage",
                                )
                            except Exception as e:
                                print(f"Failed to ban admin banisher: {e}")
        except Exception as e:
            print(f"Failed to check ban audit log: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        config = getConfig(after.guild.id)
        if not config.get("antiRaid", False):
            return

        removed_roles = set(before.roles) - set(after.roles)

        for role in removed_roles:
            if role.permissions.administrator:
                try:
                    async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=5):
                        if entry.target == after and entry.user and not await self.is_whitelisted(after.guild, entry.user):
                            try:
                                await after.guild.ban(entry.user, reason="Attempted to remove admin role - Auto banned")
                                await self.send_alert(
                                    after.guild,
                                    "Admin Removal Attempt Detected",
                                    f"🚫 **{entry.user.name}** ({entry.user.mention}) tried to remove admin from **{after.name}**.\n"
                                    f"Action: **Auto-banned** for attempting sabotage",
                                )
                            except Exception as e:
                                print(f"Failed to ban admin role remover: {e}")
                            break
                except Exception as e:
                    print(f"Failed to check member update audit log: {e}")

    @commands.command(
        name="antibot",
        usage="<on/off>",
        description="Enable or disable auto-ban for suspicious bots.",
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.guild_only()
    async def antibot(self, ctx, status):
        status = status.lower()

        if status == "on":
            config = getConfig(ctx.guild.id)
            config["antiBot"] = True
            updateConfig(ctx.guild.id, config)

            embed = branded_embed(
                title="Anti-Bot Protection Enabled",
                description="Suspicious bots will be automatically banned.",
                color="success",
            )
            await ctx.send(embed=embed)

        elif status == "off":
            config = getConfig(ctx.guild.id)
            config["antiBot"] = False
            updateConfig(ctx.guild.id, config)

            embed = branded_embed(
                title="Anti-Bot Protection Disabled",
                description="Anti-bot protection has been disabled.",
                color="error",
            )
            await ctx.send(embed=embed)
        else:
            embed = branded_embed(
                description="Usage: `?antibot <on/off>`",
                color="error",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AntiBotCog(bot))

import time
import discord
from discord.ext import commands
from discord import AuditLogAction
from Tools.utils import getConfig, updateConfig
from Tools.logMessage import sendLogMessage
from Tools.style import branded_embed, COLORS


def now_seconds():
    return time.time()


class AntiRaidCog(commands.Cog, name="Anti-Raid Protection"):
    def __init__(self, bot):
        self.bot = bot
        self.recent_actions = {}

    def _get_guild_state(self, guild_id):
        return self.recent_actions.setdefault(guild_id, {})

    def _record_action(self, guild_id, user_id, key, window):
        guild_state = self._get_guild_state(guild_id)
        users = guild_state.setdefault(key, {})
        now = now_seconds()
        timestamps = users.setdefault(user_id, [])
        timestamps.append(now)
        users[user_id] = [ts for ts in timestamps if now - ts <= window]
        return len(users[user_id])

    def _is_trusted(self, guild, member, config):
        if member is None:
            return False
        if member.id == guild.owner_id:
            return True
        if member.guild_permissions.administrator:
            return True
        if member.id == self.bot.user.id:
            return True
        trusted = config.get("whitelist", [])
        return member.id in trusted

    def _raid_limits(self, level):
        if level == 1:
            return 4, 60
        if level == 2:
            return 3, 45
        if level == 3:
            return 2, 30
        return 1, 20

    async def _get_audit_entry(self, guild, action):
        try:
            async for entry in guild.audit_logs(action=action, limit=5):
                return entry
        except Exception:
            return None

    async def _punish_executor(self, guild, executor, reason):
        if executor is None:
            return False
        try:
            if guild.me.guild_permissions.ban_members:
                await guild.ban(executor, reason=reason, delete_message_days=1)
                return True
            if guild.me.guild_permissions.kick_members:
                await guild.kick(executor, reason=reason)
                return True
        except Exception:
            pass
        return False

    async def _restore_channel(self, channel):
        guild = channel.guild
        try:
            category = channel.category
            if isinstance(channel, discord.CategoryChannel):
                new = await guild.create_category_channel(
                    name=channel.name,
                    overwrites=channel.overwrites,
                    position=channel.position,
                    reason="Restore deleted category",
                )
                for child in channel.channels:
                    try:
                        if isinstance(child, discord.TextChannel):
                            await guild.create_text_channel(
                                name=child.name, category=new, position=child.position,
                                reason="Restore channel from deleted category",
                            )
                        elif isinstance(child, discord.VoiceChannel):
                            await guild.create_voice_channel(
                                name=child.name, category=new, position=child.position,
                                reason="Restore channel from deleted category",
                            )
                    except Exception:
                        pass
            elif isinstance(channel, discord.TextChannel):
                await guild.create_text_channel(
                    name=channel.name,
                    overwrites=channel.overwrites,
                    topic=channel.topic,
                    category=category,
                    nsfw=channel.is_nsfw(),
                    slowmode_delay=getattr(channel, "slowmode_delay", 0),
                    position=channel.position,
                    reason="Restore deleted channel",
                )
            elif isinstance(channel, discord.VoiceChannel):
                await guild.create_voice_channel(
                    name=channel.name,
                    overwrites=channel.overwrites,
                    category=category,
                    bitrate=channel.bitrate,
                    user_limit=channel.user_limit,
                    position=channel.position,
                    reason="Restore deleted channel",
                )
            elif isinstance(channel, discord.ForumChannel):
                await guild.create_forum_channel(
                    name=channel.name,
                    overwrites=channel.overwrites,
                    category=category,
                    position=channel.position,
                    reason="Restore deleted forum channel",
                )
            else:
                return False
            return True
        except Exception:
            return False

    async def _restore_role(self, role):
        guild = role.guild
        try:
            new_role = await guild.create_role(
                name=role.name,
                permissions=role.permissions,
                colour=role.colour,
                hoist=role.hoist,
                mentionable=role.mentionable,
                position=role.position,
                reason="Restore deleted role",
            )
            return True
        except Exception:
            return False

    async def _send_log(self, event, config, embed):
        channel_id = config.get("logChannel")
        if not channel_id or channel_id is True or channel_id == 1:
            return
        await sendLogMessage(self, event=event, channel=channel_id, embed=embed)

    async def _handle_delete(self, event, audit_action, action_key, protection_flag, restore=True):
        guild = event.guild
        config = getConfig(guild.id)
        auto_restore = config.get("autoRestore", True)
        if not config.get(protection_flag, False) and event.id not in config.get("protectedChannels", []) and not auto_restore:
            return

        entry = await self._get_audit_entry(guild, audit_action)
        executor = entry.user if entry else None
        if self._is_trusted(guild, executor, config):
            return

        level = config.get("raidLevel", 1)
        limit, window = self._raid_limits(level)
        count = self._record_action(guild.id, executor.id if executor else 0, action_key, window)

        if auto_restore or event.id in config.get("protectedChannels", []) or count >= limit:
            label = "Category" if isinstance(event, discord.CategoryChannel) else "Channel"
            restored = await self._restore_channel(event) if restore else False
            punished = await self._punish_executor(
                guild, executor, f"Auto-protection triggered for {audit_action.name}"
            )
            embed = branded_embed(
                title="Anti-Nuke Alert",
                description=f"{label} `{event.name}` was deleted by {executor or 'unknown'}.",
                color="error",
            )
            embed.add_field(name="Restored", value="✓" if restored else "✗", inline=True)
            embed.add_field(name="Punished", value="✓" if punished else "✗", inline=True)
            await self._send_log(event, config, embed)

    @commands.command(name="autorestore", aliases=["antidelete"], description="Toggle auto-restore of deleted channels/roles")
    @commands.has_permissions(administrator=True)
    async def autorestore(self, ctx):
        config = getConfig(ctx.guild.id)
        current = config.get("autoRestore", True)
        config["autoRestore"] = not current
        updateConfig(ctx.guild.id, config)
        status = "enabled" if config["autoRestore"] else "disabled"
        embed = branded_embed(description=f"Auto-restore **{status}**. Deleted channels and roles will{' not' if not config['autoRestore'] else ''} be recreated.", color="success" if config['autoRestore'] else "error")
        await ctx.send(embed=embed)

    @commands.command(name="protectchannel", description="Protect a channel from deletion")
    @commands.has_permissions(administrator=True)
    async def protectchannel(self, ctx, channel: discord.TextChannel):
        config = getConfig(ctx.guild.id)
        protected = config.get("protectedChannels", [])
        if channel.id in protected:
            embed = branded_embed(description=f"{channel.mention} is already protected.", color="warning")
            return await ctx.send(embed=embed)
        protected.append(channel.id)
        config["protectedChannels"] = protected
        updateConfig(ctx.guild.id, config)
        embed = branded_embed(description=f"{channel.mention} is now protected from deletion.", color="success")
        await ctx.send(embed=embed)

    @commands.command(name="unprotectchannel", description="Remove channel protection")
    @commands.has_permissions(administrator=True)
    async def unprotectchannel(self, ctx, channel: discord.TextChannel):
        config = getConfig(ctx.guild.id)
        protected = config.get("protectedChannels", [])
        if channel.id not in protected:
            embed = branded_embed(description=f"{channel.mention} was not protected.", color="warning")
            return await ctx.send(embed=embed)
        protected.remove(channel.id)
        config["protectedChannels"] = protected
        updateConfig(ctx.guild.id, config)
        embed = branded_embed(description=f"{channel.mention} is no longer protected.", color="success")
        await ctx.send(embed=embed)

    @commands.command(name="protectrole", description="Protect a role from deletion")
    @commands.has_permissions(administrator=True)
    async def protectrole(self, ctx, role: discord.Role):
        config = getConfig(ctx.guild.id)
        protected = config.get("protectedRoles", [])
        if role.id in protected:
            embed = branded_embed(description=f"Role `{role.name}` is already protected.", color="warning")
            return await ctx.send(embed=embed)
        protected.append(role.id)
        config["protectedRoles"] = protected
        updateConfig(ctx.guild.id, config)
        embed = branded_embed(description=f"Role `{role.name}` is now protected.", color="success")
        await ctx.send(embed=embed)

    @commands.command(name="unprotectrole", description="Remove role protection")
    @commands.has_permissions(administrator=True)
    async def unprotectrole(self, ctx, role: discord.Role):
        config = getConfig(ctx.guild.id)
        protected = config.get("protectedRoles", [])
        if role.id not in protected:
            embed = branded_embed(description=f"Role `{role.name}` was not protected.", color="warning")
            return await ctx.send(embed=embed)
        protected.remove(role.id)
        config["protectedRoles"] = protected
        updateConfig(ctx.guild.id, config)
        embed = branded_embed(description=f"Role `{role.name}` is no longer protected.", color="success")
        await ctx.send(embed=embed)

    @commands.command(name="raidlevel", description="Set anti-raid sensitivity level (1-4)")
    @commands.has_permissions(administrator=True)
    async def raidlevel(self, ctx, level: int):
        if level < 1 or level > 4:
            embed = branded_embed(description="Invalid level. Use 1 to 4.", color="error")
            return await ctx.send(embed=embed)
        config = getConfig(ctx.guild.id)
        config["raidLevel"] = level
        updateConfig(ctx.guild.id, config)
        embed = branded_embed(description=f"Anti-raid level set to **{level}**.", color="success")
        await ctx.send(embed=embed)

    @commands.command(name="antiraidstatus", description="Check anti-raid status")
    @commands.has_permissions(administrator=True)
    async def antiraidstatus(self, ctx):
        config = getConfig(ctx.guild.id)
        protected_channels = config.get("protectedChannels", [])
        protected_roles = config.get("protectedRoles", [])
        embed = branded_embed(title="Anti-Raid Status", color="info")
        embed.add_field(name="Raid Level", value=str(config.get("raidLevel", 1)), inline=False)
        embed.add_field(name="Protected Channels", value=str(len(protected_channels)), inline=True)
        embed.add_field(name="Protected Roles", value=str(len(protected_roles)), inline=True)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await self._handle_delete(channel, AuditLogAction.channel_delete, "channel_delete", "nukeProtection")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        guild = role.guild
        config = getConfig(guild.id)
        auto_restore = config.get("autoRestore", True)
        if not config.get("roleNukeProtection", False) and role.id not in config.get("protectedRoles", []) and not auto_restore:
            return

        entry = await self._get_audit_entry(guild, AuditLogAction.role_delete)
        executor = entry.user if entry else None
        if self._is_trusted(guild, executor, config):
            return

        level = config.get("raidLevel", 1)
        limit, window = self._raid_limits(level)
        count = self._record_action(guild.id, executor.id if executor else 0, "role_delete", window)
        if auto_restore or role.id in config.get("protectedRoles", []) or count >= limit:
            restored = await self._restore_role(role)
            punished = await self._punish_executor(
                guild, executor, "Auto-protection triggered for role deletion"
            )
            embed = branded_embed(
                title="Anti-Nuke Alert",
                description=f"Role `{role.name}` was deleted by {executor or 'unknown'}.",
                color="error",
            )
            embed.add_field(name="Restored", value="✓" if restored else "✗", inline=True)
            embed.add_field(name="Punished", value="✓" if punished else "✗", inline=True)
            await self._send_log(role, config, embed)

    @commands.Cog.listener()
    async def on_guild_webhooks_update(self, guild):
        config = getConfig(guild.id)
        if not config.get("webhookNukeProtection", False):
            return
        entry = await self._get_audit_entry(guild, AuditLogAction.webhook_delete)
        executor = entry.user if entry else None
        if self._is_trusted(guild, executor, config):
            return
        level = config.get("raidLevel", 1)
        limit, window = self._raid_limits(level)
        count = self._record_action(guild.id, executor.id if executor else 0, "webhook_delete", window)
        if count >= limit:
            punished = await self._punish_executor(
                guild, executor, "Auto-protection triggered for webhook deletion"
            )
            embed = branded_embed(
                title="Anti-Nuke Alert",
                description=f"Webhook activity suspicious by {executor or 'unknown'}.",
                color="error",
            )
            await self._send_log(guild, config, embed)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        config = getConfig(guild.id)
        if not config.get("emojiNukeProtection", False):
            return
        removed = [emoji for emoji in before if emoji not in after]
        if not removed:
            return
        entry = await self._get_audit_entry(guild, AuditLogAction.emoji_delete)
        executor = entry.user if entry else None
        if self._is_trusted(guild, executor, config):
            return
        punished = await self._punish_executor(
            guild, executor, "Auto-protection triggered for emoji deletion"
        )
        embed = branded_embed(
            title="Anti-Nuke Alert",
            description=f"Emoji deleted by {executor or 'unknown'}.",
            color="error",
        )
        embed.add_field(name="Punished", value="✓" if punished else "✗", inline=True)
        await self._send_log(guild, config, embed)


async def setup(bot):
    await bot.add_cog(AntiRaidCog(bot))

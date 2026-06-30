import discord
from discord.ext import commands
from Tools.utils import getConfig, updateConfig
from Tools.style import branded_embed
from datetime import datetime, timedelta


class MegaProtectionCog(commands.Cog, name="Mega Protection"):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_users = {}
        self.trusted_users = {}

    def _get_cfg(self, guild_id):
        return getConfig(guild_id)

    def _save_cfg(self, guild_id, data):
        updateConfig(guild_id, data)

    async def _toggle(self, ctx, key, msg_on, msg_off=None, value=None):
        config = self._get_cfg(ctx.guild.id)
        if value is not None:
            config[key] = value
        else:
            config[key] = not config.get(key, False)
        self._save_cfg(ctx.guild.id, config)
        if config[key]:
            await ctx.send(f"✅ {msg_on}")
        elif msg_off:
            await ctx.send(f"❌ {msg_off}")

    async def _set_value(self, ctx, key, value, msg):
        config = self._get_cfg(ctx.guild.id)
        config[key] = value
        self._save_cfg(ctx.guild.id, config)
        await ctx.send(f"✅ {msg}")

    # ============ ANTI-RAID ============
    @commands.command(name='antiraid1', description="Enable raid detection level 1 (Low)")
    @commands.has_permissions(administrator=True)
    async def antiraid1(self, ctx):
        await self._set_value(ctx, 'raidLevel', 1, "Raid Detection Level 1 (Low sensitivity)")

    @commands.command(name='antiraid2', description="Enable raid detection level 2 (Medium)")
    @commands.has_permissions(administrator=True)
    async def antiraid2(self, ctx):
        await self._set_value(ctx, 'raidLevel', 2, "Raid Detection Level 2 (Medium sensitivity)")

    @commands.command(name='antiraid3', description="Enable raid detection level 3 (High)")
    @commands.has_permissions(administrator=True)
    async def antiraid3(self, ctx):
        await self._set_value(ctx, 'raidLevel', 3, "Raid Detection Level 3 (High sensitivity)")

    @commands.command(name='antiraid4', description="Enable raid detection level 4 (Extreme)")
    @commands.has_permissions(administrator=True)
    async def antiraid4(self, ctx):
        await self._set_value(ctx, 'raidLevel', 4, "Raid Detection Level 4 (Extreme sensitivity)")

    # ============ ANTI-NUKE ============
    NUKE_KEYS = [
        ('antinuke1', 'nukeProtection', 'Channel Nuke Protection'),
        ('antinuke2', 'roleNukeProtection', 'Role Nuke Protection'),
        ('antinuke3', 'memberNukeProtection', 'Member Nuke Protection'),
        ('antinuke4', 'webhookNukeProtection', 'Webhook Nuke Protection'),
        ('antinuke5', 'emojiNukeProtection', 'Emoji Nuke Protection'),
        ('antinuke6', 'stickerNukeProtection', 'Sticker Nuke Protection'),
    ]

    @commands.command(name='antinuke1', description="Enable channel nuke detection")
    @commands.has_permissions(administrator=True)
    async def antinuke1(self, ctx): await self._toggle(ctx, 'nukeProtection', "Channel Nuke Protection Enabled", "Channel Nuke Protection Disabled")

    @commands.command(name='antinuke2', description="Enable role nuke detection")
    @commands.has_permissions(administrator=True)
    async def antinuke2(self, ctx): await self._toggle(ctx, 'roleNukeProtection', "Role Nuke Protection Enabled", "Role Nuke Protection Disabled")

    @commands.command(name='antinuke3', description="Enable member nuke detection")
    @commands.has_permissions(administrator=True)
    async def antinuke3(self, ctx): await self._toggle(ctx, 'memberNukeProtection', "Member Nuke Protection Enabled", "Member Nuke Protection Disabled")

    @commands.command(name='antinuke4', description="Enable webhook nuke detection")
    @commands.has_permissions(administrator=True)
    async def antinuke4(self, ctx): await self._toggle(ctx, 'webhookNukeProtection', "Webhook Nuke Protection Enabled", "Webhook Nuke Protection Disabled")

    @commands.command(name='antinuke5', description="Enable emoji nuke detection")
    @commands.has_permissions(administrator=True)
    async def antinuke5(self, ctx): await self._toggle(ctx, 'emojiNukeProtection', "Emoji Nuke Protection Enabled", "Emoji Nuke Protection Disabled")

    @commands.command(name='antinuke6', description="Enable sticker nuke detection")
    @commands.has_permissions(administrator=True)
    async def antinuke6(self, ctx): await self._toggle(ctx, 'stickerNukeProtection', "Sticker Nuke Protection Enabled", "Sticker Nuke Protection Disabled")

    # ============ ANTI-SPAM ============
    @commands.command(name='antispam1', description="Enable message spam detection")
    @commands.has_permissions(administrator=True)
    async def antispam1(self, ctx): await self._toggle(ctx, 'spamProtection', "Message Spam Protection Enabled", "Message Spam Protection Disabled")

    @commands.command(name='antispam2', description="Enable mention spam detection")
    @commands.has_permissions(administrator=True)
    async def antispam2(self, ctx): await self._toggle(ctx, 'mentionSpamProtection', "Mention Spam Protection Enabled", "Mention Spam Protection Disabled")

    @commands.command(name='antispam3', description="Enable emoji spam detection")
    @commands.has_permissions(administrator=True)
    async def antispam3(self, ctx): await self._toggle(ctx, 'emojiSpamProtection', "Emoji Spam Protection Enabled", "Emoji Spam Protection Disabled")

    @commands.command(name='antispam4', description="Enable link spam detection")
    @commands.has_permissions(administrator=True)
    async def antispam4(self, ctx): await self._toggle(ctx, 'linkSpamProtection', "Link Spam Protection Enabled", "Link Spam Protection Disabled")

    @commands.command(name='antispam5', description="Enable ad spam detection")
    @commands.has_permissions(administrator=True)
    async def antispam5(self, ctx): await self._toggle(ctx, 'adSpamProtection', "Ad Spam Protection Enabled", "Ad Spam Protection Disabled")

    @commands.command(name='antispam6', description="Enable rapid message detection")
    @commands.has_permissions(administrator=True)
    async def antispam6(self, ctx): await self._toggle(ctx, 'rapidMessageProtection', "Rapid Message Protection Enabled", "Rapid Message Protection Disabled")

    @commands.command(name='antispam7', description="Enable caps spam detection")
    @commands.has_permissions(administrator=True)
    async def antispam7(self, ctx): await self._toggle(ctx, 'capsSpamProtection', "Caps Spam Protection Enabled", "Caps Spam Protection Disabled")

    @commands.command(name='antispam8', description="Enable unicode spam detection")
    @commands.has_permissions(administrator=True)
    async def antispam8(self, ctx): await self._toggle(ctx, 'unicodeSpamProtection', "Unicode Spam Protection Enabled", "Unicode Spam Protection Disabled")

    @commands.command(name='antispam9', description="Enable webhook spam detection")
    @commands.has_permissions(administrator=True)
    async def antispam9(self, ctx): await self._toggle(ctx, 'webhookSpamProtection', "Webhook Spam Protection Enabled", "Webhook Spam Protection Disabled")

    @commands.command(name='antispam10', description="Enable dm spam detection")
    @commands.has_permissions(administrator=True)
    async def antispam10(self, ctx): await self._toggle(ctx, 'dmSpamProtection', "DM Spam Protection Enabled", "DM Spam Protection Disabled")

    # ============ USER PROTECTION ============
    @commands.command(name='blockuser', description="Block a user from the server")
    @commands.has_permissions(administrator=True)
    async def blockuser(self, ctx, user: discord.User):
        self.blocked_users.setdefault(ctx.guild.id, []).append(user.id)
        await ctx.send(f"✅ {user.mention} has been blocked")

    @commands.command(name='trustuser', description="Mark a user as trusted")
    @commands.has_permissions(administrator=True)
    async def trustuser(self, ctx, user: discord.User):
        self.trusted_users.setdefault(ctx.guild.id, []).append(user.id)
        await ctx.send(f"✅ {user.mention} has been marked as trusted")

    @commands.command(name='protectrole1', description="Protect a role from deletion")
    @commands.has_permissions(administrator=True)
    async def protectrole1(self, ctx, role: discord.Role):
        config = self._get_cfg(ctx.guild.id)
        config.setdefault('protectedRoles', []).append(role.id)
        self._save_cfg(ctx.guild.id, config)
        await ctx.send(f"✅ {role.mention} is now protected")

    @commands.command(name='protectchannel1', description="Protect a channel from deletion")
    @commands.has_permissions(administrator=True)
    async def protectchannel1(self, ctx, channel: discord.TextChannel):
        config = self._get_cfg(ctx.guild.id)
        config.setdefault('protectedChannels', []).append(channel.id)
        self._save_cfg(ctx.guild.id, config)
        await ctx.send(f"✅ {channel.mention} is now protected")

    @commands.command(name='lockdown1', description="Enable lockdown mode")
    @commands.has_permissions(administrator=True)
    async def lockdown1(self, ctx):
        await self._toggle(ctx, 'lockdownMode', "Lockdown mode enabled")

    @commands.command(name='whitelistuser', description="Whitelist a user")
    @commands.has_permissions(administrator=True)
    async def whitelistuser(self, ctx, user: discord.User):
        config = self._get_cfg(ctx.guild.id)
        config.setdefault('whitelist', []).append(user.id)
        self._save_cfg(ctx.guild.id, config)
        await ctx.send(f"✅ {user.mention} has been whitelisted")

    @commands.command(name='blacklistuser', description="Blacklist a user")
    @commands.has_permissions(administrator=True)
    async def blacklistuser(self, ctx, user: discord.User):
        config = self._get_cfg(ctx.guild.id)
        config.setdefault('blacklist', []).append(user.id)
        self._save_cfg(ctx.guild.id, config)
        await ctx.send(f"✅ {user.mention} has been blacklisted")

    @commands.command(name='verifyuser', description="Request user verification")
    @commands.has_permissions(administrator=True)
    async def verifyuser(self, ctx):
        await self._toggle(ctx, 'verificationRequired', "User verification required on join")

    @commands.command(name='safechannel', description="Mark channel as safe")
    @commands.has_permissions(administrator=True)
    async def safechannel(self, ctx, channel: discord.TextChannel):
        config = self._get_cfg(ctx.guild.id)
        config.setdefault('safeChannels', []).append(channel.id)
        self._save_cfg(ctx.guild.id, config)
        await ctx.send(f"✅ {channel.mention} marked as safe")

    @commands.command(name='dangeroususer', description="Flag user as suspicious")
    @commands.has_permissions(administrator=True)
    async def dangeroususer(self, ctx, user: discord.User):
        config = self._get_cfg(ctx.guild.id)
        config.setdefault('flaggedUsers', []).append(user.id)
        self._save_cfg(ctx.guild.id, config)
        await ctx.send(f"⚠️ {user.mention} has been flagged as suspicious")

    # ============ MODERATION ============
    @commands.command(name='muteuser', description="Mute a user in voice")
    @commands.has_permissions(administrator=True)
    async def muteuser(self, ctx, user: discord.Member):
        await user.edit(mute=True)
        await ctx.send(f"🔇 {user.mention} has been muted")

    @commands.command(name='unmuteuser', description="Unmute a user in voice")
    @commands.has_permissions(administrator=True)
    async def unmuteuser(self, ctx, user: discord.Member):
        await user.edit(mute=False)
        await ctx.send(f"🔊 {user.mention} has been unmuted")

    @commands.command(name='deafenuser', description="Deafen a user")
    @commands.has_permissions(administrator=True)
    async def deafenuser(self, ctx, user: discord.Member):
        await user.edit(deafen=True)
        await ctx.send(f"🔇 {user.mention} has been deafened")

    @commands.command(name='undeafenuser', description="Undeafen a user")
    @commands.has_permissions(administrator=True)
    async def undeafenuser(self, ctx, user: discord.Member):
        await user.edit(deafen=False)
        await ctx.send(f"🔊 {user.mention} has been undeafened")

    @commands.command(name='kickuser', description="Kick a user")
    @commands.has_permissions(administrator=True)
    async def kickuser(self, ctx, user: discord.Member):
        await user.kick()
        await ctx.send(f"👢 {user.mention} has been kicked")

    @commands.command(name='banuser', description="Ban a user")
    @commands.has_permissions(administrator=True)
    async def banuser(self, ctx, user: discord.User):
        await ctx.guild.ban(user)
        await ctx.send(f"🚫 {user.mention} has been banned")

    @commands.command(name='unbanuser', description="Unban a user")
    @commands.has_permissions(administrator=True)
    async def unbanuser(self, ctx, user: discord.User):
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user.mention} has been unbanned")

    @commands.command(name='warnuser', description="Warn a user")
    @commands.has_permissions(administrator=True)
    async def warnuser(self, ctx, user: discord.Member):
        config = self._get_cfg(ctx.guild.id)
        config.setdefault('warnings', {})
        config['warnings'][str(user.id)] = config['warnings'].get(str(user.id), 0) + 1
        self._save_cfg(ctx.guild.id, config)
        await ctx.send(f"⚠️ {user.mention} has been warned (Warnings: {config['warnings'][str(user.id)]})")

    @commands.command(name='timeoutuser', description="Timeout a user")
    @commands.has_permissions(administrator=True)
    async def timeoutuser(self, ctx, user: discord.Member, seconds: int):
        await user.edit(timeout=discord.utils.utcnow() + timedelta(seconds=seconds))
        await ctx.send(f"⏱️ {user.mention} has been timed out for {seconds} seconds")

    @commands.command(name='removetimeout', description="Remove timeout from user")
    @commands.has_permissions(administrator=True)
    async def removetimeout(self, ctx, user: discord.Member):
        await user.edit(timeout=None)
        await ctx.send(f"✅ Timeout removed from {user.mention}")

    @commands.command(name='softban', description="Softban a user")
    @commands.has_permissions(administrator=True)
    async def softban(self, ctx, user: discord.User):
        await ctx.guild.ban(user)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user.mention} has been softbanned")

    @commands.command(name='purge', description="Delete messages")
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, amount: int):
        deleted = await ctx.channel.purge(limit=min(amount, 1000))
        await ctx.send(f"🗑️ Deleted {len(deleted)} messages", delete_after=5)

    @commands.command(name='clearwarnings', description="Clear user warnings")
    @commands.has_permissions(administrator=True)
    async def clearwarnings(self, ctx, user: discord.User):
        config = self._get_cfg(ctx.guild.id)
        if config.get('warnings', {}).get(str(user.id)):
            config['warnings'][str(user.id)] = 0
            self._save_cfg(ctx.guild.id, config)
        await ctx.send(f"✅ Warnings cleared for {user.mention}")

    # ============ SECURITY ============
    @commands.command(name='securityreport', description="Generate security report")
    @commands.has_permissions(administrator=True)
    async def securityreport(self, ctx):
        embed = branded_embed(title="Server Security Report", color="info")
        embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
        embed.add_field(name="Bots", value=len([m for m in ctx.guild.members if m.bot]), inline=True)
        embed.add_field(name="Roles", value=len(ctx.guild.roles), inline=True)
        embed.add_field(name="Channels", value=len(ctx.guild.channels), inline=True)
        embed.add_field(name="Verification", value=ctx.guild.verification_level, inline=True)
        await ctx.send(embed=embed)

    @commands.command(name='enableverification', description="Enable 2FA verification")
    @commands.has_permissions(administrator=True)
    async def enableverification(self, ctx): await self._toggle(ctx, 'twoFactorAuth', "2FA verification enabled")

    @commands.command(name='disableverification', description="Disable 2FA verification")
    @commands.has_permissions(administrator=True)
    async def disableverification(self, ctx): await self._toggle(ctx, 'twoFactorAuth', "2FA verification disabled", value=False)

    @commands.command(name='enablecaptcha', description="Enable CAPTCHA on join")
    @commands.has_permissions(administrator=True)
    async def enablecaptcha(self, ctx): await self._toggle(ctx, 'captchaEnabled', "CAPTCHA enabled on join")

    @commands.command(name='disablecaptcha', description="Disable CAPTCHA")
    @commands.has_permissions(administrator=True)
    async def disablecaptcha(self, ctx): await self._toggle(ctx, 'captchaEnabled', "CAPTCHA disabled", value=False)

    @commands.command(name='requireinvite', description="Require invite to join")
    @commands.has_permissions(administrator=True)
    async def requireinvite(self, ctx): await self._toggle(ctx, 'inviteOnly', "Invite-only mode enabled")

    @commands.command(name='enableauditlogs', description="Enable audit logs")
    @commands.has_permissions(administrator=True)
    async def enableauditlogs(self, ctx): await self._toggle(ctx, 'auditLogsEnabled', "Audit logs enabled")

    @commands.command(name='enableantialts', description="Detect alt accounts")
    @commands.has_permissions(administrator=True)
    async def enableantialts(self, ctx): await self._toggle(ctx, 'antiAlts', "Alt account detection enabled")

    @commands.command(name='enablesuspiciousdetection', description="Detect suspicious activity")
    @commands.has_permissions(administrator=True)
    async def enablesuspiciousdetection(self, ctx): await self._toggle(ctx, 'suspiciousDetection', "Suspicious detection enabled")

    # ============ LOGGING ============
    @commands.command(name='viewlogs', description="View audit logs")
    @commands.has_permissions(administrator=True)
    async def viewlogs(self, ctx):
        async for entry in ctx.guild.audit_logs(limit=10):
            embed = branded_embed(
                title=f"Audit Log: {entry.action.name}",
                description=f"User: {entry.user}\nTarget: {entry.target}\nReason: {entry.reason}",
                color="info",
            )
            await ctx.send(embed=embed)

    @commands.command(name='setlogchannel', description="Set logging channel")
    @commands.has_permissions(administrator=True)
    async def setlogchannel(self, ctx, channel: discord.TextChannel):
        await self._set_value(ctx, 'logChannel', channel.id, f"Log channel set to {channel.mention}")

    @commands.command(name='logmessagedeletes', description="Log deleted messages")
    @commands.has_permissions(administrator=True)
    async def logmessagedeletes(self, ctx): await self._toggle(ctx, 'logDeletes', "Message deletion logging enabled")

    @commands.command(name='logmessageedits', description="Log edited messages")
    @commands.has_permissions(administrator=True)
    async def logmessageedits(self, ctx): await self._toggle(ctx, 'logEdits', "Message edit logging enabled")

    @commands.command(name='loguserjoins', description="Log user joins")
    @commands.has_permissions(administrator=True)
    async def loguserjoins(self, ctx): await self._toggle(ctx, 'logJoins', "User join logging enabled")

    @commands.command(name='loguserleaves', description="Log user leaves")
    @commands.has_permissions(administrator=True)
    async def loguserleaves(self, ctx): await self._toggle(ctx, 'logLeaves', "User leave logging enabled")

    @commands.command(name='logrolecreates', description="Log role creation")
    @commands.has_permissions(administrator=True)
    async def logrolecreates(self, ctx): await self._toggle(ctx, 'logRoleCreates', "Role creation logging enabled")

    @commands.command(name='logrolechanges', description="Log role changes")
    @commands.has_permissions(administrator=True)
    async def logrolechanges(self, ctx): await self._toggle(ctx, 'logRoleChanges', "Role change logging enabled")

    @commands.command(name='logchannelcreates', description="Log channel creation")
    @commands.has_permissions(administrator=True)
    async def logchannelcreates(self, ctx): await self._toggle(ctx, 'logChannelCreates', "Channel creation logging enabled")

    @commands.command(name='logchannelchanges', description="Log channel changes")
    @commands.has_permissions(administrator=True)
    async def logchannelchanges(self, ctx): await self._toggle(ctx, 'logChannelChanges', "Channel change logging enabled")

    @commands.command(name='disablealllogging', description="Disable all logging")
    @commands.has_permissions(administrator=True)
    async def disablealllogging(self, ctx):
        config = self._get_cfg(ctx.guild.id)
        for key in ['logDeletes', 'logEdits', 'logJoins', 'logLeaves', 'logRoleCreates', 'logRoleChanges', 'logChannelCreates', 'logChannelChanges']:
            config[key] = False
        self._save_cfg(ctx.guild.id, config)
        await ctx.send("❌ All logging disabled")

    @commands.command(name='message', description="Toggle ticket message deletion")
    @commands.has_permissions(administrator=True)
    async def message(self, ctx, value: str):
        config = self._get_cfg(ctx.guild.id)
        if value.lower() in ["true", "on", "yes", "enable"]:
            config['deleteTicketMessage'] = True
            config.setdefault('ticketChannel', ctx.channel.id)
            self._save_cfg(ctx.guild.id, config)
            channel = self.bot.get_channel(config['ticketChannel'])
            channel_name = channel.mention if channel else 'this channel'
            await ctx.send(f"✅ Ticket message deletion enabled for {channel_name}")
        elif value.lower() in ["false", "off", "no", "disable"]:
            config['deleteTicketMessage'] = False
            self._save_cfg(ctx.guild.id, config)
            await ctx.send("❌ Ticket message deletion disabled")
        else:
            await ctx.send("Usage: ?message true|false")

    @commands.command(name='ticketchannel', description="Set ticket channel")
    @commands.has_permissions(administrator=True)
    async def ticketchannel(self, ctx, channel: discord.TextChannel):
        await self._set_value(ctx, 'ticketChannel', channel.id, f"Ticket channel set to {channel.mention}")

    @commands.command(name='setminaccountage', description="Set minimum account age")
    @commands.has_permissions(administrator=True)
    async def setminaccountage(self, ctx, days: int):
        await self._set_value(ctx, 'minAccountAge', days * 86400, f"Minimum account age set to {days} days")

    @commands.command(name='setnewmemberwait', description="Set waiting period for new members")
    @commands.has_permissions(administrator=True)
    async def setnewmemberwait(self, ctx, minutes: int):
        await self._set_value(ctx, 'newMemberWait', minutes * 60, f"New members must wait {minutes} minutes")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        config = getConfig(message.guild.id)
        if not config.get('deleteTicketMessage', False):
            return
        ticket_channel = config.get('ticketChannel')
        if ticket_channel and message.channel.id == ticket_channel:
            try:
                await message.delete()
            except (discord.Forbidden, discord.HTTPException):
                pass

    @commands.command(name="viewall", aliases=["fixperms"], description="Reset @everyone to safe perms + fix all channels")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def viewall(self, ctx):
        msg = await ctx.send("Fixing permissions...")
        count = 0

        try:
            perms = discord.Permissions(
                create_instant_invite=True,
                read_messages=True,
                send_messages=True,
                read_message_history=True,
                view_channel=True,
                connect=True,
                speak=True,
                use_voice_activation=True,
                change_nickname=True,
            )
            await ctx.guild.default_role.edit(permissions=perms)
            count += 1
        except Exception as e:
            await ctx.send(f"Failed to fix @everyone role: {e}")

        for channel in ctx.guild.channels:
            try:
                for target, overwrite in channel.overwrites.items():
                    overwrite.read_messages = None
                    overwrite.read_message_history = None
                    overwrite.view_channel = None
                    await channel.set_permissions(target, overwrite=overwrite)
                    count += 1
            except Exception:
                pass

        await msg.edit(content=f"Done! @everyone reset to safe perms + {count} channel overrides cleared.")


async def setup(bot):
    await bot.add_cog(MegaProtectionCog(bot))

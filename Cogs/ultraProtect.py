import time
import discord
from discord.ext import commands
from discord import AuditLogAction
from Tools.utils import getConfig, updateConfig
from Tools.logMessage import sendLogMessage
from Tools.style import branded_embed, COLORS, BRAND_NAME, VERSION


class PanelView(discord.ui.View):
    def __init__(self, cog, guild_id):
        super().__init__(timeout=300)
        self.cog = cog
        self.guild_id = guild_id
        self._build_buttons()

    def _get_cfg(self):
        return getConfig(self.guild_id)

    def _save_cfg(self, data):
        updateConfig(self.guild_id, data)

    def _build_buttons(self):
        config = self._get_cfg()
        features = [
            ("botProtection", "Bot Protect", "🤖"),
            ("staffProtection", "Staff Protect", "👮"),
            ("nukeProtection", "Anti Channel Nuke", "📋"),
            ("roleNukeProtection", "Anti Role Nuke", "🎭"),
            ("memberNukeProtection", "Anti Member Nuke", "👤"),
            ("webhookNukeProtection", "Anti Webhook Nuke", "🪝"),
            ("emojiNukeProtection", "Anti Emoji Nuke", "😀"),
            ("stickerNukeProtection", "Anti Sticker Nuke", "🖼️"),
            ("antiSpam", "Anti Spam", "📩"),
            ("antiProfanity", "Anti Profanity", "🤬"),
            ("antiNudity", "Anti Nudity", "🔞"),
            ("antiBot", "Anti Bot", "🤖"),
        ]
        for key, label, emoji in features:
            enabled = config.get(key, False)
            btn = discord.ui.Button(
                style=discord.ButtonStyle.success if enabled else discord.ButtonStyle.secondary,
                label=f"{emoji} {label}",
                custom_id=key,
                row=len(self.children) // 3,
            )
            btn.callback = self._make_callback(key, label, emoji)
            self.add_item(btn)

    def _make_callback(self, key, label, emoji):
        async def callback(interaction: discord.Interaction):
            if not interaction.user.guild_permissions.administrator:
                return await interaction.response.send_message("You need admin permissions.", ephemeral=True)
            config = self._get_cfg()
            current = config.get(key, False)
            config[key] = not current
            self._save_cfg(config)
            embed = self.cog._build_panel_embed(self.guild_id)
            await interaction.response.edit_message(embed=embed, view=PanelView(self.cog, self.guild_id))
        return callback


class UltraProtectCog(commands.Cog, name="Ultra Protection"):
    def __init__(self, bot):
        self.bot = bot
        self.ban_tracker = {}
        self.last_action = {}

    def _get_config(self, guild_id):
        return getConfig(guild_id)

    def _save_config(self, guild_id, data):
        updateConfig(guild_id, data)

    def _build_panel_embed(self, guild_id):
        config = self._get_config(guild_id)
        embed = branded_embed(
            title=f"{BRAND_NAME} - Panneau de Contrôle",
            description="Cliquez sur les boutons pour activer/désactiver les protections.",
            color="primary",
        )
        bot_protect = config.get("botProtection", False)
        staff_protect = config.get("staffProtection", False)
        embed.add_field(
            name="🤖 Protection des Bots",
            value="✅ Activée" if bot_protect else "❌ Désactivée",
            inline=True,
        )
        embed.add_field(
            name="👮 Protection du Staff",
            value="✅ Activée" if staff_protect else "❌ Désactivée",
            inline=True,
        )
        bot_role_id = config.get("botProtectRole")
        if bot_role_id:
            role = None
            import requests
            try:
                guild = self.bot.get_guild(guild_id)
                if guild:
                    role = guild.get_role(bot_role_id)
            except:
                pass
            embed.add_field(
                name="🎯 Rôle Bots Autorisés",
                value=role.mention if role else f"ID: {bot_role_id}",
                inline=True,
            )
        else:
            embed.add_field(name="🎯 Rôle Bots Autorisés", value="Non défini", inline=True)

        embed.add_field(name="📋 Anti Channel Nuke", value="✅" if config.get("nukeProtection") else "❌", inline=True)
        embed.add_field(name="🎭 Anti Role Nuke", value="✅" if config.get("roleNukeProtection") else "❌", inline=True)
        embed.add_field(name="👤 Anti Member Nuke", value="✅" if config.get("memberNukeProtection") else "❌", inline=True)
        embed.add_field(name="🪝 Anti Webhook Nuke", value="✅" if config.get("webhookNukeProtection") else "❌", inline=True)
        embed.add_field(name="😀 Anti Emoji Nuke", value="✅" if config.get("emojiNukeProtection") else "❌", inline=True)
        embed.add_field(name="🖼️ Anti Sticker Nuke", value="✅" if config.get("stickerNukeProtection") else "❌", inline=True)
        embed.add_field(name="📩 Anti Spam", value="✅" if config.get("antiSpam") else "❌", inline=True)
        embed.add_field(name="🤬 Anti Profanity", value="✅" if config.get("antiProfanity") else "❌", inline=True)
        embed.add_field(name="🔞 Anti Nudité", value="✅" if config.get("antiNudity") else "❌", inline=True)
        embed.add_field(name="🤖 Anti Bot", value="✅" if config.get("antiBot") else "❌", inline=True)

        embed.add_field(
            name="⚙️ Règles Staff Protection",
            value="• 2 bans/heure → kick\n• 3 kicks/heure → kick\n• Auto-assignation rôle → kick\n• Suppression salon → kick",
            inline=False,
        )
        embed.set_footer(text=f"{BRAND_NAME} v{VERSION} | Panel interactif")
        return embed

    def _is_trusted(self, guild, member, config):
        if member is None:
            return False
        if member.id == guild.owner_id:
            return True
        if member.id == self.bot.user.id:
            return True
        trusted = config.get("whitelist", [])
        return member.id in trusted

    def _is_bot_without_role(self, guild, member, config):
        if member is None:
            return False
        if not getattr(member, 'bot', False):
            return False
        if self._is_trusted(guild, member, config):
            return False
        if not isinstance(member, discord.Member):
            return True
        bot_role_id = config.get("botProtectRole")
        if bot_role_id:
            bot_role = guild.get_role(bot_role_id)
            if bot_role and bot_role in member.roles:
                return False
        return True

    def _is_staff(self, member):
        if member is None:
            return False
        if not isinstance(member, discord.Member):
            return False
        return (member.guild_permissions.administrator
                or member.guild_permissions.kick_members
                or member.guild_permissions.ban_members)

    def _is_external(self, member):
        if member is None:
            return True
        if isinstance(member, discord.Member):
            return False
        return True

    async def _get_audit_entry(self, guild, action):
        try:
            async for entry in guild.audit_logs(action=action, limit=5):
                return entry
        except Exception:
            return None

    async def _send_log(self, event, config, embed):
        channel_id = config.get("logChannel")
        if not channel_id or channel_id is True or channel_id == 1:
            return
        await sendLogMessage(self, event=event, channel=channel_id, embed=embed)

    async def _ban_member(self, guild, member, reason):
        try:
            if guild.me.guild_permissions.ban_members:
                await guild.ban(member, reason=reason, delete_message_days=1)
                return True
        except Exception:
            pass
        return False

    async def _kick_member(self, guild, member, reason):
        try:
            if guild.me.guild_permissions.kick_members:
                await member.kick(reason=reason)
                return True
        except Exception:
            pass
        return False

    @commands.command(name="panel", aliases=["p"])
    @commands.has_permissions(administrator=True)
    async def panel(self, ctx):
        embed = self._build_panel_embed(ctx.guild.id)
        view = PanelView(self, ctx.guild.id)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="setbotrole", aliases=["sbr"])
    @commands.has_permissions(administrator=True)
    async def setbotrole(self, ctx, role: discord.Role):
        config = self._get_config(ctx.guild.id)
        config["botProtectRole"] = role.id
        self._save_config(ctx.guild.id, config)
        embed = branded_embed(description=f"Rôle autorisé pour les bots : {role.mention}", color="success")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        config = self._get_config(guild.id)
        staff_protect = config.get("staffProtection", False)
        bot_protect = config.get("botProtection", False)
        if not staff_protect and not bot_protect:
            return
        entry = await self._get_audit_entry(guild, AuditLogAction.ban)
        if not entry or not entry.user:
            return
        executor = entry.user
        if self._is_external(executor) and not self._is_trusted(guild, executor, config):
            reason = "BLOCKED: External application attempted to ban a member"
            banned = await self._ban_member(guild, executor, reason)
            embed = branded_embed(
                title="External App Blocked",
                description=f"**Entity:** {executor} (`{getattr(executor, 'id', '?')}`)\n**Action:** Banned `{user}`\n**Reason:** External app/ webhook banned a member",
                color="error",
            )
            embed.add_field(name="Banned", value="Yes" if banned else "Failed", inline=True)
            await self._send_log(guild, config, embed)
            return
        if bot_protect and getattr(executor, 'bot', False):
            if self._is_bot_without_role(guild, executor, config):
                reason = "BOT AUTO-BAN: Unauthorized bot attempted to ban a member"
                banned = await self._ban_member(guild, executor, reason)
                embed = branded_embed(
                    title="Bot Auto-Banned",
                    description=f"**Bot:** {executor} (`{executor.id}`)\n**Action:** Banned `{user}`\n**Reason:** Unauthorized bot banned a member",
                    color="error",
                )
                embed.add_field(name="Banned", value="Yes" if banned else "Failed", inline=True)
                await self._send_log(guild, config, embed)
        if staff_protect and self._is_staff(executor) and not self._is_trusted(guild, executor, config):
            now = time.time()
            guild_tracker = self.ban_tracker.setdefault(guild.id, {})
            user_bans = guild_tracker.setdefault(executor.id, [])
            user_bans.append(now)
            guild_tracker[executor.id] = [t for t in user_bans if now - t <= 3600]
            ban_count = len(guild_tracker[executor.id])
            if ban_count >= 2:
                reason = f"STAFF PROTECTION: Banned {ban_count} members in 1 hour (limit: 2)"
                kicked = await self._kick_member(guild, executor, reason)
                embed = branded_embed(
                    title="Staff Kicked - Ban Abuse",
                    description=f"**Staff:** {executor} (`{executor.id}`)\n**Bans in 1h:** {ban_count}\n**Action:** Kicked for ban abuse",
                    color="error",
                )
                embed.add_field(name="Kicked", value="Yes" if kicked else "Failed", inline=True)
                await self._send_log(guild, config, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        config = self._get_config(guild.id)
        staff_protect = config.get("staffProtection", False)
        bot_protect = config.get("botProtection", False)
        if not staff_protect and not bot_protect:
            return
        entry = await self._get_audit_entry(guild, AuditLogAction.kick)
        if not entry or not entry.user:
            return
        executor = entry.user
        if self._is_external(executor) and not self._is_trusted(guild, executor, config):
            reason = "BLOCKED: External application kicked a member"
            banned = await self._ban_member(guild, executor, reason)
            embed = branded_embed(
                title="External App Blocked",
                description=f"**Entity:** {executor} (`{getattr(executor, 'id', '?')}`)\n**Action:** Kicked `{member}`\n**Reason:** External app/webhook kicked a member",
                color="error",
            )
            embed.add_field(name="Banned", value="Yes" if banned else "Failed", inline=True)
            await self._send_log(guild, config, embed)
            return
        if bot_protect and getattr(executor, 'bot', False):
            if self._is_bot_without_role(guild, executor, config):
                reason = "BOT AUTO-BAN: Unauthorized bot kicked a member"
                banned = await self._ban_member(guild, executor, reason)
                embed = branded_embed(
                    title="Bot Auto-Banned",
                    description=f"**Bot:** {executor} (`{executor.id}`)\n**Action:** Kicked `{member}`\n**Reason:** Unauthorized bot kicked a member",
                    color="error",
                )
                embed.add_field(name="Banned", value="Yes" if banned else "Failed", inline=True)
                await self._send_log(guild, config, embed)
        if staff_protect and self._is_staff(executor) and not self._is_trusted(guild, executor, config):
            now = time.time()
            guild_tracker = self.ban_tracker.setdefault(guild.id, {})
            user_bans = guild_tracker.setdefault(executor.id, [])
            user_bans.append(now)
            guild_tracker[executor.id] = [t for t in user_bans if now - t <= 3600]
            kick_count = len(guild_tracker[executor.id])
            if kick_count >= 3:
                reason = f"STAFF PROTECTION: Kicked {kick_count} members in 1 hour (limit: 3)"
                kicked = await self._kick_member(guild, executor, reason)
                embed = branded_embed(
                    title="Staff Kicked - Kick Abuse",
                    description=f"**Staff:** {executor} (`{executor.id}`)\n**Kicks in 1h:** {kick_count}\n**Action:** Kicked for kick abuse",
                    color="error",
                )
                embed.add_field(name="Kicked", value="Yes" if kicked else "Failed", inline=True)
                await self._send_log(guild, config, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles:
            return
        guild = after.guild
        config = self._get_config(guild.id)
        staff_protect = config.get("staffProtection", False)
        bot_protect = config.get("botProtection", False)
        if not staff_protect and not bot_protect:
            return
        added_roles = [r for r in after.roles if r not in before.roles]
        if not added_roles:
            return
        entry = await self._get_audit_entry(guild, AuditLogAction.member_role_update)
        if not entry or not entry.user:
            return
        executor = entry.user
        if self._is_external(executor) and not self._is_trusted(guild, executor, config):
            reason = "BLOCKED: External application modified roles"
            banned = await self._ban_member(guild, executor, reason)
            embed = branded_embed(
                title="External App Blocked",
                description=f"**Entity:** {executor} (`{getattr(executor, 'id', '?')}`)\n**Action:** Role modification on `{after}`\n**Reason:** External app/webhook modified roles",
                color="error",
            )
            embed.add_field(name="Banned", value="Yes" if banned else "Failed", inline=True)
            await self._send_log(guild, config, embed)
            return
        if bot_protect and getattr(executor, 'bot', False):
            if self._is_bot_without_role(guild, executor, config):
                reason = "BOT AUTO-BAN: Unauthorized bot modified roles"
                banned = await self._ban_member(guild, executor, reason)
                embed = branded_embed(
                    title="Bot Auto-Banned",
                    description=f"**Bot:** {executor} (`{executor.id}`)\n**Action:** Role modification on `{after}`\n**Reason:** Unauthorized bot modified roles",
                    color="error",
                )
                embed.add_field(name="Banned", value="Yes" if banned else "Failed", inline=True)
                await self._send_log(guild, config, embed)
        if staff_protect and not self._is_trusted(guild, executor, config):
            if executor.id == after.id:
                role_names = ", ".join([r.name for r in added_roles])
                reason = f"STAFF PROTECTION: Added role(s) to self: {role_names}"
                kicked = await self._kick_member(guild, executor, reason)
                embed = branded_embed(
                    title="Staff Kicked - Self Role Add",
                    description=f"**Staff:** {executor} (`{executor.id}`)\n**Roles added:** {role_names}\n**Action:** Kicked for self-role assignment",
                    color="error",
                )
                embed.add_field(name="Kicked", value="Yes" if kicked else "Failed", inline=True)
                await self._send_log(guild, config, embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        config = self._get_config(guild.id)
        staff_protect = config.get("staffProtection", False)
        bot_protect = config.get("botProtection", False)
        nuke_protect = config.get("nukeProtection", False)
        if not staff_protect and not bot_protect and not nuke_protect:
            return
        entry = await self._get_audit_entry(guild, AuditLogAction.channel_delete)
        if not entry or not entry.user:
            return
        executor = entry.user
        if self._is_external(executor) and not self._is_trusted(guild, executor, config):
            reason = "BLOCKED: External application deleted a channel"
            banned = await self._ban_member(guild, executor, reason)
            embed = branded_embed(
                title="External App Blocked",
                description=f"**Entity:** {executor} (`{getattr(executor, 'id', '?')}`)\n**Action:** Deleted channel `{channel.name}`\n**Reason:** External app/webhook deleted a channel",
                color="error",
            )
            embed.add_field(name="Banned", value="Yes" if banned else "Failed", inline=True)
            await self._send_log(guild, config, embed)
            return
        if bot_protect and getattr(executor, 'bot', False):
            if self._is_bot_without_role(guild, executor, config):
                reason = "BOT AUTO-BAN: Unauthorized bot deleted a channel"
                banned = await self._ban_member(guild, executor, reason)
                embed = branded_embed(
                    title="Bot Auto-Banned",
                    description=f"**Bot:** {executor} (`{executor.id}`)\n**Action:** Deleted channel `{channel.name}`\n**Reason:** Unauthorized bot deleted a channel",
                    color="error",
                )
                embed.add_field(name="Banned", value="Yes" if banned else "Failed", inline=True)
                await self._send_log(guild, config, embed)
        if staff_protect and self._is_staff(executor) and not self._is_trusted(guild, executor, config):
            now = time.time()
            last = self.last_action.get(guild.id, {}).get(executor.id, 0)
            if now - last < 5:
                return
            self.last_action.setdefault(guild.id, {})[executor.id] = now
            reason = "STAFF PROTECTION: Deleted a channel"
            kicked = await self._kick_member(guild, executor, reason)
            embed = branded_embed(
                title="Staff Kicked - Channel Deletion",
                description=f"**Staff:** {executor} (`{executor.id}`)\n**Channel deleted:** `{channel.name}`\n**Action:** Kicked for channel deletion",
                color="error",
            )
            embed.add_field(name="Kicked", value="Yes" if kicked else "Failed", inline=True)
            await self._send_log(guild, config, embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        guild = role.guild
        config = self._get_config(guild.id)
        staff_protect = config.get("staffProtection", False)
        bot_protect = config.get("botProtection", False)
        role_protect = config.get("roleNukeProtection", False)
        if not staff_protect and not bot_protect and not role_protect:
            return
        entry = await self._get_audit_entry(guild, AuditLogAction.role_delete)
        if not entry or not entry.user:
            return
        executor = entry.user
        if self._is_external(executor) and not self._is_trusted(guild, executor, config):
            reason = "BLOCKED: External application deleted a role"
            banned = await self._ban_member(guild, executor, reason)
            embed = branded_embed(
                title="External App Blocked",
                description=f"**Entity:** {executor} (`{getattr(executor, 'id', '?')}`)\n**Action:** Deleted role `{role.name}`\n**Reason:** External app/webhook deleted a role",
                color="error",
            )
            embed.add_field(name="Banned", value="Yes" if banned else "Failed", inline=True)
            await self._send_log(guild, config, embed)
            return
        if bot_protect and getattr(executor, 'bot', False):
            if self._is_bot_without_role(guild, executor, config):
                reason = "BOT AUTO-BAN: Unauthorized bot deleted a role"
                banned = await self._ban_member(guild, executor, reason)
                embed = branded_embed(
                    title="Bot Auto-Banned",
                    description=f"**Bot:** {executor} (`{executor.id}`)\n**Action:** Deleted role `{role.name}`\n**Reason:** Unauthorized bot deleted a role",
                    color="error",
                )
                embed.add_field(name="Banned", value="Yes" if banned else "Failed", inline=True)
                await self._send_log(guild, config, embed)
        if staff_protect and self._is_staff(executor) and not self._is_trusted(guild, executor, config):
            now = time.time()
            last = self.last_action.get(guild.id, {}).get(executor.id, 0)
            if now - last < 5:
                return
            self.last_action.setdefault(guild.id, {})[executor.id] = now
            reason = "STAFF PROTECTION: Deleted a role"
            kicked = await self._kick_member(guild, executor, reason)
            embed = branded_embed(
                title="Staff Kicked - Role Deletion",
                description=f"**Staff:** {executor} (`{executor.id}`)\n**Role deleted:** `{role.name}`\n**Action:** Kicked for role deletion",
                color="error",
            )
            embed.add_field(name="Kicked", value="Yes" if kicked else "Failed", inline=True)
            await self._send_log(guild, config, embed)


async def setup(bot):
    await bot.add_cog(UltraProtectCog(bot))

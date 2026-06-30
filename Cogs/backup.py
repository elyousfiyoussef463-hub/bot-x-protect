import discord
from discord.ext import commands
from datetime import datetime
import json
import os
from Tools.utils import getConfig, updateConfig
from Tools.style import branded_embed, COLORS

class BackupCog(commands.Cog, name="Server Backup and Restore"):
    def __init__(self, bot):
        self.bot = bot
        self.backup_folder = "backups"
        if not os.path.exists(self.backup_folder):
            os.makedirs(self.backup_folder)

    def get_backup_path(self, guild_id):
        return os.path.join(self.backup_folder, f"backup_{guild_id}.json")

    async def create_backup(self, guild):
        try:
            backup_data = {
                "guild_name": guild.name,
                "guild_id": guild.id,
                "timestamp": datetime.now().isoformat(),
                "roles": [],
                "channels": [],
                "members": [],
            }

            for role in guild.roles:
                if role == guild.default_role:
                    continue
                role_data = {
                    "id": role.id,
                    "name": role.name,
                    "color": role.color.value,
                    "hoist": role.hoist,
                    "mentionable": role.mentionable,
                    "permissions": role.permissions.value,
                    "position": role.position,
                }
                backup_data["roles"].append(role_data)

            for channel in guild.channels:
                channel_data = {
                    "id": channel.id,
                    "name": channel.name,
                    "type": str(channel.type),
                    "position": channel.position,
                    "topic": getattr(channel, "topic", None),
                    "nsfw": getattr(channel, "nsfw", False),
                    "slowmode_delay": getattr(channel, "slowmode_delay", 0),
                    "permissions": {},
                }

                for target, overwrite in channel.overwrites.items():
                    if isinstance(target, discord.Role):
                        channel_data["permissions"][f"role_{target.id}"] = {
                            "allow": overwrite.pair()[0].value,
                            "deny": overwrite.pair()[1].value,
                        }
                    elif isinstance(target, discord.Member):
                        channel_data["permissions"][f"member_{target.id}"] = {
                            "allow": overwrite.pair()[0].value,
                            "deny": overwrite.pair()[1].value,
                        }

                backup_data["channels"].append(channel_data)

            backup_data["member_count"] = guild.member_count

            backup_path = self.get_backup_path(guild.id)
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=4, ensure_ascii=False)

            return True, backup_data
        except Exception as e:
            return False, str(e)

    async def restore_backup(self, guild, backup_data):
        try:
            restored = {"roles": 0, "channels": 0, "permissions": 0}

            for role_data in backup_data.get("roles", []):
                try:
                    existing_role = discord.utils.get(guild.roles, name=role_data["name"])
                    if not existing_role:
                        await guild.create_role(
                            name=role_data["name"],
                            color=discord.Color(role_data["color"]),
                            hoist=role_data["hoist"],
                            mentionable=role_data["mentionable"],
                            permissions=discord.Permissions(role_data["permissions"]),
                        )
                        restored["roles"] += 1
                except Exception as e:
                    print(f"Failed to restore role {role_data['name']}: {e}")

            for channel_data in backup_data.get("channels", []):
                try:
                    existing_channel = discord.utils.get(guild.channels, name=channel_data["name"])
                    if not existing_channel:
                        if channel_data["type"] == "text":
                            await guild.create_text_channel(
                                name=channel_data["name"],
                                topic=channel_data.get("topic"),
                                nsfw=channel_data.get("nsfw", False),
                                slowmode_delay=channel_data.get("slowmode_delay", 0),
                            )
                        elif channel_data["type"] == "voice":
                            await guild.create_voice_channel(name=channel_data["name"])
                        restored["channels"] += 1
                except Exception as e:
                    print(f"Failed to restore channel {channel_data['name']}: {e}")

            return True, restored
        except Exception as e:
            return False, str(e)

    @commands.group(name="backup", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.guild_only()
    async def backup(self, ctx):
        embed = branded_embed(
            title="Backup Commands",
            description="Manage server backups",
            color="info",
        )
        prefix = ctx.prefix
        embed.add_field(name=f"{prefix}backup create", value="Create a server backup", inline=False)
        embed.add_field(name=f"{prefix}backup restore", value="Restore from last backup", inline=False)
        embed.add_field(name=f"{prefix}backup info", value="Show backup info", inline=False)
        await ctx.send(embed=embed)

    @backup.command(name="create")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def backup_create(self, ctx):
        async with ctx.typing():
            success, data = await self.create_backup(ctx.guild)

            if success:
                embed = branded_embed(
                    title="Backup Created",
                    description="Server backup saved successfully!",
                    color="success",
                )
                embed.add_field(name="Timestamp", value=data["timestamp"], inline=False)
                embed.add_field(name="Roles Backed Up", value=str(len(data["roles"])), inline=True)
                embed.add_field(name="Channels Backed Up", value=str(len(data["channels"])), inline=True)
                embed.add_field(name="Members Count", value=str(data["member_count"]), inline=True)
                await ctx.send(embed=embed)
            else:
                embed = branded_embed(
                    title="Backup Failed",
                    description=f"Error: {data}",
                    color="error",
                )
                await ctx.send(embed=embed)

    @backup.command(name="restore")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def backup_restore(self, ctx):
        backup_path = self.get_backup_path(ctx.guild.id)

        if not os.path.exists(backup_path):
            embed = branded_embed(
                title="No Backup Found",
                description="No backup exists for this server.",
                color="error",
            )
            await ctx.send(embed=embed)
            return

        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)

            async with ctx.typing():
                success, restored = await self.restore_backup(ctx.guild, backup_data)

                if success:
                    embed = branded_embed(
                        title="Backup Restored",
                        description="Server restored from backup!",
                        color="success",
                    )
                    embed.add_field(name="Backup Date", value=backup_data["timestamp"], inline=False)
                    embed.add_field(name="Roles Restored", value=str(restored["roles"]), inline=True)
                    embed.add_field(name="Channels Restored", value=str(restored["channels"]), inline=True)
                    await ctx.send(embed=embed)
                else:
                    embed = branded_embed(
                        title="Restore Failed",
                        description=f"Error: {restored}",
                        color="error",
                    )
                    await ctx.send(embed=embed)
        except Exception as e:
            embed = branded_embed(
                title="Error",
                description=f"Failed to restore: {str(e)}",
                color="error",
            )
            await ctx.send(embed=embed)

    @backup.command(name="info")
    @commands.has_permissions(administrator=True)
    async def backup_info(self, ctx):
        backup_path = self.get_backup_path(ctx.guild.id)

        if not os.path.exists(backup_path):
            embed = branded_embed(
                title="No Backup Found",
                description="No backup exists for this server.",
                color="error",
            )
            await ctx.send(embed=embed)
            return

        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)

            embed = branded_embed(
                title="Backup Information",
                description=f"Backup for **{backup_data['guild_name']}**",
                color="info",
            )
            embed.add_field(name="Created", value=backup_data["timestamp"], inline=False)
            embed.add_field(name="Roles", value=str(len(backup_data["roles"])), inline=True)
            embed.add_field(name="Channels", value=str(len(backup_data["channels"])), inline=True)
            embed.add_field(name="Members Count", value=str(backup_data["member_count"]), inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = branded_embed(
                title="Error",
                description=f"Failed to read backup: {str(e)}",
                color="error",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BackupCog(bot))

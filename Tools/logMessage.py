from Tools.utils import getConfig, updateConfig
from Tools.style import branded_embed


async def sendLogMessage(cog, event, channel, embed, messageFile=None):
    if channel is False or channel is None:
        return

    if isinstance(channel, int):
        channel = cog.bot.get_channel(channel)

    if channel is None:
        try:
            guild = event.guild
            channel = await guild.create_text_channel(f"{cog.bot.user.name}-logs")
            perms = channel.overwrites_for(guild.default_role)
            perms.read_messages = False
            await channel.set_permissions(guild.default_role, overwrite=perms)
        except Exception as error:
            err_msg = getattr(error, 'text', str(error))
            err_code = getattr(error, 'code', None)
            if err_code == 50013:
                event_channel = getattr(event, 'channel', None)
                if event_channel:
                    await event_channel.send(f"**Log error :** I cannot create a log channel ({err_msg}).")
            else:
                event_channel = getattr(event, 'channel', None)
                if event_channel:
                    await event_channel.send(err_msg)
            return

        data = getConfig(channel.guild.id)
        data["logChannel"] = channel.id
        updateConfig(channel.guild.id, data)

    await channel.send(embed=embed, file=messageFile)

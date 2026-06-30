import json
import os
import threading
from datetime import datetime, timedelta, timezone

_config_cache = {}
_cache_ttl = timedelta(seconds=5)
_config_lock = threading.Lock()

def _load_config():
    with _config_lock:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)

def _save_config(data):
    with _config_lock:
        tmp = "config.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(tmp, "config.json")

defaultConfig = {
    "prefix": "?",
    "language": "en-US",
    "antiProfanity": True,
    "antiNudity": True,
    "antiSpam": True,
    "allowSpam": [],
    "captcha": False,
    "captchaChannel": False,
    "logChannel": 1,
    "temporaryRole": 1,
    "roleGivenAfterCaptcha": False,
    "deleteTicketMessage": False,
    "ticketChannel": None,
    "minAccountDate": 86400,
    "raidLevel": 1,
    "nukeProtection": False,
    "roleNukeProtection": False,
    "memberNukeProtection": False,
    "webhookNukeProtection": False,
    "emojiNukeProtection": False,
    "stickerNukeProtection": False,
    "protectedChannels": [],
    "protectedRoles": [],
    "whitelist": [],
    "botProtection": False,
    "staffProtection": False,
    "botProtectRole": None,
    "spamWarnCount": 5,
    "spamKickCount": 8,
    "spamWindow": 10
}

def getConfig(guildID):
    guild_key = str(guildID)
    now = datetime.now(timezone.utc)

    if guild_key in _config_cache:
        entry = _config_cache[guild_key]
        if now - entry["time"] < _cache_ttl and entry["time"].tzinfo is not None:
            return entry["data"]

    data = _load_config()
    guilds = data.setdefault("guilds", {})

    if guild_key not in guilds:
        guilds[guild_key] = dict(defaultConfig)
        updateConfig(guildID, dict(defaultConfig))
        _config_cache[guild_key] = {"data": dict(defaultConfig), "time": now}
        return dict(defaultConfig)

    guild_config = guilds[guild_key]
    updated = False
    for key, value in defaultConfig.items():
        if key not in guild_config:
            guild_config[key] = value
            updated = True

    if updated:
        _save_config(data)

    _config_cache[guild_key] = {"data": guild_config, "time": now}
    return guild_config

def updateConfig(guildID, data):
    guild_key = str(guildID)
    raw = _load_config()
    raw.setdefault("guilds", {})[guild_key] = data
    _save_config(raw)
    _config_cache[guild_key] = {"data": data, "time": datetime.now(timezone.utc)}

def invalidateCache(guildID=None):
    if guildID:
        _config_cache.pop(str(guildID), None)
    else:
        _config_cache.clear()

async def getGuildPrefix(bot, message):
    if not message.guild:
        return "?"
    config = getConfig(message.guild.id)
    return config["prefix"]
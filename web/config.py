import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "config.json"), "r", encoding="utf-8") as f:
    _data = json.load(f)

_web = _data.get("web", {})

WEB_CONFIG = {
    "DISCORD_CLIENT_ID": _web.get("DISCORD_CLIENT_ID", "TON_CLIENT_ID"),
    "DISCORD_CLIENT_SECRET": _web.get("DISCORD_CLIENT_SECRET", "TON_CLIENT_SECRET"),
    "DISCORD_REDIRECT_URI": _web.get("DISCORD_REDIRECT_URI", "https://TON_NGROK.ngrok-free.app/callback"),
    "BOT_TOKEN": os.environ.get("BOT_TOKEN", _data.get("token", "")),
    "TARGET_GUILD_ID": _web.get("TARGET_GUILD_ID", "1513003332795498526"),
    "SESSION_SECRET": _web.get("SESSION_SECRET", "change-me-to-a-random-secret"),
    "PORT": _web.get("PORT", 5000),
}

import os
import sys
import json
import secrets
import threading
import requests
from flask import Flask, redirect, request, session, render_template, url_for, jsonify

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web.config import WEB_CONFIG

app = Flask(__name__)
app.secret_key = WEB_CONFIG["SESSION_SECRET"]

DISCORD_API = "https://discord.com/api/v10"
CLIENT_ID = WEB_CONFIG["DISCORD_CLIENT_ID"]
CLIENT_SECRET = WEB_CONFIG["DISCORD_CLIENT_SECRET"]
REDIRECT_URI = WEB_CONFIG.get("DASHBOARD_REDIRECT_URI", "http://localhost:5001/callback")
BOT_TOKEN = WEB_CONFIG["BOT_TOKEN"]

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
BOT_PREFIX = "?"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(data):
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(tmp, CONFIG_PATH)


def get_guild_config(guild_id):
    data = load_config()
    guilds = data.setdefault("guilds", {})
    gid = str(guild_id)
    if gid not in guilds:
        return None
    return guilds[gid]


def update_guild_config(guild_id, new_config):
    data = load_config()
    guilds = data.setdefault("guilds", {})
    guilds[str(guild_id)] = new_config
    save_config(data)


def exchange_code(code):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify guilds",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(f"{DISCORD_API}/oauth2/token", data=data, headers=headers)
    return resp.json()


def get_user(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{DISCORD_API}/users/@me", headers=headers)
    return resp.json()


def get_user_guilds(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{DISCORD_API}/users/@me/guilds", headers=headers)
    return resp.json()


def check_dashboard_access(user_id, guild_id):
    try:
        headers = {"Authorization": f"Bot {BOT_TOKEN}"}
        resp = requests.get(f"{DISCORD_API}/guilds/{guild_id}/members/{user_id}", headers=headers)
        if resp.status_code != 200:
            return False
        member = resp.json()
        member_roles = member.get("roles", [])
        guild_config = get_guild_config(guild_id)
        if not guild_config:
            return False
        whitelist = guild_config.get("whitelist", [])
        if user_id in whitelist:
            return True
        guild_resp = requests.get(f"{DISCORD_API}/guilds/{guild_id}", headers=headers)
        if guild_resp.status_code != 200:
            return False
        guild_data = guild_resp.json()
        if guild_data.get("owner_id") == str(user_id):
            return True
        roles_resp = requests.get(f"{DISCORD_API}/guilds/{guild_id}/roles", headers=headers)
        if roles_resp.status_code != 200:
            return False
        for role in roles_resp.json():
            if role["id"] in member_roles and role.get("permissions", 0) & 0x8:
                return True
        return False
    except Exception:
        return False


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("guilds"))
    return render_template("dashboard_login.html")


@app.route("/login")
def login():
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    params = (
        f"response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=identify%20guilds"
        f"&state={state}"
    )
    return redirect(f"{DISCORD_API}/oauth2/authorize?{params}")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    if not state or state != session.pop("oauth_state", None):
        return "State mismatch", 403
    if not code:
        return "No code", 400
    token_data = exchange_code(code)
    if "access_token" not in token_data:
        return f"Token exchange failed: {token_data}", 400
    session["access_token"] = token_data["access_token"]
    session["refresh_token"] = token_data.get("refresh_token")
    user = get_user(token_data["access_token"])
    if "id" not in user:
        return f"Failed to get user: {user}", 400
    session["user"] = user
    return redirect(url_for("guilds"))


@app.route("/guilds")
def guilds():
    if "user" not in session or "access_token" not in session:
        return redirect(url_for("home"))
    user = session["user"]
    user_guilds = get_user_guilds(session["access_token"])
    admin_guilds = []
    for g in user_guilds:
        perms = int(g.get("permissions", 0))
        if perms & 0x20 or perms & 0x8:
            admin_guilds.append(g)
    return render_template("dashboard_guilds.html", user=user, guilds=admin_guilds)


@app.route("/dashboard/<guild_id>")
def dashboard(guild_id):
    if "user" not in session:
        return redirect(url_for("home"))
    user = session["user"]
    if not check_dashboard_access(user["id"], guild_id):
        return "Access denied. You must be an admin of this server.", 403
    config = get_guild_config(guild_id)
    if not config:
        return "Guild not configured.", 404
    prefix = config.get("prefix", "?")
    try:
        guild_resp = requests.get(
            f"{DISCORD_API}/guilds/{guild_id}",
            headers={"Authorization": f"Bot {BOT_TOKEN}"},
        )
        guild_data = guild_resp.json() if guild_resp.status_code == 200 else {"name": "Unknown", "id": guild_id}
    except Exception:
        guild_data = {"name": "Unknown", "id": guild_id}
    return render_template("dashboard.html", user=user, guild=guild_data, config=config, prefix=prefix)


@app.route("/api/<guild_id>/config", methods=["GET"])
def api_get_config(guild_id):
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    if not check_dashboard_access(session["user"]["id"], guild_id):
        return jsonify({"error": "Access denied"}), 403
    config = get_guild_config(guild_id)
    if not config:
        return jsonify({"error": "Not found"}), 404
    return jsonify(config)


@app.route("/api/<guild_id>/config", methods=["POST"])
def api_update_config(guild_id):
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    if not check_dashboard_access(session["user"]["id"], guild_id):
        return jsonify({"error": "Access denied"}), 403
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    config = get_guild_config(guild_id)
    if not config:
        return jsonify({"error": "Not found"}), 404
    for key, value in data.items():
        if key in ["prefix", "language", "raidLevel", "minAccountDate",
                    "antiProfanity", "antiNudity", "antiSpam", "antiBot",
                    "antiRaid", "captcha", "logs",
                    "nukeProtection", "roleNukeProtection", "memberNukeProtection",
                    "webhookNukeProtection", "emojiNukeProtection", "stickerNukeProtection",
                    "botProtection", "staffProtection", "botProtectRole",
                    "dashboardPort"]:
            config[key] = value
    update_guild_config(guild_id, config)
    return jsonify({"success": True, "config": config})


@app.route("/api/<guild_id>/toggle/<key>", methods=["POST"])
def api_toggle(guild_id, key):
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    if not check_dashboard_access(session["user"]["id"], guild_id):
        return jsonify({"error": "Access denied"}), 403
    config = get_guild_config(guild_id)
    if not config:
        return jsonify({"error": "Not found"}), 404
    if key in config:
        config[key] = not config[key]
    else:
        config[key] = True
    update_guild_config(guild_id, config)
    return jsonify({"success": True, key: config[key]})


@app.route("/api/<guild_id>/stats")
def api_stats(guild_id):
    if "user" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    if not check_dashboard_access(session["user"]["id"], guild_id):
        return jsonify({"error": "Access denied"}), 403
    try:
        headers = {"Authorization": f"Bot {BOT_TOKEN}"}
        guild_resp = requests.get(f"{DISCORD_API}/guilds/{guild_id}", headers=headers)
        guild_data = guild_resp.json() if guild_resp.status_code == 200 else {}
        channels_resp = requests.get(f"{DISCORD_API}/guilds/{guild_id}/channels", headers=headers)
        channels = channels_resp.json() if channels_resp.status_code == 200 else []
        roles_resp = requests.get(f"{DISCORD_API}/guilds/{guild_id}/roles", headers=headers)
        roles = roles_resp.json() if roles_resp.status_code == 200 else []
        return jsonify({
            "name": guild_data.get("name", "Unknown"),
            "member_count": guild_data.get("approximate_member_count", 0) or guild_data.get("member_count", 0),
            "channels": len(channels),
            "roles": len(roles),
            "verification": guild_data.get("verification_level", "none"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


def run_dashboard(port=5001):
    print(f"  Dashboard: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def start_dashboard_thread(port=5001):
    thread = threading.Thread(target=run_dashboard, args=(port,), daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    print("=" * 50)
    print("  [+] EMPIRE-X | PROTECT - Dashboard")
    print("=" * 50)
    print("  http://localhost:5001")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=False)

import os
import sys
import secrets
import requests
from flask import Flask, redirect, request, session, render_template, url_for

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web.config import WEB_CONFIG

app = Flask(__name__)
app.secret_key = WEB_CONFIG["SESSION_SECRET"]

DISCORD_API = "https://discord.com/api/v10"

CLIENT_ID = WEB_CONFIG["DISCORD_CLIENT_ID"]
CLIENT_SECRET = WEB_CONFIG["DISCORD_CLIENT_SECRET"]
REDIRECT_URI = WEB_CONFIG["DISCORD_REDIRECT_URI"]
BOT_TOKEN = WEB_CONFIG["BOT_TOKEN"]
TARGET_GUILD = WEB_CONFIG["TARGET_GUILD_ID"]


def exchange_code(code):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify guilds.join",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(f"{DISCORD_API}/oauth2/token", data=data, headers=headers)
    return resp.json()


def refresh_token(refresh_token):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(f"{DISCORD_API}/oauth2/token", data=data, headers=headers)
    return resp.json()


def get_user(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{DISCORD_API}/users/@me", headers=headers)
    return resp.json()


def add_user_to_guild(user_id, access_token):
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {"access_token": access_token}
    resp = requests.put(
        f"{DISCORD_API}/guilds/{TARGET_GUILD}/members/{user_id}",
        headers=headers,
        json=data,
    )
    return resp.status_code, resp.text


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("terms"))
    return render_template("login.html")


@app.route("/login")
def login():
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    params = (
        f"response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=identify%20guilds.join"
        f"&state={state}"
    )
    return redirect(f"{DISCORD_API}/oauth2/authorize?{params}")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")

    if not state or state != session.pop("oauth_state", None):
        return "State mismatch – CSRF detected.", 403

    if not code:
        return "No code provided.", 400

    token_data = exchange_code(code)
    if "access_token" not in token_data:
        return f"Token exchange failed: {token_data}", 400

    session["access_token"] = token_data["access_token"]
    session["refresh_token"] = token_data.get("refresh_token")

    user = get_user(token_data["access_token"])
    if "id" not in user:
        return f"Failed to get user: {user}", 400

    session["user"] = user
    return redirect(url_for("terms"))


@app.route("/terms")
def terms():
    if "user" not in session:
        return redirect(url_for("home"))
    return render_template("terms.html", user=session["user"])


@app.route("/accept")
def accept():
    if "user" not in session or "access_token" not in session:
        return redirect(url_for("home"))

    user = session["user"]
    user_id = user["id"]
    access_token = session["access_token"]

    status, body = add_user_to_guild(user_id, access_token)

    if status == 201 or status == 204:
        return render_template("success.html", user=user, already_member=False)
    elif status == 409:
        return render_template("success.html", user=user, already_member=True)
    else:
        return f"Failed to add user to guild ({status}): {body}", 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    print("=" * 50)
    print("  WEB PORTAL - Discord OAuth2 + Auto Join")
    print("=" * 50)
    print(f"  Redirect URI: {REDIRECT_URI}")
    print(f"  Target Guild: {TARGET_GUILD}")
    print(f"  Port:         {WEB_CONFIG['PORT']}")
    print("=" * 50)
    print("  Make sure ngrok is running:")
    print("  ngrok http 5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=WEB_CONFIG["PORT"], debug=False)

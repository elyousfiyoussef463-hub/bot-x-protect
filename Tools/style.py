import discord
from datetime import datetime, timezone

VERSION = "1.0"

BRAND_NAME = "[+] EMPIRE-X | PROTECT"
BRAND_ICON = "🛡️"

COLORS = {
    "primary": 0xBE1A1A,
    "dark": 0x0d0d15,
    "accent": 0xff6b6b,
    "success": 0x2ecc71,
    "error": 0xe74c3c,
    "warning": 0xf39c12,
    "info": 0x3498db,
    "captcha_pass": 0x2fa737,
    "captcha_fail": 0xca1616,
    "neutral": 0x95a5a6,
}

def branded_embed(
    title=None,
    description=None,
    color="primary",
    footer_text=None,
    footer_icon=None,
    thumbnail=None,
    image=None,
    timestamp=None,
    author_name=None,
    author_icon=None,
):
    color_val = COLORS.get(color, COLORS["primary"])
    embed = discord.Embed(
        title=title,
        description=description,
        color=color_val,
    )
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if timestamp:
        embed.timestamp = timestamp
    else:
        embed.timestamp = datetime.now(timezone.utc)
    if author_name:
        embed.set_author(name=author_name, icon_url=author_icon)
    if footer_text:
        embed.set_footer(text=footer_text, icon_url=footer_icon)
    else:
        embed.set_footer(
            text=f"{BRAND_NAME} v{VERSION}",
            icon_url=footer_icon,
        )
    return embed


def success_embed(title, description=None):
    return branded_embed(
        title=f"✓ {title}",
        description=description,
        color="success",
    )


def error_embed(title, description=None):
    return branded_embed(
        title=f"✗ {title}",
        description=description,
        color="error",
    )


def warning_embed(title, description=None):
    return branded_embed(
        title=f"⚠ {title}",
        description=description,
        color="warning",
    )


def info_embed(title, description=None):
    return branded_embed(
        title=title,
        description=description,
        color="info",
    )


def captcha_result_embed(passed, description):
    return branded_embed(
        description=description,
        color="captcha_pass" if passed else "captcha_fail",
    )


def user_info_field(embed, member, member_id):
    embed.add_field(
        name="User Information",
        value=f"**Name:** {member}\n**ID:** `{member_id}`",
        inline=False,
    )


def log_embed(title, description, color="primary", fields=None):
    embed = branded_embed(title=title, description=description, color=color)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed


def format_bool(value):
    return "✓ Enabled" if value else "✗ Disabled"

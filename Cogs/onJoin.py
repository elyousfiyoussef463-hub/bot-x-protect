import discord
import random
import string
import Augmentor
import os
import shutil
import asyncio
import time
from discord.ext import commands
from discord.utils import get
from PIL import ImageFont, ImageDraw, Image
from Tools.utils import getConfig
from Tools.logMessage import sendLogMessage
from Tools.style import branded_embed, COLORS

class OnJoinCog(commands.Cog, name="on join"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        data = getConfig(member.guild.id)
        logChannel = data["logChannel"]
        captchaChannelId = data.get("captchaChannel")
        captchaChannel = self.bot.get_channel(captchaChannelId) if captchaChannelId else None
        if not captchaChannel:
            return

        memberTime = f"{member.joined_at.year}-{member.joined_at.month}-{member.joined_at.day} {member.joined_at.hour}:{member.joined_at.minute}:{member.joined_at.second}"

        if data["minAccountDate"] is not False:
            minAge = data["minAccountDate"]
            accountAge = time.time() - member.created_at.timestamp()
            if accountAge < minAge:
                minAccountHours = minAge / 3600
                embed = branded_embed(
                    title=self.bot.translate.msg(member.guild.id, "onJoin", "YOU_HAVE_BEEN_KICKED").format(member.guild.name),
                    description=self.bot.translate.msg(member.guild.id, "onJoin", "MIN_ACCOUNT_AGE_KICK_REASON").format(minAccountHours),
                    color="error",
                )
                try:
                    await member.send(embed=embed)
                except discord.Forbidden:
                    pass
                await member.kick()
                embed = branded_embed(
                    title=self.bot.translate.msg(member.guild.id, "onJoin", "HAS_BEEN_KICKED").format(member),
                    description=self.bot.translate.msg(member.guild.id, "onJoin", "MIN_ACCOUNT_AGE_HAS_BEEN_KICKED_REASON").format(
                        minAccountHours, member.created_at, member, member.id
                    ),
                    color="error",
                    footer_text=f"at {member.joined_at}",
                )
                await sendLogMessage(self, event=member, channel=logChannel, embed=embed)

        if data["captcha"] is True:
            temp_role_id = data.get("temporaryRole")
            if temp_role_id and temp_role_id != 1:
                getrole = get(member.guild.roles, id=temp_role_id)
                if getrole:
                    await member.add_roles(getrole)

            image = Image.new("RGB", (350, 100), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font="Tools/arial.ttf", size=60)

            text = " ".join(random.choice(string.ascii_uppercase) for _ in range(6))

            W, H = (350, 100)
            bbox = draw.textbbox((0, 0), text, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((W - w) / 2, (H - h) / 2), text, font=font, fill=(90, 90, 90))

            ID = member.id
            folderPath = f"captchaFolder/{member.guild.id}/captcha_{ID}"
            try:
                os.mkdir(folderPath)
            except OSError:
                if os.path.isdir(f"captchaFolder/{member.guild.id}") is False:
                    os.mkdir(f"captchaFolder/{member.guild.id}")
                if os.path.isdir(folderPath) is True:
                    shutil.rmtree(folderPath)
                os.mkdir(folderPath)
            image.save(f"{folderPath}/captcha{ID}.png")

            p = Augmentor.Pipeline(folderPath)
            p.random_distortion(probability=1, grid_width=4, grid_height=4, magnitude=14)
            p.process()

            path = f"{folderPath}/output"
            files = os.listdir(path)
            captchaName = [i for i in files if i.endswith(".png")]
            captchaName = captchaName[0]

            image = Image.open(f"{folderPath}/output/{captchaName}")

            width = random.randrange(6, 8)
            co1 = random.randrange(0, 75)
            co3 = random.randrange(275, 350)
            co2 = random.randrange(40, 65)
            co4 = random.randrange(40, 65)
            draw = ImageDraw.Draw(image)
            draw.line([(co1, co2), (co3, co4)], width=width, fill=(90, 90, 90))

            noisePercentage = 0.25
            pixels = image.load()
            for i in range(image.size[0]):
                for j in range(image.size[1]):
                    rdn = random.random()
                    if rdn < noisePercentage:
                        pixels[i, j] = (90, 90, 90)

            image.save(f"{folderPath}/output/{captchaName}_2.png")

            captchaFile = discord.File(f"{folderPath}/output/{captchaName}_2.png")
            captchaEmbed = await captchaChannel.send(
                self.bot.translate.msg(member.guild.id, "onJoin", "CAPTCHA_MESSAGE").format(member.mention),
                file=captchaFile,
            )
            try:
                shutil.rmtree(folderPath)
            except Exception as error:
                print(f"Delete captcha file failed {error}")

            def check(message):
                if message.author == member and message.content != "":
                    return message.content

            try:
                msg = await self.bot.wait_for("message", timeout=120.0, check=check)
                password = text.split(" ")
                password = "".join(password)
                if msg.content.upper() == password:
                    embed = branded_embed(
                        description=self.bot.translate.msg(member.guild.id, "onJoin", "MEMBER_PASSED_THE_CAPTCHA").format(member.mention),
                        color="captcha_pass",
                    )
                    await captchaChannel.send(embed=embed, delete_after=5)
                    try:
                        role_id = data.get("roleGivenAfterCaptcha")
                        if role_id:
                            getrole = get(member.guild.roles, id=role_id)
                            if getrole:
                                await member.add_roles(getrole)
                    except Exception as error:
                        print(f"Give role failed: {error}")
                    try:
                        getrole = get(member.guild.roles, id=data["temporaryRole"])
                        await member.remove_roles(getrole)
                    except Exception as error:
                        print(f"No temp role found (onJoin) : {error}")
                    await asyncio.sleep(3)
                    try:
                        await captchaEmbed.delete()
                    except discord.errors.NotFound:
                        pass
                    try:
                        await msg.delete()
                    except discord.errors.NotFound:
                        pass
                    embed = branded_embed(
                        title=self.bot.translate.msg(member.guild.id, "onJoin", "MEMBER_PASSED_THE_CAPTCHA").format(member),
                        description=self.bot.translate.msg(member.guild.id, "onJoin", "USER_INFORMATIONS").format(member, member.id),
                        color="captcha_pass",
                        footer_text=self.bot.translate.msg(member.guild.id, "onJoin", "DATE").format(memberTime),
                    )
                    await sendLogMessage(self, event=member, channel=logChannel, embed=embed)
                else:
                    link = await captchaChannel.create_invite(max_age=172800)
                    embed = branded_embed(
                        description=self.bot.translate.msg(member.guild.id, "onJoin", "MEMBER_FAILED_THE_CAPTCHA").format(member.mention),
                        color="captcha_fail",
                    )
                    await captchaChannel.send(embed=embed, delete_after=5)
                    embed = branded_embed(
                        title=self.bot.translate.msg(member.guild.id, "onJoin", "YOU_HAVE_BEEN_KICKED").format(member.guild.name),
                        description=self.bot.translate.msg(member.guild.id, "onJoin", "MEMBER_FAILED_THE_CAPTCHA_REASON").format(link),
                        color="error",
                    )
                    try:
                        await member.send(embed=embed)
                    except discord.errors.Forbidden:
                        pass
                    await member.kick()
                    await asyncio.sleep(3)
                    try:
                        await captchaEmbed.delete()
                    except discord.errors.NotFound:
                        pass
                    try:
                        await msg.delete()
                    except discord.errors.NotFound:
                        pass
                    embed = branded_embed(
                        title=self.bot.translate.msg(member.guild.id, "onJoin", "MEMBER_HAS_BEEN_KICKED").format(member),
                        description=self.bot.translate.msg(member.guild.id, "onJoin", "MEMBER_FAILED_THE_CAPTCHA_REASON_LOG").format(member, member.id),
                        color="error",
                        footer_text=self.bot.translate.msg(member.guild.id, "onJoin", "DATE").format(memberTime),
                    )
                    await sendLogMessage(self, event=member, channel=logChannel, embed=embed)

            except asyncio.TimeoutError:
                link = await captchaChannel.create_invite(max_age=172800)
                embed = branded_embed(
                    title=self.bot.translate.msg(member.guild.id, "onJoin", "TIME_IS_OUT"),
                    description=self.bot.translate.msg(member.guild.id, "onJoin", "USER_HAS_EXCEEDED_THE_RESPONSE_TIME").format(member.mention),
                    color="error",
                )
                await captchaChannel.send(embed=embed, delete_after=5)
                try:
                    embed = branded_embed(
                        title=self.bot.translate.msg(member.guild.id, "onJoin", "YOU_HAVE_BEEN_KICKED").format(member.guild.name),
                        description=self.bot.translate.msg(member.guild.id, "onJoin", "USER_HAS_EXCEEDED_THE_RESPONSE_TIME_REASON").format(link),
                        color="error",
                    )
                    await member.send(embed=embed)
                    await member.kick()
                except Exception as error:
                    print(f"Log failed (onJoin) : {error}")
                await asyncio.sleep(3)
                await captchaEmbed.delete()
                embed = branded_embed(
                    title=self.bot.translate.msg(member.guild.id, "onJoin", "MEMBER_HAS_BEEN_KICKED").format(member),
                    description=self.bot.translate.msg(member.guild.id, "onJoin", "USER_HAS_EXCEEDED_THE_RESPONSE_TIME_LOG").format(member, member.id),
                    color="error",
                    footer_text=self.bot.translate.msg(member.guild.id, "onJoin", "DATE").format(memberTime),
                )
                await sendLogMessage(self, event=member, channel=logChannel, embed=embed)


async def setup(bot):
    await bot.add_cog(OnJoinCog(bot))

import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import json
import os
import time
import io
import aiohttp
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from arabic_reshaper import reshape
from bidi.algorithm import get_display

ALLOWED_CHANNEL_ID = 1519822739152572496

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cog_dir = os.path.dirname(__file__)
        self.data_file = os.path.join(self.cog_dir, "levels.json")
        self.users_data = self.load_data()
        self.cooldowns = {}
        self.auto_save_loop.start()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                try:
                    data = json.load(f)
                    for user_id in data:
                        data[user_id].pop("voice_xp", None)
                        data[user_id].pop("voice_level", None)
                    return data
                except:
                    return {}
        return {}

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.users_data, f, indent=4)

    def cog_unload(self):
        self.auto_save_loop.cancel()
        self.save_data()

    def init_user(self, user_id):
        if str(user_id) not in self.users_data:
            self.users_data[str(user_id)] = {"xp": 0, "level": 1}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
            
        # ⚡ حل مشكلة الردين: منع الـ on_message من لقط أمر -rank لكي لا يتداخل مع أمر الكوماند المكتوب تحت
        if message.content.startswith('-rank'):
            return

        if message.content.startswith(('-', '.', ':')):
            return

        user_id = str(message.author.id)
        current_time = time.time()

        if user_id in self.cooldowns and current_time - self.cooldowns[user_id] < 30:
            return

        self.init_user(user_id)
        self.cooldowns[user_id] = current_time

        self.users_data[user_id]["xp"] += random.randint(15, 25)
        lvl = self.users_data[user_id]["level"]
        xp_needed = self.get_xp_needed(lvl)

        if self.users_data[user_id]["xp"] >= xp_needed:
            self.users_data[user_id]["level"] += 1
            self.users_data[user_id]["xp"] -= xp_needed
            try:
                await message.channel.send(f"🎉 مبروك {message.author.mention}! لفل الكتابة صار **{lvl + 1}**!")
            except:
                pass

    @tasks.loop(seconds=60.0)
    async def auto_save_loop(self):
        self.save_data()

    @auto_save_loop.before_loop
    async def before_loops(self):
        await self.bot.wait_until_ready()

    def get_xp_needed(self, level):
        return 5 * (level ** 2) + (50 * level) + 100

    def format_text(self, text):
        return get_display(reshape(text))

    async def generate_rank_card(self, name, avatar_url, lvl, xp, xp_needed):
        card_width = 950
        card_height = 320
        
        bg_name = "image_90f347.jpg"
        font_name_file = "Cairo-Bold.ttf"
        
        parent_dir = os.path.dirname(self.cog_dir)
        
        paths_to_check_bg = [
            os.path.join(parent_dir, bg_name),
            os.path.join(self.cog_dir, bg_name),
            bg_name
        ]
        
        bg_path = None
        for path in paths_to_check_bg:
            if os.path.exists(path):
                bg_path = path
                break

        paths_to_check_font = [
            os.path.join(parent_dir, font_name_file),
            os.path.join(self.cog_dir, font_name_file),
            font_name_file
        ]
        
        font_path = None
        for path in paths_to_check_font:
            if os.path.exists(path):
                font_path = path
                break

        bg = None
        async with aiohttp.ClientSession() as session:
            if bg_path:
                try:
                    bg = Image.open(bg_path).convert("RGBA").resize((card_width, card_height))
                    print("✅ تم تحميل صورة الساكورا بنجاح من الملفات!")
                except Exception as e:
                    print(f"❌ فشل فتح الصورة محلياً بسبب: {e}")
            
            if bg is None:
                print("⚠️ لم يتم العثور على الصورة محلياً، جاري التحميل من الرابط الاحتياطي...")
                backup_img_url = "https://images.squarespace-cdn.com/content/v1/5ad0ed45b9861e6878b66808/dfbf288e-73cb-4f1b-a36c-9a4f6cf142fc/cherry-blossoms-japan.jpg"
                try:
                    async with session.get(backup_img_url) as res:
                        if res.status == 200:
                            bg = Image.open(io.BytesIO(await res.read())).convert("RGBA").resize((card_width, card_height))
                except:
                    bg = Image.new("RGBA", (card_width, card_height), (25, 20, 35, 255))

            bg = ImageEnhance.Brightness(bg).enhance(0.55)
            draw = ImageDraw.Draw(bg)

            if font_path:
                print(f"✅ تم العثور على خط القاهرة بنجاح في: {font_path}")
            else:
                print("⚠️ لم يتم العثور على الخط محلياً، جاري تحميله تلقائياً لمنع المربعات...")
                font_url = "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Bold.ttf"
                try:
                    async with session.get(font_url) as res:
                        if res.status == 200:
                            font_path = io.BytesIO(await res.read())
                except:
                    font_path = "arial.ttf"

            try:
                font_name = ImageFont.truetype(font_path, 50)   
                font_stats = ImageFont.truetype(font_path, 32)  
                font_lbl = ImageFont.truetype(font_path, 30)    
            except:
                font_name = font_stats = font_lbl = ImageFont.load_default()

            async with session.get(avatar_url) as response:
                avatar_bytes = await response.read()
                
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((190, 190))
        mask = Image.new("L", (190, 190), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 190, 190), fill=255)
        bg.paste(avatar, (40, 65), mask)
        
        draw.ellipse([36, 61, 234, 259], outline=(195, 120, 230, 255), width=5)
        
        formatted_name = self.format_text(str(name))
        draw.text((270, 50), formatted_name, fill=(255, 255, 255, 255), font=font_name)

        formatted_lvl_text = self.format_text(f" Level: {lvl} 💬")
        draw.text((270, 125), formatted_lvl_text, fill=(255, 255, 255, 230), font=font_lbl)
        
        xp_text = f"{xp} / {xp_needed} XP"
        draw.text((680, 125), xp_text, fill=(230, 235, 250, 255), font=font_stats)
        
        draw.rounded_rectangle([270, 185, 900, 220], radius=15, fill=(45, 35, 55, 180))
        
        progress_chat = min(xp / xp_needed, 1.0)
        if progress_chat > 0:
            draw.rounded_rectangle([270, 185, 270 + int(630 * progress_chat), 220], radius=15, fill=(195, 75, 225, 255))

        output = io.BytesIO()
        bg.save(output, format="PNG")
        output.seek(0)
        return output

    # 1️⃣ أمر الـ Slash Command المحدث لجلب الاسم الفوري المحدث
    @app_commands.command(name="rank", description="عرض بطاقة المستوى (اللفل) الخاصة بك أو بعضو آخر.")
    @app_commands.describe(member="العضو المراد عرض بطاقته (اختياري)")
    async def slash_rank(self, interaction: discord.Interaction, member: discord.Member = None):
        if interaction.channel_id != ALLOWED_CHANNEL_ID:
            return await interaction.response.send_message(
                f"❌ لا يمكنك فعلها هنا! يجب استعمال هذا الأمر في الروم المخصص: <#{ALLOWED_CHANNEL_ID}>", 
                ephemeral=True
            )

        target_member = member or interaction.user
        await interaction.response.defer(ephemeral=False)
        
        # ⚡ التعديل الأهم: استخدام display_name لضمان جلب الاسم المحدث دائماً حتى لو تم تغييره
        display_name = target_member.display_name
        
        self.init_user(str(target_member.id))
        lvl = self.users_data[str(target_member.id)]["level"]
        xp = self.users_data[str(target_member.id)]["xp"]
        xp_needed = self.get_xp_needed(lvl)

        card_image = await self.generate_rank_card(display_name, target_member.display_avatar.url, lvl, xp, xp_needed)
        file = discord.File(fp=card_image, filename="rank.png")
        await interaction.followup.send(file=file)

    # 2️⃣ أمر الـ Prefix Command المحدث لحذف الرسائل العشوائية والرد الفردي
    @commands.command(name="rank")
    async def prefix_rank(self, ctx, member: discord.Member = None):
        if ctx.channel.id != ALLOWED_CHANNEL_ID:
            try: await ctx.message.delete()
            except: pass
            msg = await ctx.send(f"❌ لا يمكنك فعلها هنا يا {ctx.author.mention}! يجب استعمال هذا الأمر في الروم المخصص: <#{ALLOWED_CHANNEL_ID}>")
            await asyncio.sleep(15)
            try: await msg.delete()
            except: pass
            return

        target_member = member or ctx.author
        self.init_user(str(target_member.id))
        
        lvl = self.users_data[str(target_member.id)]["level"]
        xp = self.users_data[str(target_member.id)]["xp"]
        xp_needed = self.get_xp_needed(lvl)

        async with ctx.typing():
            # ⚡ استخدام display_name لضمان تحديث الاسم فورا
            display_name = target_member.display_name
            card_image = await self.generate_rank_card(display_name, target_member.display_avatar.url, lvl, xp, xp_needed)
            file = discord.File(fp=card_image, filename="rank.png")
            await ctx.reply(file=file, mention_author=False)

    @app_commands.command(name="setlevel", description="تغيير مستوى (لفل) عضو معين في السيرفر.")
    @app_commands.describe(member="العضو المراد تغيير مستواه", level="المستوى الجديد المراد وضعه له")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlevel(self, interaction: discord.Interaction, member: discord.Member, level: int):
        if level < 1:
            await interaction.response.send_message("❌ ما يصير تحط لفل أقل من 1!", ephemeral=True)
            return
        user_id = str(member.id)
        self.init_user(user_id)
        self.users_data[user_id]["level"] = level
        self.users_data[user_id]["xp"] = 0
        await interaction.response.send_message(f"✅ تم تعديل لفل {member.mention} بنجاح إلى لفل **{level}**!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Levels(bot))
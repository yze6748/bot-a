import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import os
import asyncio

# الأياديات الخاصة بسيرفرك
TARGET_GUILD_ID = 1519350245136273500
ALLOWED_CHANNEL_ID = 1519444743732461698
IMMUNE_ROLE_ID = 1519351522503168142  # الرتبة الحصينة من الحذف

class Downloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # حدث لحذف الرسائل العادية وتنبيه الأعضاء
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if message.channel.id == ALLOWED_CHANNEL_ID:
            # التحقق إذا كان العضو يمتلك الرتبة الحصينة
            if isinstance(message.author, discord.Member):
                if any(role.id == IMMUNE_ROLE_ID for role in message.author.roles):
                    return  # تخطي الحذف لأن لديه الحصانة
            
            # حذف رسالة العضو المخالف فوراً
            try:
                await message.delete()
                # إرسال رسالة تنبيه مخفية للعضو (لا يراها غيره) لحفظ نظافة الروم
                await message.channel.send(
                    f"⚠️ {message.author.mention} ما يمديك تستعمل الروم كذا، لازم تكتب `/مقطع` وترسل رابط المقطع.",
                    delete_after=15  # تحذف تلقائياً بعد 15 ثانية احتياطاً لو ظهرت
                )
            except discord.Forbidden:
                print(f"البوت يفتقر لصلاحية 'إدارة الرسائل' في الروم {ALLOWED_CHANNEL_ID}")
            except discord.HTTPException:
                pass

    @app_commands.command(name="مقطع", description="تحميل مقطع، صورة، أو GIF من الرابط")
    @app_commands.describe(url="رابط المقطع أو الصورة", visibility="هل تبيه عام أم خاص؟", spoiler="هل المقطع فيه سبويلر؟")
    @app_commands.choices(visibility=[
        app_commands.Choice(name="عام (الكل يشوفه)", value="public"),
        app_commands.Choice(name="خاص (أنا فقط)", value="private")
    ])
    async def مقطع(self, interaction: discord.Interaction, url: str, visibility: str = "public", spoiler: bool = False):
        
        # تطبيق شروط السيرفر الخاص بك
        if interaction.guild_id == TARGET_GUILD_ID:
            if interaction.channel_id != ALLOWED_CHANNEL_ID:
                visibility = "private"
        
        is_ephemeral = (visibility == "private")
        await interaction.response.defer(ephemeral=is_ephemeral)
        
        clean_url = url.strip().lower()
        image_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
        
        # التعديل: فحص روابط الصور المباشرة أو منصات الصور (بنترست، انستا، تيك توك صور)
        is_image_platform = any(p in clean_url for p in ["pinterest.com", "pin.it", "instagram.com", "tiktok.com"])
        
        # إذا كان الرابط ينتهي بامتداد صورة أو كان رابط من منصات الصور بشرط ألا يكون فيديو واضحاً
        if clean_url.endswith(image_extensions) or "tenor.com" in clean_url or "giphy.com" in clean_url or (is_image_platform and not any(v in clean_url for v in ["/video/", "/p/", "/reel/"])):
            content = f"🖼️ **طلب بواسطة:** {interaction.user.mention}\n"
            if spoiler:
                content += f"|| {url} ||"
            else:
                content += url
                
            await interaction.followup.send(content=content, ephemeral=is_ephemeral)
            return

        # معالجة الفيديوهات عبر yt_dlp
        file_name = f"video_{interaction.id}.mp4"
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_name,
            'quiet': True,
            'max_filesize': 1000 * 1024 * 1024,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'مقطع فيديو')
            
            if os.path.exists(file_name):
                file = discord.File(file_name, filename="video.mp4", spoiler=spoiler)
                content = f"🎬 **العنوان:** {title}\nطلب بواسطة: {interaction.user.mention}"
                
                await interaction.followup.send(content=content, file=file, ephemeral=is_ephemeral)
                os.remove(file_name)
            else:
                # رسالة خطأ تحذف بعد 30 ثانية إذا كانت عامة
                await interaction.followup.send("❌ عذراً، تعذر العثور على الملف المحمل.", ephemeral=is_ephemeral)
                
        except yt_dlp.utils.DownloadError:
            msg = "❌ حجم المقطع كبير جداً، أو المنصة غير مدعومة حالياً."
            await interaction.followup.send(msg, ephemeral=is_ephemeral)
        except Exception as e:
            msg = f"❌ حدث خطأ غير متوقع: {e}"
            await interaction.followup.send(msg, ephemeral=is_ephemeral)
            if os.path.exists(file_name):
                os.remove(file_name)

async def setup(bot):
    await bot.add_cog(Downloader(bot))
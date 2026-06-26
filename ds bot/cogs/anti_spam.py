import discord
from discord.ext import commands
import asyncio
from datetime import timedelta, datetime

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_history = {}  # لتخزين تواريخ الرسائل بالوقت اللحظي
        self.immunity = {}       # لتخزين وقت انتهاء الحصانة
        self.yze_id = 1160184736946323456
        self.itheb_id = 1170429557518647319  # يوزر itheb.17
        self.vip_user = 719883090075320412

    @commands.Cog.listener()
    async def on_message(self, message):
        # تجاهل البوتات
        if message.author.bot or message.author.id == self.bot.user.id:
            return

        uid = message.author.id
        now = datetime.utcnow()

        # 1. نظام الحصانة المطور (يجب أن يكون ريبلاي على رسالة تحذير محددة وبأحرف دقيقة)
        if message.reference and message.reference.resolved:
            replied_msg = message.reference.resolved
            
            # التأكد أن الرسالة المردود عليها هي من البوت نفسه، وتحتوي على عبارات التحذير المعروفة
            if replied_msg.author.id == self.bot.user.id and any(x in replied_msg.content for x in ["اهجد", "بزر", "تايم آوت"]):
                
                # فحص كلمات الحصانة لصاحب الحساب yze_
                if uid == self.yze_id and message.content in ["مياو", "احبك", "اروح لك فدوه"]:
                    self.immunity[uid] = now + timedelta(minutes=10)
                    await message.reply("خلاص جتك حصانة دبلوماسية مخصوص مني، 10 دقايق سبام على كيفك!")
                    return
                
                # فحص كلمة "سردب" لصاحبك itheb.17
                elif uid == self.itheb_id and message.content == "سردب":
                    self.immunity[uid] = now + timedelta(minutes=10) # إذا تبي تعطيه حصانة أيضاً، أو تقدر تحذف السطر هذا
                    await message.reply("سردب")
                    return

        # التحقق من وجود الحصانة الفعالة
        if uid in self.immunity:
            if now < self.immunity[uid]:
                return
            else:
                del self.immunity[uid]

        # تحديد لقب الشخص
        title = "الحلو ذا" if uid == self.vip_user else "الحمار ذا"

        # 2. نظام السبام العشوائي (أي 3 رسائل خلال 3 ثوانٍ)
        if uid not in self.users_history:
            self.users_history[uid] = []
        
        # إضافة وقت الرسالة الحالية للتاريخ
        self.users_history[uid].append(now)
        
        # تنظيف التاريخ: إزالة أي رسائل أقدم من 3 ثوانٍ من الآن
        self.users_history[uid] = [msg_time for msg_time in self.users_history[uid] if (now - msg_time).total_seconds() <= 3]
        
        msg_count = len(self.users_history[uid])

        # فحص العقوبات بناءً على عدد الرسائل في الـ 3 ثوانٍ الأخيرة
        if msg_count >= 3:
            if msg_count == 4:  # الرسالة الرابعة خلال الـ 3 ثوانٍ تعني تايم آوت فوراً
                try:
                    await message.author.timeout(timedelta(minutes=10), reason="سبام عشوائي مكثف")
                    await message.channel.send(f"ترا عطيت {title} {message.author.mention} تايم آوت 10 دقايق!")
                except:
                    await message.channel.send("ماقدرت أعطيه تايم آوت، تأكد من صلاحياتي!")
            elif msg_count == 3:  # الرسالة الثالثة تعني التحذير الأول
                if uid == self.itheb_id:
                    await message.reply(f"يا حلو اهجد شوي، ولا بنادي يامي <@{self.itheb_id}>!")
                else:
                    await message.reply(f"خلاص يابزر عطيناك وجه، اهجد ولا بنادي يامي <@{self.itheb_id}>")

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
import discord
from discord.ext import commands
import datetime

# إعدادات الأياديات الخاصة بسيرفرك
TARGET_GUILD_ID = 1519350245136273500
ALLOWED_ROLE_ID = 1519351847314391040   # الرتبة المسموح لها فما فوق
SPECIAL_USER_ID = 1160184736946323456   # آيدي صاحب الحساب المحدد
LOGS_CHANNEL_ID = 1519813983723589823     # روم السجلات (اللوق)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # دالة فحص الصلاحيات والسيرفر
    async def check_permissions(self, ctx):
        # إذا كان الأمر خارج السيرفر المستهدف، يسمح بالمرور طبيعي بناءً على صلاحيات الديسكورد الأساسية
        if ctx.guild.id != TARGET_GUILD_ID:
            return True

        # التحقق من الحساب المخصص أو الرتبة فما فوق
        is_special_user = ctx.author.id == SPECIAL_USER_ID
        has_required_role = False
        
        if isinstance(ctx.author, discord.Member):
            target_role = ctx.guild.get_role(ALLOWED_ROLE_ID)
            if target_role and ctx.author.top_role >= target_role:
                has_required_role = True

        if not (is_special_user or has_required_role):
            await ctx.reply("❌ عذراً، لا تملك الصلاحيات الكافية لاستخدام هذا الأمر هنا.", delete_after=10)
            return False

        return True

    # دالة مساعدة لمقارنة رتب الإداريين لمنع المشاكل
    def can_moderate(self, ctx, member):
        if member.id == ctx.guild.owner_id:
            return "❌ تبيني ألمس صاحب السيرفر؟ مستحيل!"
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            return "❌ ما تقدر تسوي كذا، رتبته أعلى منك أو مساوية لك!"
        if member.top_role >= ctx.guild.me.top_role:
            return "❌ رتبته أعلى من رتبتي، ما أقدر ألمسه!"
        return None

    # دالة لإرسال السجلات (Logs) تلقائياً
    async def send_log(self, ctx, action_name, target, details="لا يوجد"):
        if ctx.guild.id != TARGET_GUILD_ID:
            return
        
        logs_channel = self.bot.get_channel(LOGS_CHANNEL_ID)
        if logs_channel:
            embed = discord.Embed(
                title="📝 سجل عمل إداري جديد",
                timestamp=discord.utils.utcnow(),
                color=discord.Color.red()
            )
            embed.add_field(name="المنفّذ (المسؤول):", value=f"{ctx.author.mention} ({ctx.author.id})", inline=False)
            embed.add_field(name="الإجراء (الأمر):", value=f"`-{action_name}`", inline=True)
            embed.add_field(name="المتلقي (العضو):", value=f"{target.mention} ({target.id})", inline=True)
            embed.add_field(name="تفاصيل إضافية / المدة:", value=details, inline=False)
            embed.set_footer(text=f"سيرفر: {ctx.guild.name} | الشات: #{ctx.channel.name}")
            
            await logs_channel.send(embed=embed)

    # --- أوامر الإدارة ---

    @commands.command(name="اسكت")
    @commands.has_permissions(moderate_members=True)
    async def timeout_user(self, ctx, member: discord.Member = None, duration: str = None):
        if not await self.check_permissions(ctx): return

        # دعم الريبلاي
        if not member and ctx.message.reference:
            member = ctx.message.reference.resolved.author
            args = ctx.message.content.split()
            duration = args[1] if len(args) > 1 else None

        if not member or not duration:
            return await ctx.reply("❌ الطريقة الصحيحة: `-اسكت @منشن 3m` أو سوي ريبلاي واكتب `-اسكت 3m`", delete_after=30)

        error = self.can_moderate(ctx, member)
        if error: return await ctx.reply(error, delete_after=30)

        try:
            unit = duration[-1].lower()
            amount = int(duration[:-1])
            if unit == 's': delta = datetime.timedelta(seconds=amount)
            elif unit == 'm': delta = datetime.timedelta(minutes=amount)
            elif unit == 'h': delta = datetime.timedelta(hours=amount)
            elif unit == 'd': delta = datetime.timedelta(days=amount)
            else: raise ValueError
            
            await member.edit(timed_out_until=discord.utils.utcnow() + delta)
            await ctx.reply(f"🔇 تم إسكات {member.mention} لمدة {duration}!")
            await self.send_log(ctx, "اسكت", member, f"المدة: {duration}")
        except Exception:
            await ctx.reply("❌ صيغة الوقت غلط! (مثال: `-اسكت @عضو 3m`)", delete_after=30)

    @commands.command(name="تكلم")
    @commands.has_permissions(moderate_members=True)
    async def unmute_user(self, ctx, member: discord.Member = None):
        if not await self.check_permissions(ctx): return

        if not member and ctx.message.reference:
            member = ctx.message.reference.resolved.author
            
        if not member:
            return await ctx.reply("❌ لازم تمنشن الشخص أو تسوي ريبلاي عليه!", delete_after=30)

        error = self.can_moderate(ctx, member)
        if error: return await ctx.reply(error, delete_after=30)

        try:
            await member.edit(timed_out_until=None)
            await ctx.reply(f"🕊️ أبشر، جاك عفو ملكي يا {member.mention}، تقدر تتكلم من جديد!")
            await self.send_log(ctx, "تكلم", member, "تم إلغاء الإسكات (عفو ملكي)")
        except Exception as e:
            await ctx.reply(f"❌ فيه مشكلة، تأكد من صلاحياتي! (الخطأ: {e})", delete_after=30)

    @commands.command(name="انقلع")
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member = None):
        if not await self.check_permissions(ctx): return

        if not member and ctx.message.reference:
            member = ctx.message.reference.resolved.author
        
        if not member: return await ctx.reply("❌ لازم تمنشن الشخص أو تسوي ريبلاي!", delete_after=30)
        
        error = self.can_moderate(ctx, member)
        if error: return await ctx.reply(error, delete_after=30)

        try:
            await member.kick(reason="بأمر من Lucelifr")
            await ctx.reply(f"✈️ انقلع براا {member.name} بسلام.")
            await self.send_log(ctx, "انقلع", member, "الطرد بطلب من الإدارة")
        except Exception as e:
            await ctx.reply(f"❌ تعذر طرد العضو: {e}", delete_after=30)

    @commands.command(name="حظر")
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: discord.Member = None):
        if not await self.check_permissions(ctx): return

        if not member and ctx.message.reference:
            member = ctx.message.reference.resolved.author

        if not member: return await ctx.reply("❌ لازم تمنشن الشخص أو تسوي ريبلاي!", delete_after=30)

        error = self.can_moderate(ctx, member)
        if error: return await ctx.reply(error, delete_after=30)

        try:
            await member.ban(reason="بأمر من Lucelifr")
            await ctx.reply(f"🔨 تم بنجاح نفخ وتبنيد {member.mention}!")
            await self.send_log(ctx, "حظر", member, "حظر نهائي وبند من السيرفر")
        except Exception as e:
            await ctx.reply(f"❌ تعذر حظر العضو: {e}", delete_after=30)

async def setup(bot):
    await bot.add_cog(Admin(bot))
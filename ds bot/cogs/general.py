import discord
from discord.ext import commands

MY_ACCOUNT_ID = 1160184736946323456  # الآيدي الثابت الخاص بك
FEMALE_ROLE_ID = 1519758969604800695  # رتبة البنات المحددة
LEVEL_CHANNEL_ID = 1519822739152572496  # آيدي روم اللفلات لإرسال تحديث الاسم فيه

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content_clean = message.content.strip()

        # ⚡ حل مشكلة الردين: منع الـ on_message من معالجة أي رسالة تبدأ بـ الأوامر لكي لا تتكرر الردود
        if content_clean.startswith(('-', '.', ':')):
            return

        # --- 1. فحص السلام عليكم ---
        if "سلام عليكم" in content_clean:
            if message.author.id == MY_ACCOUNT_ID:
                await message.reply("عليكم السلام ورحمة الله وبركاته منور يازعيمم", mention_author=False)
            elif isinstance(message.author, discord.Member) and any(role.id == FEMALE_ROLE_ID for role in message.author.roles):
                await message.reply("عليكم السلام ورحمة الله وبركاته منوره ياحلوههه", mention_author=False)
            else:
                await message.reply("عليكم السلام ورحمة الله وبركاته منور", mention_author=False)

        # --- 2. فحص صباح الخير ---
        elif "صباح الخير" in content_clean:
            if isinstance(message.author, discord.Member) and any(role.id == FEMALE_ROLE_ID for role in message.author.roles):
                await message.reply("صباحو يا احلا صباح انتي.", mention_author=False)
            else:
                await message.reply("صباح النور والسرور ارحب", mention_author=False)

    @commands.command(name="اسم")
    @commands.has_permissions(manage_nicknames=True)  # التأكد أن المستخدم لديه صلاحية تعديل الأسماء
    async def name_changer(self, ctx, member: discord.Member, *, new_nick: str):
        if member == ctx.guild.owner:
            return await ctx.send("❌ ما أقدر أغير اسم مالك السيرفر!", delete_after=30)

        # حفظ الاسم القديم قبل التغيير (إذا ما عنده نيك نيم بيأخذ اسمه الأصلي)
        old_name = member.display_name 

        try:
            # تغيير الاسم
            await member.edit(nick=new_nick)
            await ctx.send(f"تم تغيير اسم {member.mention} إلى **{new_nick}** بنجاح! ✅")

            # --- إرسال التقرير إلى الروم المحدد ---
            log_channel_id = 1519813983723589823  # آيدي روم التقارير
            log_channel = self.bot.get_channel(log_channel_id)

            if log_channel:
                embed = discord.Embed(
                    title="📝 تقرير تغيير اسم مستعار",
                    color=discord.Color.blue(),
                    timestamp=ctx.message.created_at
                )
                embed.add_field(name="المنفذ (المشرف):", value=f"{ctx.author.mention} ({ctx.author.id})", inline=False)
                embed.add_field(name="المستهدف (العضو):", value=f"{member.mention} ({member.id})", inline=False)
                embed.add_field(name="الاسم القديم:", value=f"**{old_name}**", inline=True)
                embed.add_field(name="الاسم الجديد:", value=f"**{new_nick}**", inline=True)
                embed.set_footer(text=f"سيرفر: {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                
                await log_channel.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ عجزت أغير الاسم! تأكد أن رتبة البوت أعلى من رتبة هذا الشخص في قائمة الرتب وصلاحياتي كاملة.", delete_after=30)
        except Exception as e:
            await ctx.send(f"❌ حدث خطأ: {e}", delete_after=30)


async def setup(bot):
    await bot.add_cog(General(bot))
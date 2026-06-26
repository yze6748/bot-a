import discord
from discord.ext import commands
import asyncio
from datetime import timedelta

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_history = {}
        self.immunity = {}
        self.yze_id = 1160184736946323456

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.id == self.bot.user.id:
            return

        uid = message.author.id
        content = message.content or "sticker"
        
      
        if message.reference and message.reference.resolved:
            
            if any(word in message.content.lower() for word in ["مياو", "احبك", "اروح لك فدوه"]):
                
                if uid == self.yze_id:
                    self.immunity[uid] = True
                    await message.reply("خلاص جتك حصانة دبلوماسية مخصوص مني، 10 دقايق سبام على كيفك!")
                    
                    
                    await asyncio.sleep(600)
                    if uid in self.immunity:
                        del self.immunity[uid]
                    return

        if self.immunity.get(uid):
            return

       
        title = "الحلو ذا" if uid == 719883090075320412 else "الحمار ذا"
        
        
        if uid not in self.users_history: self.users_history[uid] = []
        history = self.users_history[uid]
        history.append(content)
        if len(history) > 4: history.pop(0)

        
        b3w9_id = 1170429557518647319

        if len(history) >= 3 and history.count(content) >= 3:
            if history.count(content) == 4:
                try:
                    await message.author.timeout(timedelta(minutes=10), reason="سبام")
                    await message.channel.send(f"ترا عطيت {title} {message.author.mention} تايم آوت 10 دقايق!")
                except:
                    await message.channel.send("ماقدرت أعطيه تايم آوت، تأكد من صلاحياتي!")
            else:
                # هنا التعديل لعمل المنشن لـ b3w9
                if uid == 1170429557518647319:
                    await message.reply(f"يا حلو اهجد شوي، ولا بنادي يامي <@{b3w9_id}>!")
                else:
                    await message.reply(f"خلاص يابزر عطيناك وجه، اهجد ولا بنادي يامي <@{b3w9_id}>")

        await asyncio.sleep(5)
        if uid in self.users_history and content in self.users_history[uid]:
            self.users_history[uid].remove(content)

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
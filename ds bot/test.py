import discord
from discord.ext import commands
import asyncio
import os


MY_ID = 1160184736946323456

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix="-", intents=intents, owner_id=MY_ID)


@bot.check
async def global_check(ctx):
    if ctx.author.id == MY_ID:
        
        await ctx.send("صانعي ما اقدر اسوي له شي مايطاوعني قلبي ❤️")
        return False 
    return True #
import discord
from discord.ext import commands
import asyncio
import os


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True


bot = commands.Bot(command_prefix="-", intents=intents)


async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ تم تحميل ملف الأوامر: {filename}")
            except Exception as e:
                print(f"❌ فشل تحميل ملف {filename}: {e}")


@bot.event
async def on_ready():
    print(f"🎯 البوت شغال الحين باسم: {bot.user.name}")
    
    synced = await bot.tree.sync()
    print(f"✨ تم تحديث {len(synced)} من اختصارات الـ (/) بنجاح!")
    
    
    try:
        synced = await bot.tree.sync()
        print(f"✨ تم تحديث {len(synced)} من اختصارات الـ (/) بنجاح في السيرفرات!")
    except Exception as e:
        print(f"❌ فشل تحديث اختصارات الـ (/) في السيرفر: {e}")
    print("------------------------------------------")


async def main():
    async with bot:
        await load_extensions() 
        await bot.start('MTUxNzQ0MjM3Mjk5NTM4MzMyNg.GEagFR.zOusvsEZYeEacPUURoadT_rtSCCmqQCJAV9OBo')

if __name__ == "__main__":
    asyncio.run(main())

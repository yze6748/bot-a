from discord.ext import commands
import discord

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="صلاحيات")
    @commands.is_owner() 
    async def get_power(self, ctx):
        
        await ctx.send("✅ تم التعرف عليك يا صانعي، صلاحياتك مفعلة!")

    @commands.command(name="سوبر")
    @commands.is_owner()
    async def super_power(self, ctx):
        await ctx.send("✅ تم تفعيل الوضع الخارق: أنت الآن تمتلك كامل الصلاحيات!")


async def setup(bot):
    await bot.add_cog(AdminTools(bot))
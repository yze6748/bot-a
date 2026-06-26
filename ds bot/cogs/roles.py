import discord
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def find_role(self, ctx, query):
        matches = [r for r in ctx.guild.roles if query.lower() in r.name.lower()]
        if not matches: return None, "❌ مالقيت رتبة باسم مشابه!"
        if len(matches) > 1: return None, "⚠️ لقيت أكثر من رتبة مشابهة، حدد الاسم بدقة."
        return matches[0], None

    @commands.command(name="عطني")
    async def get_role(self, ctx, *, role_name: str = None):
        if not role_name: return await ctx.reply("❌ اكتب اسم الرتبة!")
        role, error = self.find_role(ctx, role_name)
        if error: return await ctx.reply(error)
        
        try:
            await ctx.author.add_roles(role)
            await ctx.reply(f"✅ أبشر، عطيتك رتبة **{role.name}**!")
        except discord.Forbidden:
            await ctx.reply("❌ ما أقدر أعطيك الرتبة، تأكد أن رتبتي في السيرفر أعلى من رتبة الرتبة اللي تبيها!")

    @commands.command(name="خذ")
    @commands.has_permissions(manage_roles=True)
    async def give_role(self, ctx, *, args: str):
        if not ctx.message.mentions: return await ctx.reply("❌ لازم تمنشن الشخص!")
        member = ctx.message.mentions[0]
        role_query = args.replace(f"<@{member.id}>", "").replace(f"<@!{member.id}>", "").strip()
        role, error = self.find_role(ctx, role_query)
        if error: return await ctx.reply(error)
        
        try:
            await member.add_roles(role)
            await ctx.reply(f"✅ تم إعطاء **{role.name}** لـ {member.mention}")
        except discord.Forbidden:
            await ctx.reply("❌ تأكد من ترتيب الرتب (رتبتي لازم تكون فوق الرتبة المطلوبة)!")

    @commands.command(name="اسحب")
    @commands.has_permissions(manage_roles=True)
    async def remove_role(self, ctx, *, args: str):
        if not ctx.message.mentions: return await ctx.reply("❌ لازم تمنشن الشخص!")
        member = ctx.message.mentions[0]
        role_query = args.replace(f"<@{member.id}>", "").replace(f"<@!{member.id}>", "").strip()
        role, error = self.find_role(ctx, role_query)
        if error: return await ctx.reply(error)
        
        try:
            await member.remove_roles(role)
            await ctx.reply(f"➖ تم سحب **{role.name}** من {member.mention}")
        except discord.Forbidden:
            await ctx.reply("❌ تأكد من ترتيب الرتب!")

async def setup(bot):
    await bot.add_cog(Roles(bot))
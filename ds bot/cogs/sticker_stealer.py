import discord
from discord.ext import commands
import io
import aiohttp
from PIL import Image

class Stealer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_image_bytes(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()
        return None

    @commands.command(name="اسرق")
    async def steal(self, ctx):
        url = None
        if ctx.message.reference and ctx.message.reference.resolved:
            msg = ctx.message.reference.resolved
            if msg.stickers: url = msg.stickers[0].url
            elif msg.attachments: url = msg.attachments[0].url
            elif msg.content:
                if "<" in msg.content and ">" in msg.content:
                    emoji_id = msg.content.split(":")[-1].replace(">", "")
                    is_animated = msg.content.startswith("<a:")
                    url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if is_animated else 'png'}"
        
        if not url:
            return await ctx.reply("❌ لم أجد إيموجي أو ستكر!")

        image_data = await self.get_image_bytes(url)
        if not image_data:
            return await ctx.reply("❌ فشل تحميل الملف.")

        emoji_slots = ctx.guild.emoji_limit - len(ctx.guild.emojis)
        sticker_slots = ctx.guild.sticker_limit - len(ctx.guild.stickers)
        
        view = StealView(image_data, emoji_slots, sticker_slots)
        # الرسالة ستحذف تلقائياً بعد 30 ثانية إذا لم يتم الضغط على شيء
        await ctx.reply("🤔 وش تبيها تكون؟", view=view, delete_after=30)

class StealView(discord.ui.View):
    def __init__(self, image_data, emoji_slots, sticker_slots):
        super().__init__(timeout=30)
        self.image_data = image_data
        
        self.emoji_btn.label = f"إيموجي ({emoji_slots})"
        self.emoji_btn.style = discord.ButtonStyle.success if emoji_slots > 0 else discord.ButtonStyle.danger
        self.emoji_btn.disabled = (emoji_slots <= 0)

        self.sticker_btn.label = f"ستكر ({sticker_slots})"
        self.sticker_btn.style = discord.ButtonStyle.primary if sticker_slots > 0 else discord.ButtonStyle.danger
        self.sticker_btn.disabled = (sticker_slots <= 0)

    @discord.ui.button(label="إيموجي", custom_id="emoji")
    async def emoji_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # حذف الرسالة فور الضغط
            await interaction.message.delete()
            await interaction.response.send_message("⏳ جاري الرفع...", ephemeral=True)
            await interaction.guild.create_custom_emoji(name="stolen", image=self.image_data)
            await interaction.followup.send("✅ تمت سرقة الإيموجي!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ خطأ: {e}", ephemeral=True)

    @discord.ui.button(label="ستكر", custom_id="sticker")
    async def sticker_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # حذف الرسالة فور الضغط
            await interaction.message.delete()
            await interaction.response.send_message("⏳ جاري الضغط والرفع...", ephemeral=True)
            
            img = Image.open(io.BytesIO(self.image_data)).convert("RGBA")
            output = io.BytesIO()
            img.save(output, format="PNG")
            output.seek(0)
            
            await interaction.guild.create_sticker(
                name="stolen", file=discord.File(output, filename="st.png"),
                description="مسروق", emoji='😀'
            )
            await interaction.followup.send("✅ تمت سرقة الستكر!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ فشل: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Stealer(bot))
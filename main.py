import discord
from discord.ext import commands
import aiohttp
import urllib.parse
from datetime import datetime
import asyncio
import os

# ================= ตั้งค่าบอท =================
TOKEN = ' ' 
API_TOKEN = "ใส่โทเค่น"
BASE_URL = "https://slumzick.xyz"
OWNER_ID = 1074621727541317712 
RESULT_CHANNEL_ID = 1474880810136895498 
# ===========================================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ SLUMZICK SHOP - ULTIMATE UI & DEEP SCAN READY')

async def call_api(endpoint, value):
    current_token = "mz" if endpoint == "transport.php" else API_TOKEN
    url = f"{BASE_URL}/{endpoint}?token={current_token}&value={urllib.parse.quote(str(value))}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=30) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
        except: return None

# --- ฟังก์ชันเจาะทะลุ JSON (Deep Scan) ---
def find_mobile_items(data):
    results = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "mobileItems" and isinstance(v, list):
                results.extend(v)
            else:
                results.extend(find_mobile_items(v))
    elif isinstance(data, list):
        for item in data:
            results.extend(find_mobile_items(item))
    return results

# --- ฟังก์ชันสร้าง Embed สปสช ---
def create_nhso_embed(title, color, data, footer, user_mention):
    owner = data.get('owner', {})
    p = owner.get('personData', {})
    is_dead = str(p.get('deathFlag', '0'))
    status_life = "🟢 ยังมีชีวิตอยู่" if is_dead == '0' else "💀 เสียชีวิตแล้ว"
    gender_raw = p.get('gender') or p.get('sex') or "-"
    gender_display = "ชาย ♂️" if "1" in str(gender_raw) or "ชาย" in str(gender_raw) else "หญิง ♀️" if "2" in str(gender_raw) or "หญิง" in str(gender_raw) else gender_raw

    info = (
        f"👤 ชื่อ-นามสกุล : {p.get('fullName', '-')}\n"
        f"🆔 เลขบัตรประชาชน : {p.get('pid', '-')}\n"
        f"🎂 วันเกิด : {p.get('displayBirthDate', '-')}\n"
        f"⏳ อายุ : {p.get('age', {}).get('years', '-')} ปี  |  🚻 เพศ : {gender_display}\n"
        f"💓 สถานะบุคคล : {status_life}\n"
        f"🛡️ สิทธิหลัก : {owner.get('subInscl', {}).get('insclName', '-')}\n"
        f"🏥 หน่วยงาน : {owner.get('hospMain', {}).get('hname', '-')}\n"
        f"📍 ที่อยู่ : {p.get('fullAddress', '-')}"
    )
    embed = discord.Embed(title=title, color=color, description=f"👤 ผู้ค้นหา: {user_mention}\n```yaml\n{info}\n```")
    embed.set_footer(text=footer)
    return embed

# --- [ จุดแก้ไข: ฟังก์ชันดึงข้อมูลแยกข้อความ ] ---
async def get_parent_data(channel, pid, label, color, user):
    if not pid or pid == "-": return
    data = await call_api("nhso.php", pid)
    if data and data.get('owner'):
        embed = create_nhso_embed(f"📌 ข้อมูล{label}", color, data, f"SLUMZICK DATABASE | {label}", user.mention)
        await channel.send(embed=embed)

class InputModal(discord.ui.Modal):
    def __init__(self, title, endpoint):
        super().__init__(title=title)
        self.endpoint = endpoint
        self.input_field = discord.ui.TextInput(label=f"ระบุ {title}", placeholder="ป้อนข้อมูลเพื่อเริ่มต้นการเจาะระบบ...", required=True)
        self.add_item(self.input_field)

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        result_channel = bot.get_channel(RESULT_CHANNEL_ID)
        await interaction.response.send_message(f"🌀 **กำลังเชื่อมต่อฐานข้อมูล SLUMZICK... กรุณารอสักครู่**", ephemeral=True)
        
        raw_data = await call_api(self.endpoint, self.input_field.value)
        await interaction.edit_original_response(content=f"✅ **ค้นหาข้อมูลสำเร็จ!** ตรวจสอบได้ที่ช่อง <#{RESULT_CHANNEL_ID}>")

        if not raw_data: return await result_channel.send(f"❌ {user.mention} ไม่พบข้อมูล")

        if self.endpoint == "true.php":
            res = raw_data.get('response-data', {})
            if not res: return
            addr = res.get('address-list', {}).get('CUSTOMER_ADDRESS', {})
            embed = discord.Embed(title="🔍 ข้อมูลลูกค้า True Portal", color=0xe74c3c)
            embed.add_field(name="【 👤 ข้อมูลเจ้าของบัญชี 】", value=f"```\nชื่อ-สกุล: {res.get('firstname', '-')} {res.get('lastname', '-')}\nเลขบัตร: {res.get('id-number', '-')}\nวันเกิด: {res.get('birthDate', '-')}\nเพศ: {res.get('gender', '-')}\n```", inline=False)
            embed.add_field(name="【 📞 ช่องทางติดต่อ 】", value=f"```\n{res.get('contact-number', self.input_field.value)}\n```", inline=False)
            embed.add_field(name="【 📜 ที่อยู่จดทะเบียน 】", value=f"```\nบ้านเลขที่: {addr.get('number', '-')}\nตำบล: {addr.get('sub-district', '-')}\nอำเภอ: {addr.get('district', '-')}\nจังหวัด: {addr.get('province', '-')}\n```", inline=False)
            embed.add_field(name="【 💬 รายละเอียดบริการ 】", value=f"```\nCID: {res.get('customer-id', '-')}\nLevel: {res.get('customer-level', 'None')}\n```", inline=False)
            await result_channel.send(embed=embed)
            await result_channel.send(user.mention)

        elif self.endpoint == "nhso.php":
            # 1. แสดงข้อมูลเจ้าตัว
            embed = create_nhso_embed("🏥 ข้อมูลสิทธิการรักษา (เจ้าของ)", 0xf1c40f, raw_data, "SLUMZICK DATABASE", user.mention)
            await result_channel.send(embed=embed)
            
            # 2. ดึงข้อมูลพ่อแม่แยกข้อความ
            fam = raw_data.get('family', {})
            f_pid = fam.get('father', {}).get('pid')
            m_pid = fam.get('mother', {}).get('pid')
            
            if f_pid: await get_parent_data(result_channel, f_pid, "บิดา", 0x3498db, user)
            if m_pid: await get_parent_data(result_channel, m_pid, "มารดา", 0xe91e63, user)

        elif self.endpoint == "name.php":
            res_list = raw_data.get('data', [])
            if not res_list: return await result_channel.send(f"❌ {user.mention} ไม่พบข้อมูล")
            for item in res_list[:5]:
                p = item.get('personalInfo', {})
                info = (f"👤 ชื่อ-นามสกุล : {p.get('fullName', '-')}\n🆔 เลขบัตรประชาชน : {p.get('idNumber', '-')}\n⏳ อายุ : {p.get('age', '-')} ปี")
                embed = discord.Embed(title="🔍 ผลการค้นหาฐานข้อมูลชื่อ", color=0x3498db, description=f"```yaml\n{info}\n```")
                await result_channel.send(embed=embed)

        elif self.endpoint == "transport.php":
            all_items = find_mobile_items(raw_data)
            if not all_items: return await result_channel.send(f"⚠️ {user.mention} ไม่พบประวัติขนส่ง")
            msg = await result_channel.send(f"🛰️ **SLUMZICK SCANNER:** กำลังกวาดข้อมูลขนส่งพาร์ทเนอร์...")
            await asyncio.sleep(1)
            for item in all_items:
                name = item.get('name') or item.get('ชื่อ') or "-"
                info = (f"📦 สถานะ : พัสดุถูกบันทึกเรียบร้อย\n👤 ผู้รับ : {name}\n📱 ติดต่อ : {item.get('มือถือ', '-')}\n🏠 ที่อยู่ : {item.get('detail_address', '-')}\n🏙️ พื้นที่ : {item.get('จังหวัด', '-')} | {item.get('อำเภอ', '-')}\n📅 บันทึกเมื่อ : {item.get('สร้างเมื่อ', '-')}")
                embed = discord.Embed(title="🚚 TRANSPORT LOGISTICS DATA", color=0x9b59b6, description=f"```yaml\n{info}\n```")
                embed.set_author(name="SLUMZICK SHOP PARTNER", icon_url="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3Z6eXN6eXN6eXN6eXN6eXN6eXN6eXN6eXN6eXN6eXN6eXN6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpx4tqhP0V-o/giphy.gif")
                embed.set_footer(text=f"SLUMZICK DATABASE SYSTEM | ID: {item.get('รหัส', '-')}")
                await result_channel.send(embed=embed)
            await msg.delete()

class PersistentView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="ค้นชื่อ", style=discord.ButtonStyle.primary, emoji="🔍", custom_id="sl_n")
    async def b1(self, i, b): await i.response.send_modal(InputModal("ชื่อ-นามสกุล", "name.php"))
    @discord.ui.button(label="สปสช", style=discord.ButtonStyle.success, emoji="🏥", custom_id="sl_h")
    async def b2(self, i, b): await i.response.send_modal(InputModal("เลขบัตรประชาชน", "nhso.php"))
    @discord.ui.button(label="ทรู", style=discord.ButtonStyle.danger, emoji="📡", custom_id="sl_t")
    async def b3(self, i, b): await i.response.send_modal(InputModal("เบอร์โทรศัพท์", "true.php"))
    @discord.ui.button(label="ขนส่ง", style=discord.ButtonStyle.secondary, emoji="📦", custom_id="sl_tr")
    async def b4(self, i, b): await i.response.send_modal(InputModal("เบอร์โทรศัพท์", "transport.php"))

@bot.command(name="setup")
async def setup(ctx):
    if ctx.author.id != OWNER_ID: return
    file = discord.File("sm.png", filename="sm.png")
    embed = discord.Embed(
        title="👑 SLUMZICK SHOP - THE ULTIMATE DATABASE 👑",
        description=(
            "## 🔱 ยินดีต้อนรับสู่ขุมพลังข้อมูลส่วนบุคคล\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔥 **SERVICES SELECTION**\n"
            "> **` 🔍 ค้นชื่อ `** : เจาะฐานข้อมูลราษฎร์ทั่วประเทศ\n"
            "> **` 🏥 สปสช   `** : ตรวจสอบสิทธิและผังครอบครัว\n"
            "> **` 📡 ทรู     `** : แกะรอยเจ้าของเบอร์และที่อยู่\n"
            "> **` 📦 ขนส่ง   `** : ดึงประวัติการสั่งพัสดุเรียลไทม์\n\n"
            "✨ *กรุณาเลือกปุ่มด้านล่างเพื่อเข้าถึงข้อมูลระดับ VIP*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🛡️ **SYSTEM SLUMM: [ 🟢 ONLINE & SECURED ]**"
        ), color=0x2b2d31
    )
    embed.set_image(url="attachment://sm.png")
    embed.set_thumbnail(url="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3Z6eXN6eXN6eXN6eXN6eXN6eXN6eXN6eXN6eXN6eXN6eXN6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpx4tqhP0V-o/giphy.gif")
    embed.set_footer(text="SLUMZICK SHOP | THE BEST DATABASE PROVIDER", icon_url="https://cdn-icons-png.flaticon.com/512/252/252030.png")
    await ctx.send(file=file, embed=embed, view=PersistentView())

bot.run(TOKEN)
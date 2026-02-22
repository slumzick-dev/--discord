# SLUMZICK SHOP - Discord Bot (Ultimate UI & Deep Scan)

README ฉบับภาษาไทย — คู่มือการติดตั้งและใช้งานแบบละเอียดสำหรับโค้ดบอท Discord ที่ส่งคำค้นไปยัง API ภายนอก (nhso.php, true.php, name.php, transport.php) และแสดงผลเป็น Embeds พร้อม Modal UI และ Persistent Buttons

> หมายเหตุสำคัญด้านกฎหมายและจริยธรรม  
> โค้ดนี้จัดการข้อมูลส่วนบุคคล (เช่น เลขบัตรประชาชน, ที่อยู่, วันเกิด) หากคุณไม่มีสิทธิ์ทางกฎหมายชัดเจนในการเข้าถึง/เผยแพร่ข้อมูลเหล่านี้ วางไฟล์ในตำแหน่งเดียวกับสคริปต์หรือแก้พาธให้ถูกต้อง การใช้งานที่ไม่ถูกต้องอาจละเมิด PDPA/GDPR หรือกฎหมายท้องถิ่น และขัดต่อเงื่อนไขการให้บริการของ API ต้นทางและ Discord

---

สารบัญ
- คุณสมบัติหลัก
- ความต้องการเบื้องต้น
- เตรียม Discord Application & Bot
- ตัวแปรสภาพแวดล้อม (.env)
- ติดตั้งและรัน
- คำสั่ง และ ปุ่ม UI
- การปรับแต่งที่แนะนำ (ความปลอดภัย / ประสิทธิภาพ)
- ปัญหาที่พบบ่อย และวิธีแก้
- ตัวอย่างไฟล์ที่จำเป็น
- License / สรุป

---

คุณสมบัติหลัก
- Modal-based inputs (discord.ui.Modal) เพื่อรับข้อมูลจากผู้ใช้
- PersistentView ปุ่ม 4 ปุ่ม (ค้นชื่อ, สปสช, ทรู, ขนส่ง)
- เรียก API ภายนอกผ่าน aiohttp และแสดงผลด้วย Embed
- ฟังก์ชัน deep scan สำหรับ JSON ที่ซ้อน (ค้น key `mobileItems`)
- ฟังก์ชันสร้าง Embed แบบเฉพาะสำหรับข้อมูลสปสช

ความต้องการเบื้องต้น
- Python 3.10+ แนะนำ 3.11
- อินเทอร์เน็ตเพื่อเข้าถึง BASE_URL ของ API
- สิทธิ์เข้าถึง Discord Developer Portal (สร้าง Bot &ตั้งค่า)
- ไฟล์ภาพ `sm.png` (ใช้กับคำสั่ง setup) วางไว้ในไดเรกทอรีเดียวกับไฟล์บอท
- ควรใช้งานใน environment ปลอดภัย (เช่น server หรือ container ที่มีการจัดการ secrets)

เตรียม Discord Application & Bot
1. เข้าไปที่ https://discord.com/developers/applications
2. สร้าง Application ใหม่ -> ไปที่ "Bot" -> Add Bot
3. จดค่า BOT TOKEN (ใส่ในไฟล์ .env)
4. เปิด Privileged Gateway Intents ถ้าจำเป็น:
   - MESSAGE CONTENT INTENT: จำเป็นถ้าคุณต้องการให้ bot รับคำสั่ง prefix แบบข้อความ (`!setup`) เพราะ commands.Bot แบบ prefix ใช้ message content
   - (ถ้าไม่ต้องการ prefix commands ให้พิจารณาเปลี่ยนเป็น slash commands แทน)
5. ใน OAuth2 -> URL Generator:
   - Scopes: bot, applications.commands (ถาต้องการ slash commands)
   - Permissions: เลือกอย่างน้อย Send Messages, Embed Links, Attach Files, Use Slash Commands (หรือใส่ permission integer ตามต้องการ)
6. ใช้ URL ที่ได้เพื่อเชิญบอทเข้าร่วมเซิร์ฟเวอร์ของคุณ

ตัวแปรสภาพแวดล้อม (.env)
- ห้าม hardcode token ในโค้ดกลาง โค้ดตัวอย่างแนะนำเก็บใน environment variables
- ตัวแปรที่ต้องเตรียม:
  - DISCORD_TOKEN — token ของ bot
  - API_TOKEN — token สำหรับ API ภายนอก (ค่าในโค้ดเดิมเป็น "zick")
  - BASE_URL — URL พื้นฐานของ API (เช่น https://slumzick.xyz)
  - OWNER_ID — ไอดีของเจ้าของบอท (integer) เพื่อจำกัดคำสั่ง setup
  - RESULT_CHANNEL_ID — channel id ที่บอทจะส่งผลลัพธ์

ตัวอย่างไฟล์ .env (อย่าลืมเก็บเป็นความลับ)
```env
DISCORD_TOKEN=your_discord_bot_token_here
API_TOKEN=zick
BASE_URL=https://slumzick.xyz
OWNER_ID=1074621727541317712
RESULT_CHANNEL_ID=1474880810136895498
```

ติดตั้งและรัน
1. สร้าง virtual environment (แนะนำ)
```bash
python -m venv venv
source venv/bin/activate     # Linux / macOS
venv\Scripts\activate        # Windows
```

2. ติดตั้ง dependencies
```bash
pip install -r requirements.txt
```

3. ตั้งค่าไฟล์ `.env` หรือ export environment variables ตามระบบปฏิบัติการ
- Linux/macOS:
```bash
export DISCORD_TOKEN="..."
export API_TOKEN="..."
export BASE_URL="https://slumzick.xyz"
export OWNER_ID="1074621727541317712"
export RESULT_CHANNEL_ID="1474880810136895498"
```

4. วางไฟล์ `sm.png` ในโฟลเดอร์เดียวกับ bot script (ไฟล์ที่ส่งโดยคำสั่ง setup)

5. รันบอท
```bash
python bot.py
```
(��ปลี่ยนชื่อไฟล์เป็นไฟล์บอทของคุณ — หากไฟล์ของคุณชื่อ `main.py` ให้รัน `python main.py`)

คำสั่ง และ ปุ่ม UI
- คำสั่ง prefix:
  - `!setup` — ส่ง embed พร้อมภาพและ PersistentView (ปุ่ม) เพื่อให้ผู้ใช้กด (จำกัดเฉพาะ OWNER_ID เท่านั้น)
- ปุ่ม UI (PersistentView):
  - ค้นชื่อ (🔍) — เปิด Modal เพื่อค้นหาจาก `name.php`
  - สปสช (🏥) — เปิด Modal เพื่อค้นจาก `nhso.php`
  - ทรู (📡) — เปิด Modal เพื่อค้นจาก `true.php`
  - ขนส่ง (📦) — เปิด Modal เพื่อค้นจาก `transport.php`
- ผลลัพธ์ทั้งหมดจะถูกส่งไปที่ช่องที่กำหนดด้วย `RESULT_CHANNEL_ID`

การปรับแต่งที่แนะนำ (ความปลอดภัย / ประสิทธิภาพ)
- เก็บ tokens ใน secret manager หรือ environment variables (ไม่ commit สู่ git)
- สร้างและ reuse aiohttp.ClientSession แทนการเปิด session ใหม่ทุกครั้ง
- จับ exception เฉพาะ (เช่น aiohttp.ClientError, asyncio.TimeoutError) และ log ข้อผิดพลาดด้วย `logging`
- เพิ่ม rate-limiting / per-user cooldown เพื่อป้องกัน abuse และลดการเรียก API ที่เยอะ
- ตรวจสอบ `result_channel = bot.get_channel(RESULT_CHANNEL_ID)` ว่าไม่เป็น None และบอทมี permission ในช่องนั้นก่อนส่ง
- ลด scope ของ intents — ขอแค่ intents ที่ต้องใช้จริง ๆ (เช่น messages, guilds, message_content ถ้าต้องการ)
- เปลี่ยน prefix commands เป็น slash commands (application commands) เพื่อความปลอดภัยและ UX ที่ดีกว่า
- ทำ input validation ให้แน่นขึ้น (เช็ครูปแบบ PID, เบอร์โทร, ความยาวข้อความ)

ปัญหาที่พบบ่อย และวิธีแก้
- bot ไม่ตอบคำสั่ง prefix: ตรวจสอบว่าได้เปิด MESSAGE CONTENT INTENT ใน Developer Portal และ enable ในโค้ด (`discord.Intents`). หากต้องการหลีกเลี่ยง intent นี้ ให้ใช้ slash commands
- result_channel เป็น None: ตรวจสอบ ID ให้ถูกต้อง บอทต้องอยู่ใน guild เดียวกับช่อง และช่องต้องมีสิทธิ์ส่งข้อความ
- FileNotFoundError สำหรับ `sm.png`: วางไฟล์ในตำแหน่งเดียวกับสคริปต์หรือแก้พาธให้ถูกต้อง
- Rate limit / API timeouts: เพิ่ม timeout และ retry/backoff, พิจารณา caching เพื่อหลีกเลี่ยงการเรียกซ้ำบ่อย

ตัวอย่างการปรับโค้ดสั้น ๆ (อ่าน env ในโค้ด)
```python
import os
TOKEN = os.environ.get("DISCORD_TOKEN")
API_TOKEN = os.environ.get("API_TOKEN", "zick")
BASE_URL = os.environ.get("BASE_URL", "https://slumzick.xyz")
OWNER_ID = int(os.environ.get("OWNER_ID", "1074621727541317712"))
RESULT_CHANNEL_ID = int(os.environ.get("RESULT_CHANNEL_ID", "1474880810136895498"))
```

ข้อควรระวังด้านกฎหมายและนโยบาย
- ห้ามใช้เพื่อกระทำการที่ผิดกฎหมาย เช่น ใช้ข้อมูลส่วนบุคคลโดยไม่ได้รับอนุญาต ปลอมแปลงข้อมูล หรือคุกคามผู้อื่น
- ตรวจสอบ Terms of Service ของ API ต้นทางว่าการเรียกข้อมูลและการเผยแพร่เป็นไปตามข้อกำหนดหรือไม่
- หากให้บริการแก่บุคคลอื่น ควรมีนโยบายความเป็นส่วนตัวและระบบ logging/consent ที่ชัดเจน

ไฟล์ตัวอย่างที่จำเป็น
- bot script (เช่น `bot.py`) — โค้ดที่คุณให้มา
- `sm.png` — รูปภาพสำหรับคำสั่ง setup
- `.env` — ตัวแปรสภาพแวดล้อม
- `requirements.txt` — รายการ dependencies (ตัวอย่างแนบด้านล่าง)

การ deploy (แนะนำ)
- ใช้ process manager เช่น systemd / docker / docker-compose / pm2 (สำหรับ node) เพื่อรันบอทแบบ persist
- ใน Docker: เก็บ secrets ผ่าน Docker secrets หรือ environment variables ของ container runtime
- ใช้ monitoring และ logging (เช่น Prometheus/Grafana หรือ simple file logs)

License / สรุป
- README นี้เป็นคู่มือการติดตั้งและใช้งานเท่านั้น — โค้ดต้นฉบับและการใช้งานจริงเป็นความรับผิดชอบของผู้ใช้งาน
- โปรดปฏิบัติตามกฎหมายท้องถิ่นและนโยบายแพลตฟอร์มในการใช้งานข้อมูลส่วนบุคคล

หากต้องการ ผมช่วย:
- แก้โค้ดให้ใช้ environment variables เต็มรูปแบบ
- แก้ให้ reuse aiohttp.ClientSession และเพิ่ม logging
- เปลี่ยนเป็น slash commands (application commands) แทน prefix command
- เพิ่ม cooldown / rate limit ตัวอย่าง
บอกได้เลยว่าต้องการให้ผมทำจุดไหนต่อเป็นอันดับแรก

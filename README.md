# ⚽ FPL Analytics & Week-by-Week Strategy Dashboard

ระบบวิเคราะห์และวางแผนทีม Fantasy Premier League (FPL) สำหรับทีม **GEMINI UNITED** (Team ID: `306983`)

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```text
FPL/
├── data/                         # เก็บข้อมูล JSON แคชจาก Official FPL API
│   ├── bootstrap_static.json     # สถิตินักเตะและทีมทั้งหมดในพรีเมียร์ลีก
│   ├── fixtures.json             # โปรแกรมแข่งขันและความยากง่าย (FDR)
│   ├── entry.json                # ข้อมูลโปรไฟล์ทีมและอันดับ
│   ├── history.json              # ประวัติคะแนนย้อนหลังแต่ละสัปดาห์
│   └── picks_gw*.json            # รายชื่อตัวจริง/ตัวสำรองแต่ละ Gameweek
├── fetch_fpl_data.py             # สคริปต์ดึงข้อมูลล่าสุดจาก FPL API
├── generate_presentation.py      # สคริปต์ประมวลผลสถิติและสร้าง HTML Presentation
├── index.html                    # Dashboard / Presentation ล่าสุด (ดับเบิลคลิกเปิดบนเบราว์เซอร์ได้ทันที)
└── fpl_gw3_presentation.html     # สรุปและแผนงานประจำ Gameweek 3
```

---

## 🚀 วิธีใช้งานในแต่ละสัปดาห์ (Week-by-Week Workflow)

เมื่อถึงสัปดาห์ใหม่ หรือก่อนเดดไลน์แต่ละ Gameweek:

1. **บอกให้ผมช่วยอัปเดตและวิเคราะห์ให้ได้ทันที** ในแชตนี้
2. หรือรันคำสั่งดึงข้อมูลและอัปเดตไฟล์ HTML เองผ่าน Terminal:
   ```bash
   python3 fetch_fpl_data.py --team-id 306983
   python3 generate_presentation.py --out index.html
   ```
3. ดับเบิลคลิกเปิดไฟล์ `index.html` หรือ `fpl_gw3_presentation.html` บน Google Chrome / Safari / Edge เพื่อดูสรุปจัดตัวได้เลย!

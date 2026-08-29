# FPL Project Operational Rules & Workflow

ข้อกำหนดและมาตรฐานการวิเคราะห์ทีม **GEMINI UNITED (ID: 306983)** ทุกสัปดาห์:

---

### 1. กฎการอัปเดต Presentation & GitHub Pages อัตโนมัติ (Automated Workflow)
* ทุกครั้งที่มีการวิเคราะห์ทีมประจำสัปดาห์หรืออัปเดต Gameweek ใหม่ ระบบจะทำหน้าที่อัตโนมัติครบวงจร:
  1. ดึงข้อมูลจริงล่าสุดจาก Official FPL API และ Solio Analytics API
  2. รันสคริปต์ `generate_presentation.py` เพื่อสร้างและอัปเดตไฟล์ `index.html` และ `fpl_gw{X}_presentation.html`
  3. สั่งคำสั่ง Git เพื่อ Commit และ Push ขึ้น GitHub (`origin/main`) โดยอัตโนมัติทันที เพื่อให้หน้าเว็บออนไลน์ที่ GitHub Pages อัปเดตเอง
  4. สรุปผลวิเคราะห์ในแชต พร้อมแนบลิงก์ให้เปิดดูไฟล์ Presentation ทันที

---

### 2. มาตรฐานการออกแบบ (Design Standards)
* **Zero Emojis:** งดการใช้อีโมจิทุกชนิดในไฟล์ Presentation, โค้ด และรายงานสรุป
* **Dark Minimalist Theme:** ใช้โทนสีมืดสุขุม (Deep Charcoal / Midnight Slate `#090c10`, `#0f141c`, `#151b26`) และตัดเฉดสี Gemini ม่วง/ชมพูออกทั้งหมด
* **Analytical Accents:** ใช้สีเฉพาะข้อมูลเชิงสถิติ เช่น Emerald (`#10b981`), Sky Blue (`#38bdf8`), และ Amber (`#f59e0b`)

---

### 3. การผสาน 5 แหล่งข้อมูลการวิเคราะห์ (5 Intelligence Sources)
1. **Fantasy Football Scout:** ข่าวงานแถลงข่าว (Press Conferences), รายงานอาการบาดเจ็บ และไลน์อัปหลุดก่อนเดดไลน์ (Early Leaks)
2. **Solio Analytics:** โมเดล AI จำลองแต้มล่วงหน้า (Projected Points), ค่าความต่าง (Differentials) และคลีนชีต
3. **Coach FPL FDR:** ตารางความยากง่ายโปรแกรมระยะยาว (GW3 - GW38) และการจับคู่โรเตชั่นแนวรับ
4. **LiveFPL:** อันดับสดเรียลไทม์, Effective Ownership (EO%) และการวิเคราะห์กลุ่ม Top 10k
5. **FPL Gameweek:** ระบบติดตามคู่แข่งในมินิลีก, แต้มสดพร้อม Live BPS และระบบคำนวณตัวสำรองอัตโนมัติ

---

### 4. นโยบายการบริหารทีมระยะยาว (Long-Term Low Turnover Policy)
* **No Deadweight Bench:** ตัวสำรองทุกคนต้องเป็นตัวจริงที่ลงเล่น 90 นาทีจริงในพรีเมียร์ลีก
* **Target:** จบฤดูกาลในอันดับ **Top 100k**

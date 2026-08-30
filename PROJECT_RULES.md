# FPL Project Operational Rules & Workflow

ข้อกำหนดและมาตรฐานการวิเคราะห์ทีม **GEMINI UNITED (ID: 306983)**:

---

### 1. กฎการดึงข้อมูลสดก่อนตอบทุกครั้ง (Mandatory Live API Fetch Protocol)
* **Live Fetch on Every Query :** ทุกครั้งที่มีคำถามจากผู้จัดการทีม ไม่ว่าจะเป็นการวิเคราะห์ทีม, การถามข้อมูลนักเตะ, หรือคำถามทั่วไป ระบบจะต้องทำการ Re-fetch ข้อมูลสดล่าสุดจาก **Official FPL API** (`entry/306983/`, `entry/306983/history/`, `bootstrap-static/`, `fixtures/`) และ **Solio Analytics API** ทันที ก่อนเริ่มการคำนวณและตอบคำถามเสมอ เพื่อให้ได้ตัวเลขราคา, สถานะอาการบาดเจ็บ, สถิติ xGI และข้อมูลที่ถูกต้องเป็นปัจจุบัน 100%
* **Local-First Presentation :** การสร้างและแก้ไขไฟล์ Presentation จะทำในเครื่อง Local เสมอ (`index.html` และ `fpl_gw{X}_presentation.html`)
* **Explicit GitHub Push Only :** ทำการ Push ขึ้น GitHub ต่อเมื่อผู้จัดการทีมมีคำสั่งแจ้งอย่างชัดเจนเท่านั้น

---

### 2. ข้อกำหนดการทำงานของ 2 แผน (Choice 1 vs Choice 2 Protocols)

#### Choice 1 : แผนที่ผู้จัดการทีมตัดสินใจเลือกเอง (Manager Dynamic Selection)
* **บทบาทของ AI :** ทำหน้าที่เป็น **ผู้ตรวจสอบแท็กติก (Tactical Auditor)**
* **แนวทางปฏิบัติ :** **ไม่อนุมานหรือใส่ข้อสันนิษฐานวิธีคิดแทนผู้จัดการทีม** เพราะผู้จัดการทีมปรับแก้ข้อมูลอย่าง Dynamic ด้วยตนเองตลอดเวลา เมื่อผู้จัดการทีมส่งไลน์อัปเข้ามา AI จะทำการวิเคราะห์และคอมเมนต์เฉพาะ **"จุดแข็ง (Strengths) และ จุดอ่อน (Weaknesses)"** เท่านั้น

#### Choice 2 : The Master Fortress Blueprint (AI Autonomous Optimization)
* **บทบาทของ AI :** ทำหน้าที่เป็น **ผู้วางแผนกลยุทธ์อิสระ 100% (Master Strategist)**
* **แนวทางปฏิบัติ :** 
  * AI มีสิทธิ์ตัดสินใจจัดตัว เข้า-ออก วางกัปตัน และวางแผนระยะยาวตลอด 38 Gameweek ได้เอง 100% โดยอิงจาก 5 แหล่งข้อมูลวิจัยเชิงปริมาณ
  * **การตรวจสอบชิปแบบ Real-Time :** ทุกครั้งที่มีการแนะนำการจัดตัวประจำสัปดาห์ ระบบจะเชื่อมต่อไปยัง `https://fantasy.premierleague.com/api/entry/306983/history/` โดยอัตโนมัติ เพื่อเช็กสถานะชิปที่เหลืออยู่จริงของทีม ID 306983, จำนวนโควตา Free Transfers สะสม และเงินใน Bank ก่อนตัดสินใจว่าจะเปิดใช้การ์ด/ชิปใดในสัปดาห์นั้น
  * ยึดมั่นใน **ปรัชญา Low-Turnover & 2-FT Buffer** (โครงสร้างพื้นฐานแน่น, Zero Deadweight ตัวจริง 90 นาทีครบทั้ง 15 คน)
  * **ทุกครั้งที่ผู้จัดการทีมสั่งให้อัปเดตหรือแนะนำแผนประจำสัปดาห์ AI จะทำการปรับปรุงเฉพาะ Choice 2 นี้ด้วยข้อมูล Real-Time ณ วินาทีนั้นเสมอ**

---

### 3. มาตรฐานการออกแบบ (Design Standards)
* **Zero Emojis :** งดการใช้อีโมจิทุกชนิดในไฟล์ Presentation, โค้ด และรายงานสรุป 100%
* **Dark Minimalist Theme :** ใช้โทนสีมืดสุขุม (Deep Charcoal / Midnight Slate `#090c10`, `#0f141c`, `#151b26`) และตัดเฉดสี Gemini ม่วง/ชมพูออกทั้งหมด
* **Analytical Accents :** ใช้สีเฉพาะข้อมูลเชิงสถิติ เช่น Emerald (`#10b981`), Sky Blue (`#38bdf8`), และ Amber (`#f59e0b`)

---

### 4. การผสาน 5 แหล่งข้อมูลการวิเคราะห์ (5 Intelligence Sources)
1. **Fantasy Football Scout :** ข่าวงานแถลงข่าว (Press Conferences), รายงานอาการบาดเจ็บ และไลน์อัปหลุดก่อนเดดไลน์ (Early Leaks)
2. **Solio Analytics :** โมเดล AI จำลองแต้มล่วงหน้า (Projected Points), ค่าความต่าง (Differentials) และคลีนชีต
3. **Coach FPL FDR :** ตารางความยากง่ายโปรแกรมระยะยาว (GW3 - GW38) และการจับคู่โรเตชั่นแนวรับ
4. **LiveFPL :** อันดับสดเรียลไทม์, Effective Ownership (EO%) และการวิเคราะห์กลุ่ม Top 10k
5. **FPL Gameweek :** ระบบติดตามคู่แข่งในมินิลีก, แต้มสดพร้อม Live BPS และระบบคำนวณตัวสำรองอัตโนมัติ

---

### 5. นโยบายการบริหารทีมระยะยาว (Long-Term Low Turnover Policy)
* **No Deadweight Bench :** ตัวสำรองทุกคนต้องเป็นตัวจริงที่ลงเล่นจริงในพรีเมียร์ลีก
* **Target :** จบฤดูกาลในอันดับ **Top 100k**

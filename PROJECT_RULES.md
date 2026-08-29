# FPL Project Operational Rules & Workflow

ข้อกำหนดและมาตรฐานการวิเคราะห์ทีม **GEMINI UNITED (ID: 306983)**:

---

### 1. นโยบายการอัปเดต Presentation & GitHub Push (Local-First Workflow)
* **Local-First Always :** ทุกครั้งที่มีการวิเคราะห์ทีมหรือปรับเปลี่ยนผังไลน์อัป ระบบจะสร้างและอัปเดตไฟล์ Presentation ในเครื่อง Local เท่านั้น (`index.html` และ `fpl_gw{X}_presentation.html`) เพื่อให้ผู้จัดการทีมตรวจเช็กในเครื่องก่อน
* **Explicit GitHub Push Only :** **ห้ามสั่ง Git Push ขึ้น GitHub โดยอัตโนมัติเด็ดขาด** จะทำการ Push ไฟล์ขึ้น GitHub ต่อเมื่อผู้จัดการทีมมีคำสั่งแจ้งอย่างชัดเจนเท่านั้น (เช่น "อัปโหลดขึ้น GitHub", "Push ขึ้น GitHub")

---

### 2. มาตรฐานการออกแบบ (Design Standards)
* **Zero Emojis :** งดการใช้อีโมจิทุกชนิดในไฟล์ Presentation, โค้ด และรายงานสรุป 100%
* **Dark Minimalist Theme :** ใช้โทนสีมืดสุขุม (Deep Charcoal / Midnight Slate `#090c10`, `#0f141c`, `#151b26`) และตัดเฉดสี Gemini ม่วง/ชมพูออกทั้งหมด
* **Analytical Accents :** ใช้สีเฉพาะข้อมูลเชิงสถิติ เช่น Emerald (`#10b981`), Sky Blue (`#38bdf8`), และ Amber (`#f59e0b`)

---

### 3. การผสาน 5 แหล่งข้อมูลการวิเคราะห์ (5 Intelligence Sources)
1. **Fantasy Football Scout :** ข่าวงานแถลงข่าว (Press Conferences), รายงานอาการบาดเจ็บ และไลน์อัปหลุดก่อนเดดไลน์ (Early Leaks)
2. **Solio Analytics :** โมเดล AI จำลองแต้มล่วงหน้า (Projected Points), ค่าความต่าง (Differentials) และคลีนชีต
3. **Coach FPL FDR :** ตารางความยากง่ายโปรแกรมระยะยาว (GW3 - GW38) และการจับคู่โรเตชั่นแนวรับ
4. **LiveFPL :** อันดับสดเรียลไทม์, Effective Ownership (EO%) และการวิเคราะห์กลุ่ม Top 10k
5. **FPL Gameweek :** ระบบติดตามคู่แข่งในมินิลีก, แต้มสดพร้อม Live BPS และระบบคำนวณตัวสำรองอัตโนมัติ

---

### 4. นโยบายการบริหารทีมระยะยาว (Long-Term Low Turnover Policy)
* **No Deadweight Bench :** ตัวสำรองทุกคนต้องเป็นตัวจริงที่ลงเล่น 90 นาทีจริงในพรีเมียร์ลีก
* **Target :** จบฤดูกาลในอันดับ **Top 100k**

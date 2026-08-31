# FPL Project Operational Rules & Workflow

ข้อกำหนดและมาตรฐานการวิเคราะห์ทีม **GEMINI UNITED (ID: 306983)**:

---

### 1. กฎการดึงข้อมูลสดก่อนตอบทุกครั้ง (Mandatory Live API Fetch Protocol)
* **Live Fetch on Every Query :** ทุกครั้งที่มีคำถามจากผู้จัดการทีม ไม่ว่าจะเป็นการวิเคราะห์ทีม, การถามข้อมูลนักเตะ, หรือคำถามทั่วไป ระบบจะต้องทำการ Re-fetch ข้อมูลสดล่าสุดจาก **Official FPL API** (`entry/306983/`, `entry/306983/history/`, `bootstrap-static/`, `fixtures/`) และ **Solio Analytics API** ทันที ก่อนเริ่มการคำนวณและตอบคำถามเสมอ เพื่อให้ได้ตัวเลขราคา, สถานะอาการบาดเจ็บ, สถิติ xGI และข้อมูลที่ถูกต้องเป็นปัจจุบัน 100%
* **Local-First Presentation :** การสร้างและแก้ไขไฟล์ Presentation จะทำในเครื่อง Local เสมอ (`index.html` และ `fpl_gw{X}_presentation.html`)
* **Explicit Manual GitHub Push Only (ห้าม Auto-Push เด็ดขาด) :** ทุกการแก้ไขโค้ด, ปรับดีไซน์ หรืออัปเดตบทวิเคราะห์ จะต้องทำและตรวจสอบในเครื่อง Local เท่านั้น **ห้ามทำการ `git push` ขึ้น GitHub โดยอัตโนมัติเด็ดขาด** จนกว่าผู้จัดการทีมจะมีคำสั่ง Manual แจ้งให้อัปโหลดอย่างชัดเจน (เช่น "อัปโหลดข้อมูลลง github" หรือ "push ขึ้น github") เท่านั้น

---

### 2. ข้อกำหนดการทำงานของ 2 แผน (Choice 1 vs Choice 2 Protocols)

#### Choice 1 : แผนที่ผู้จัดการทีมตัดสินใจเลือกเอง (Manager Dynamic Selection)
* **บทบาทของ AI :** ทำหน้าที่เป็น **ผู้ตรวจสอบแท็กติก (Tactical Auditor)**
* **แนวทางปฏิบัติ :** **ไม่อนุมานหรือใส่ข้อสันนิษฐานวิธีคิดแทนผู้จัดการทีม** เพราะผู้จัดการทีมปรับแก้ข้อมูลอย่าง Dynamic ด้วยตนเองตลอดเวลา เมื่อผู้จัดการทีมส่งไลน์อัปเข้ามา AI จะทำการวิเคราะห์และคอมเมนต์เฉพาะ **"จุดแข็ง (Strengths) และ จุดอ่อน (Weaknesses)"** เท่านั้น

#### Choice 2 : The Master Fortress Blueprint (AI Autonomous Optimization)
* **บทบาทของ AI :** ทำหน้าที่เป็น **ผู้วางแผนกลยุทธ์อิสระ 100% (Master Strategist)**
* **แนวทางปฏิบัติ :** 
  * AI มีสิทธิ์ตัดสินใจจัดตัว เข้า-ออก วางกัปตัน และวางแผนระยะยาวตลอด 38 Gameweek ได้เอง 100% โดยอิงจาก 5 แหล่งข้อมูลวิจัยเชิงปริมาณ
  * **การคำนวณและวางแผนระยะยาว 38 Gameweek พร้อมชิป (38-GW Long-Term & 8-Chip Calculation) :** 
    * ทุกครั้งที่ผู้จัดการทีมสั่งให้วางแผนการจัดตัวในแต่ละ Gameweek ระบบจะต้องคำนวณเงื่อนไขทั้งหมดที่ผู้จัดการทีมกำหนดไว้ (ปรัชญา Low-Turnover, Zero Deadweight 15 ตัวจริง 90 นาที, การรักษา 2-FT Buffer)
    * คำนวณและจำลองจังหวะการใช้ชิปทั้งหมดตลอด 38 Gameweek (Wildcard 1/2, Bench Boost 1/2, Triple Captain 1/2, Free Hit 1/2) โดยดึงข้อมูลประวัติการใช้ชิปจริงจาก `https://fantasy.premierleague.com/api/entry/306983/history/` มาประมวลผลสด
    * ผสานข้อมูลจาก **5 แหล่งข้อมูลวิจัย** (Official FPL API, Solio Analytics, Coach FPL FDR, LiveFPL, FPL Gameweek) ในการคัดเลือก 11 ตัวจริง, กัปตัน (C), รองกัปตัน (VC) และลำดับตัวสำรอง (Sub 1, 2, 3)
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

---

### 6. ข้อกำหนดการอัปเดตแท็บ Plan Summary และความสอดคล้องของมูลค่าทีม (Mandatory Synchronized Plan Summary & Valuation Protocol)
* **ซิงค์บทวิเคราะห์และราคานักเตะทุกครั้ง (Always-In-Sync) :** 
  * ทุกครั้งที่ผู้จัดการทีมส่งไลน์อัปอัปเดตทีมใน **Choice 1** 
  * และทุกครั้งที่ผู้จัดการทีมสั่งให้อัปเดตหรือวางแผนทีมก่อนเตะในแต่ละ Gameweek สำหรับ **Choice 2**
  * **ระบบจะต้องทำการอัปเดตแท็บ `Plan Summary` (`#tab-summary`) พร้อมกันเสมอ** โดยกลั่นกรองและแจกแจง:
    1. **ข้อดีและจุดแข็ง (Strengths & Pros)** และ **ข้อเสียและจุดที่ต้องระวัง (Weaknesses & Cons)** ของทั้งสอง Choice ให้สอดคล้องกับไลน์อัป, สถิติ xGI, โปรแกรมการแข่งขัน, การจัดตัวจริง/สำรอง, เม็ดเงิน Benched Capital และสถานะการ์ด/ชิป ณ ขณะนั้นอย่างแม่นยำ 100%
    2. **ความสอดคล้องของราคานักเตะและมูลค่าทีม (100% Price & Team Value Consistency) :** ราคานักเตะทุกคนที่ระบุในบทวิเคราะห์ (เช่น `£X.Xm`), มูลค่ารวมของทีม (Squad Cost), และเงินคงเหลือในบัญชี (Bank Buffer) จะต้องคำนวณจากฐานข้อมูล Official API สด และต้องแสดงผลตัวเลขที่ตรงกันทุกจุดอย่างสมบูรณ์แบบ (ตั้งแต่กล่อง Header ด้านบน, ป้าย Badge บนผังสนาม Plan Lineup, จนถึงหัวข้อและเนื้อหาในแท็บ Plan Summary)

---

### 7. สถาปัตยกรรมการทำงานระบบไฮบริด (The Hybrid Dual-Engine Architecture)
ระบบถูกออกแบบให้ทำงานร่วมกันแบบ 2 โหมดคู่ขนาน (Hybrid Dual-Engine):
1. **Choice 1 : Manager Dynamic Mode (Manual Control & Auditor)**
   * ควบคุมและตัดสินใจโดยผู้จัดการทีม 100%
   * จัดการและทดสอบในเครื่อง Local เสมอ และจะ Push ขึ้น GitHub ต่อเมื่อผู้จัดการทีมมีคำสั่ง Manual ชัดเจนเท่านั้น
2. **Choice 2 : Autonomous Cloud Engine (15-Minute Cron on GitHub Actions)**
   * ควบคุมและคำนวณโดย AI อิสระ 100% ผ่านระบบ GitHub Actions Workflow (`.github/workflows/hybrid_choice2_cron.yml`)
   * **รอบการทำงานอัตโนมัติ (Every 15 Minutes) :** ระบบใน Cloud จะดึงข้อมูลสดจาก 5 แหล่งวิจัยทุกๆ 15 นาที เพื่อตรวจสอบความฟิต, ราคาตลาด, ข่าวงานแถลงข่าว และอัตรา Clean Sheet
   * **จุดตัดยอดไฟนอล (Final Lockdown at Deadline - 30m) :** ระบบจะล็อกการจัดทัพ 11 ตัวจริง, กัปตัน [C], รองกัปตัน [VC], ลำดับม้านั่งสำรอง และ Re-compile หน้าเว็บอัตโนมัติก่อนเริ่มแต่ละ Gameweek 30 นาทีพอดี


# FPL Research Sources & Analytical Framework

ชุดเครื่องมือและเว็บไซต์วิเคราะห์ 5 แหล่งที่บันทึกไว้ในโปรเจกต์นี้ เพื่อใช้ในการวิเคราะห์ทีม **GEMINI UNITED (ID: 306983)** ทุกๆ สัปดาห์:

---

### 1. Solio Analytics (`https://fpl.solioanalytics.com`)
* **บทบาทหลัก:** การคำนวณสถิติคาดการณ์ด้วย AI (Expected Projections & Optimization Solver)
* **ข้อมูลที่ดึงมาใช้อัตโนมัติ:**
  - **Projected Points:** แต้มที่คาดการณ์ของนักเตะแต่ละคนใน Gameweek
  - **Top Captain Picks:** อันดับตัวเลือกกัปตันที่ให้ค่าคาดหวังแต้มสูงสุด
  - **Highest-Leverage Differentials:** ตัวสร้างความต่างที่มี Ownership ต่ำแต่ค่า Projected สูง ช่วยดันแรงก์
  - **Clean Sheet Odds:** โอกาสเก็บคลีนชีตของทีมในแต่ละสัปดาห์
  - **prG & prA:** ประตูคาดหวัง (Projected Goals) และ แอสซิสต์คาดหวัง (Projected Assists)

---

### 2. Fantasy Football Scout (`https://www.fantasyfootballscout.co.uk`)
* **บทบาทหลัก:** รายงานข่าวความพร้อม, อาการบาดเจ็บ และไลน์อัปคาดการณ์/ข่าวหลุดก่อนแข่ง (Team News & Predicted Lineups)
* **ข้อมูลที่นำมาใช้:**
  - **Press Conference Summaries:** สรุปบทสัมภาษณ์งานแถลงข่าวของผู้จัดการทีมทั้ง 20 สโมสร
  - **Injury & Ban Table:** ตารางอัปเดตอาการบาดเจ็บและโทษแบนล่าสุดก่อนเดดไลน์
  - **Predicted Lineups & Team Leaks:** ไลน์อัป 11 ตัวจริงที่คาดการณ์ และข่าวตัวจริงที่หลุดออกมาก่อนเดดไลน์ (Early Leaks)
  - **Scout Picks & Captaincy Analysis:** บทวิเคราะห์เชิงลึกจากทีมงานกูรู FPL

---

### 3. Coach FPL (`https://www.coachfpl.app/`)
* **บทบาทหลัก:** ศูนย์รวมข้อมูลและการวิเคราะห์ครบวงจร (CoachFPL Analytics Hub) และ Transfer Solver สำหรับ Choice 2 Selection
* **ข้อมูลที่นำมาใช้:**
  - **Fixtures & Custom FDR:** วิเคราะห์ความยากง่ายโปรแกรมแข่งขัน แยกเกมรุก (Attacking FDR) และเกมรับ (Defensive FDR) พร้อมโรเตชั่นแนวรับ
  - **Player Projections & Expected Stats:** สถิติคาดการณ์แต้ม ประตู และแอสซิสต์
  - **Ownership Analytics:** สถิติการถือครองและความเสี่ยง
  - **Transfer Solver Optimization:** โมเดลจำลองและคำนวณการย้ายตัวจัดทีมอัตโนมัติ

---

### 4. LiveFPL (`https://www.livefpl.net`)
* **บทบาทหลัก:** Real-time Rank & Effective Ownership (EO) Analytics
* **ข้อมูลที่นำมาใช้:**
  - **Effective Ownership (EO%):** อัตราการถือครองจริงรวมการตั้งกัปตัน เพื่อประเมินความเสี่ยงและแต้มปลอดภัย (Safety Score)
  - **Top 10k Template:** ส่องทีมของผู้จัดการระดับท็อปของโลก (Elite Managers)
  - **Rank Swing Simulation:** จำลองผลกระทบต่ออันดับโลก

---

### 5. FPL Gameweek (`https://www.fplgameweek.com`)
* **บทบาทหลัก:** ติดตามมินิลีกแบบ Real-time (Mini-League & Rival Tracking)
* **ข้อมูลที่นำมาใช้:**
  - การจัดตัวและกัปตันของคู่แข่งในมินิลีก
  - การคำนวณแต้มสดพร้อมแต้มโบนัสชั่วคราว (Live BPS) และการเปลี่ยนตัวสำรองอัตโนมัติ (Live Auto-subs)

---

## Automated Data Pipeline

ระบบจะทำการผสานข้อมูลจาก **Official FPL API** ร่วมกับ **Solio Analytics Projections API** และรายงานความพร้อม/สถิติจาก **Fantasy Football Scout, LiveFPL, Coach FPL, และ FPL Gameweek** ในทุกๆ ครั้งที่มีการสร้าง Presentation รายงานประจำสัปดาห์

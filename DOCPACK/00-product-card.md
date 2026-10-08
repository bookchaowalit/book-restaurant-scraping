---
title: Book Restaurant Scraping — Product Card
doc_id: CARD-book-restaurant-scraping
doc_type: product-card
verdict: showcase
version: 0.1
date: 2026-10-08
status: ร่างเพื่อพิจารณา
owner: Product owner (Book Dev)
---

# Book Restaurant Scraping — Product Card

## 1. สรุปคุณค่าในหนึ่งประโยค

ต้นแบบเก็บรายชื่อร้านอาหารพร้อมข้อมูลธุรกิจที่เปิดเผยจาก Wongnai เป็น CSV สำหรับวิเคราะห์หรือหา lead โดยเก็บข้อมูลแบบสุภาพและตัดข้อมูลรีวิวเวอร์ออก

## 2. ปัญหาและผู้ใช้เป้าหมาย

- การรวบรวมรายชื่อร้านอาหารตามพื้นที่ด้วยมือช้า
- ผู้ใช้หลักคือเจ้าของ repo (Tier C / tool prototype) อาจใช้เป็น lead list ขายบริการให้ร้านอาหาร **[สมมติฐาน]**

## 3. สิ่งที่ทำได้จริงตอนนี้

- `restaurants/wongnai_scraper.py` parse หน้าผลค้นหา; `scripts/run_restaurants.py` รันหลาย job แยกความล้มเหลวราย job
- `restaurants/http.py` เป็นทางเครือข่ายเดียว: User-Agent ระบุตัว, timeout 30s, retry 3 ครั้งแบบ backoff เฉพาะ 429/5xx/timeout และเคารพ `Retry-After`
- จำกัด 5 หน้า x 100 แถว เว้น 2 วินาทีต่อหน้า เขียน raw/snapshot/history แบบ atomic
- raw capture เก็บเฉพาะฟิลด์ธุรกิจ ไม่เก็บรีวิวหรือชื่อผู้รีวิว; มี cron รายสัปดาห์ (`setup_cron.sh`)
- test 6 ไฟล์ (parser, http, atomic IO, runner)

## 4. หลักฐานสถานะ

- Stack: Python
- Commits: 16 (แรก 2026-07-09 → ล่าสุด 2026-10-01), branch `main`; working tree สะอาด
- Source: 10 ไฟล์ / 1,147 บรรทัด; test 6 ไฟล์
- CI: 1 workflow
- Deploy config: ไม่มี
- Live URL: ไม่พบใน repo

## 5. คุณค่าและจุดต่าง

- เป็นตัวอย่าง polite scraping ที่ดีที่สุดในกลุ่ม scraper ของ Book Dev
- Wongnai มีข้อมูลครบกว่าในแอปของตัวเอง ผลลัพธ์จึงมีค่าเฉพาะเมื่อเอาไปใช้ต่อ (lead list/analysis)
- มุมรายได้: lead list สำหรับขายบริการ (เช่นเว็บ/LINE OA) ให้ร้านอาหาร **[สมมติฐาน]** ต้องตรวจเงื่อนไขการใช้ข้อมูลก่อน **[ต้องยืนยัน]**

## 6. ช่องว่างสำคัญ

- ยังไม่ระบุว่าการเก็บข้อมูลสอดคล้องเงื่อนไขการใช้งานของ Wongnai **[ต้องยืนยัน]**
- ไม่มี consumer ปลายทางหรือการวิเคราะห์ต่อจาก CSV
- ผูกกับโครง HTML ของเว็บเดียว เปราะต่อการเปลี่ยนหน้าเว็บ

## 7. คำตัดสิน

**showcase** — โค้ดคุณภาพดีและเป็นหลักฐานด้าน scraping อย่างรับผิดชอบ แต่ไม่มีผู้ใช้หรือ use case ที่พิสูจน์แล้ว

จะเป็น `invest` เมื่อมี use case ปลายทางที่ใช้จริง (เช่น lead list ที่ทำให้เกิดการขาย) และยืนยันเงื่อนไขการใช้ข้อมูลแล้ว

## 8. ขั้นต่อไป

1. ยืนยันเงื่อนไขการใช้ข้อมูลของแหล่งต้นทาง
2. ใช้ `restaurants/http.py` เป็น helper มาตรฐานของ scraper ตัวอื่น
3. ตัดสินใจ use case ปลายทาง หรือคงไว้เป็น portfolio

## การอนุมัติ

| บทบาท | สถานะ | วันที่ | ลงนาม |
|---|---|---|---|
| Product owner (Book Dev) | รอพิจารณา | — | ________ |

## แหล่งข้อมูล

- `README.md`
- `restaurants/http.py`
- `restaurants/wongnai_scraper.py`
- `scripts/run_restaurants.py`
- `tests/`

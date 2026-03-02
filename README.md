# 🚗 Vehicle Tracking & Lane Counter
> **Real-Time Traffic Analysis with Sloped Lane Logic (YOLO + OpenCV)**

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![YOLO](https://img.shields.io/badge/YOLO-Ultralytics-orange?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-green?style=for-the-badge&logo=opencv)
![CUDA](https://img.shields.io/badge/CUDA-Enabled-76B900?style=for-the-badge&logo=nvidia)

ระบบตรวจจับ ติดตาม และนับจำนวนรถแบบ Real-Time โดยใช้ Ultralytics YOLO ร่วมกับ OpenCV รองรับการแบ่งเลนแบบเส้นเอียง (Sloped Lane Divider) เพื่อการนับรถที่แม่นยำตามมุมมองกล้องจริง (Perspective View)

---

## 🔥 ความสามารถของระบบ (Features)

* ✅ **Real-Time Detection:** ตรวจจับรถด้วย YOLO รุ่นล่าสุด (YOLOv8/v11)
* ✅ **Persistent Tracking:** ติดตามวัตถุด้วย ID เฉพาะ ไม่หลุดแม้รถบังกัน
* ✅ **Sloped Lane Divider:** แบ่งเลนด้วยเส้นเอียง (คำนวณจากการคลิก 2 จุดบนหน้าจอ)
* ✅ **Multi-Class Counting:** แยกนับตามประเภทรถ (Car, Truck, Bus, Motorcycle)
* ✅ **GPU Acceleration:** รองรับการประมวลผลผ่าน CUDA เพื่อความลื่นไหล
* ✅ **Interactive Setup:** กำหนดเส้นแบ่งเลนได้เองขณะรันโปรแกรม

---

## 🧠 หลักการทำงาน (System Logic)

### 1. การตรวจจับและติดตาม
ใช้ระบบ Tracking ภายในของ Ultralytics เพื่อคงค่า ID ของรถแต่ละคัน:
`results = model.track(frame, persist=True, classes=[2, 5, 7], device=0)`

### 2. สมการเส้นแบ่งเลน (Sloped Line Divider)
ระบบคำนวณจากจุดที่ผู้ใช้คลิก 2 จุด เพื่อสร้างสมการเส้นตรงสำหรับแบ่งพื้นที่:
* **Logic:** x = (slope * y) + intercept
* ช่วยให้แยกฝั่งซ้าย-ขวาได้แม่นยำแม้ถนนจะมีความเอียงตามมุมกล้อง



### 3. เงื่อนไขการนับ (Counting Logic)
| กรณี | การประมวลผล |
| :--- | :--- |
| **ตำแหน่ง** | เทียบจุดกึ่งกลาง (Center Point) กับเส้นแบ่งเลน |
| **ทิศทาง** | ตรวจสอบเมื่อจุดกึ่งกลางตัดผ่านเส้นนับ (Counting Line) |
| **การนับซ้ำ** | ใช้ track_id เก็บใน Set เพื่อป้องกันการนับรถคันเดิมซ้ำ |

---

## 🚀 วิธีติดตั้งและใช้งาน (Getting Started)

### 1. การเตรียมระบบและติดตั้ง
* **Python:** แนะนำเวอร์ชัน 3.9 ขึ้นไป
* **Library:** ติดตั้งผ่าน Terminal/Command Prompt:
```bash
pip install ultralytics opencv-python

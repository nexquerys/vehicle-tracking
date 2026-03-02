# 🚗 Vehicle Tracking & Lane Counter
> **Real-Time Traffic Analysis using YOLO + OpenCV**

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![YOLO](https://img.shields.io/badge/YOLO-Ultralytics-orange?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-green?style=for-the-badge&logo=opencv)
![CUDA](https://img.shields.io/badge/CUDA-Enabled-76B900?style=for-the-badge&logo=nvidia)

ระบบตรวจจับ ติดตาม และนับจำนวนรถแบบ Real-Time ที่ถูกออกแบบมาเพื่อจัดการกับความท้าทายของ **"เส้นแบ่งเลนแนวเอียง (Sloped Lane Divider)"** ช่วยให้การนับจำนวนรถแยกฝั่งซ้าย-ขวาแม่นยำยิ่งขึ้นตามมุมมองของกล้องวงจรปิดจริง

---

## 🔥 Key Features

* **Smart Tracking:** ใช้ Persistent Tracking (ByteTrack/BoT-SORT) ทำให้ ID ของรถไม่กระโดดแม้มีการบดบัง
* **Dynamic Lane Divider:** ระบบคำนวณสมการเส้นตรงจากการคลิก 2 จุด รองรับถนนทุกมุมกล้อง
* **Multi-Class Detection:** แยกนับประเภทรถได้ชัดเจน (Car, Truck, Bus, Motorcycle)
* **High Performance:** รองรับการประมวลผลผ่าน GPU (CUDA) เพื่อความเร็วระดับ Real-Time
* **Visual Analytics:** แสดง Bounding Box, Tracking ID, Center Point และ Summary Dashboard บนหน้าจอ

---

## 🧠 System Architecture

ระบบทำงานโดยอาศัย 3 กลไกหลัก:

### 1. Detection & Tracking
ใช้โมเดล YOLO ล่าสุดพร้อมคำสั่ง `model.track()` เพื่อคงค่า ID ของวัตถุไว้ตลอดการเคลื่อนที่
```python
results = model.track(frame, persist=True, classes=[2, 5, 7], device=0)

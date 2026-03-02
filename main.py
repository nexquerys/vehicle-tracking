import cv2 as cv
from ultralytics import YOLO

lane_points = []

# YOLO
model = YOLO('yolo26n.pt')
model.to("cuda")
class_list = model.names

# Mouse callback function เพื่อรับพิกัดและคำนวณ slope
# 1. ผู้ใช้คลิกเมาส์บนหน้าจอ
# 2. OpenCV เรียก mouse_callback()
# 3. โค้ดบันทึกพิกัดที่คลิก
# 4. เมื่อได้ครบ 2 จุด → คำนวณสมการเส้น
# 5. ล้างค่าเพื่อรอคลิกใหม่
def mouse_callback(event, x, y, flags, param):
    # เมื่อผู้ใช้คลิ๊กเมาส์ซ้าย
    if event == cv.EVENT_LBUTTONDOWN:
        # ทำไมต้องหาร ratio ?
        # เพราะ:
        # - ภาพที่แสดงถูก "ย่อ"
        # - แต่ YOLO ใช้พิกัด "ภาพจริง"
        # ดังนั้นต้องแปลงกลับ
        original_x = int(x / ratio)
        original_y = int(y / ratio)
        print(f"mouse click: {original_x}, {original_y}")

        # เก็บจุดลง list
        # ตอนนี้ list จะมีค่าแบบนี้:
        # - [(x1,y1)] หรือ [(x1,y1), (x2,y2)]
        lane_points.append((original_x, original_y))

        # ตรวจว่าคลิกครบ 2 จุดหรือยัง
        # เพราะเส้นตรงต้องใช้ 2 จุดในการสร้าง
        if len(lane_points) == 2:
            # ดึงค่าพิกัด
            x1, y1 = lane_points[0]
            x2, y2 = lane_points[1]

            # ป้องกันหารด้วยศูนย์
            if y2 != y1:
                # สูตรจริงของเส้นตรงคือ:
                # - m = (x) / (y)
                # สังเกตว่า:
                # - ใช้ y เป็นตัวแปรหลัก
                # - เพราะภาพคอมพิวเตอร์แกน Y คือแนวตั้ง
                slope = (x2 - x1) / (y2 - y1)

                # คำนวณ intercept
                # มาจากสูตรเส้นตรง:
                # - x = slope * y + intercept
                intercept = x2 - slope * y2

                # แสดงผลลัพธ์
                # จะได้ค่าแบบ:
                # - slope = 0.345
                # - intercept = 120.0
                print(f"slope = {slope:.3f}")
                print(f"intercept = {intercept:.1f}")

                # แสดงสมการเส้น
                # ตัวอย่าง:
                # - x = 0.345 * y + 120
                # นี่คือสมการเส้นแบ่งเลน
                print(f"Equation: x = {slope:.3f} * y + {intercept:.1f}")

                # รีเซ็ต list เพื่อให้สามารถคลิกเลือกเส้นใหม่ได้
                lane_points.clear()

def get_lane_divider_x(y):
    return int(lane_divider_slope * y + lane_divider_intercept)

def draw_sloped_lane_divider(frame, y_start, y_end):
    # คำนวณตำแหน่ง X ของเส้นซึ่งมาจากการคลิก 2 จุดก่อนหน้า
    x_start = get_lane_divider_x(y_start)
    x_end = get_lane_divider_x(y_end)

    # วาดเส้น
    cv.line(frame, (x_start, y_start), (x_end, y_end), (255, 255, 255), 3)

ratio = 0.5

lane_divider_slope = 0.005
lane_divider_intercept = 642.3

class_count_left = {}
class_count_right = {}
crossed_in_ids  = set()
crossed_out_ids = set()

name = "Traffic Detection"
path = "highway-traffic.mp4"
cap = cv.VideoCapture(path)
cv.namedWindow(name)
cv.setMouseCallback(name, mouse_callback)

if not cap.isOpened():
    exit()

while True:
    # ret = อ่านสำเร็จไหม
    # frame = ภาพ
    ret, frame = cap.read()

    # คำนวณขนาดใหม่
    new_wight = int(ratio * frame.shape[1])
    new_hight = int(ratio * frame.shape[0])

    # print(f"original width: {frame.shape[1]}, original height: {frame.shape[0]}")
    # print(f"new wight: {new_wight}, hight: {new_hight}")

    if not ret:
        break

    # วาดเส้นเกาะกลาง
    draw_sloped_lane_divider(frame, 0, frame.shape[0])

    # กำหนดตำแหน่งความสูงของเส้นนับรถ
    line_y = int(frame.shape[0] * 0.55)

    # หาตำแหน่ง X ของเส้นกลางถนน ที่ระดับความสูงนี้
    divider_x = get_lane_divider_x(line_y)

    # วาดเส้นแบ่งซ้าย
    # จุดเริ่ม:
    #     - (0, line_y)
    #       - 0 = ขอบซ้ายสุดของภาพ (แกน X เริ่มที่ 0 เสมอ)
    #       - line_y = ความสูงของเส้นนับรถ (แกน Y)
    # จุดจบ:
    #     - (divider_x, line_y)
    #       - divider_x = ตำแหน่ง X ของเส้นกลางถนน ณ ระดับความสูงนี้
    #       - line_y = อยู่ระดับเดียวกัน → จึงเป็นเส้นแนวนอน
    cv.line(frame, (0, line_y), (divider_x, line_y), (0, 255, 0), 3)
    cv.putText(frame, "Left lane", (50, line_y - 10), cv.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)

    # วาดเส้นแบ่งขวา
    # จุดเริ่ม:
    #     - (divider_x, line_y)
    #         - divider_x = ตำแหน่ง X ของเส้นกลางถนน ณ ระดับความสูงนี้
    #         - line_y = ความสูงของเส้นนับรถ
    # จุดจบ:
    #     - (frame.shape[1], line_y)
    #         - frame.shape[1] = ความกว้างของภาพ → ขอบขวาสุด
    #         - line_y = อยู่ระดับเดียวกัน (เป็นเส้นแนวนอน)
    cv.line(frame, (divider_x, line_y), (frame.shape[1], line_y), (0, 0, 255), 3)
    cv.putText(frame, "Right lane", (divider_x + 20, line_y - 10), cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)

    # สั่งให้โมเดลตรวจจับ + ติดตามวัตถุในเฟรมปัจจุบัน
    # 1. ส่งภาพ frame เข้า YOLO
    # 2. YOLO ตรวจจับวัตถุที่เป็นรถ (class 2 = car, 7 = truck)
    # 3. Tracker จะกำหนด ID ให้แต่ละคัน
    # 4. persist=True ทำให้ ID ไม่เปลี่ยนทุกเฟรม
    results = model.track(frame, persist=True, classes=[2], device=0, verbose=False)

    # ตรวจว่ามี detection หรือไม่
    # ทำไมต้องเช็ค:
    # - บางเฟรมอาจไม่มีรถ
    # - ถ้าไม่เช็ค → โปรแกรมจะ error เพราะไม่มีข้อมูลให้อ่าน
    if results[0].boxes.id is not None:
        # ดึงข้อมูลตำแหน่งกรอบของวัตถุ
        # รูปแบบข้อมูล:
        # - [x1, y1, x2, y2]
        # - เป็นมุมซ้ายบน → มุมขวาล่าง
        boxes = results[0].boxes.xyxy.cpu()

        # ดึง ID ของวัตถุที่ tracker สร้างขึ้น
        # ทำไมต้องมี ID:
        # - ใช้แยกว่ารถแต่ละคันคือคนละตัว
        # - ป้องกันการนับซ้ำ
        track_ids = results[0].boxes.id.int().cpu().tolist()

        # ดึง class index ของวัตถุ
        # เช่น:
        # - 2 = car
        # - 7 = truck
        class_indices = results[0].boxes.cls.int().cpu().tolist()

        # ดึงค่าความมั่นใจของโมเดล
        # ค่าจะอยู่ระหว่าง 0 → 1
        confidences = results[0].boxes.conf.cpu()

        # วนลูปประมวลผลวัตถุทีละตัว
        # zip() ใช้จับคู่ข้อมูลของ:
        # - box
        # - id
        # - class
        # - confidence
        for box, track_id, class_idx, conf in zip(boxes, track_ids, class_indices, confidences):
            # แปลงค่าพิกัดเป็นจำนวนเต็ม
            x1, y1, x2, y2 = map(int, box)

            # คำนวณจุดกึ่งกลางของกรอบ
            # ทำไมต้องใช้จุดกลาง:
            # - ใช้เป็นตำแหน่งอ้างอิงในการตรวจว่ารถข้ามเส้นหรือยัง
            # - แม่นยำกว่าใช้มุมของกรอบ
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # แปลง class index → ชื่อ class
            # เช่น:
            # - 2 → car
            # - 7 → truck
            class_name = class_list[class_idx]

            # หาตำแหน่ง X ของเส้นแบ่งเลน ณ ความสูงของรถ
            # ทำไมต้องใช้ cy:
            # - เพราะเส้นกลางถนนเป็นเส้นเอียง
            # - ตำแหน่ง X จะเปลี่ยนไปตามระดับ Y
            divider_x_at_vehicle = get_lane_divider_x(cy)

            # วาดจุดกลางของรถ
            # ใช้เพื่อดูตำแหน่งอ้างอิงของระบบนับรถ
            cv.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

            # แสดง ID และชื่อ class บนภาพ
            # ช่วยให้รู้ว่ารถคันไหนถูก track อยู่
            cv.putText(frame, f"ID: {track_id} {class_name}", (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # วาดกรอบสี่เหลี่ยมรอบวัตถุ
            # เพื่อให้เห็นตำแหน่งที่ YOLO ตรวจจับได้
            cv.rectangle(frame, (x1, y1), (x2,y2), (0, 255, 0), 2)

            # ตรวจว่ารถ "เข้าเลน IN"
            if cx > divider_x_at_vehicle and cy < line_y and track_id not in crossed_in_ids:
                # เงื่อนไข:
                # 1. cx > divider → อยู่ฝั่งขวาของถนน
                # 2. cy < line_y → อยู่เหนือเส้นนับรถ
                # 3. ID ยังไม่เคยนับ

                # บันทึกว่า ID นี้ถูกนับแล้ว
                crossed_in_ids.add(track_id)

                # เพิ่มจำนวนรถของ class นั้น
                # get() ใช้เพื่อป้องกัน key ไม่มีใน dict
                class_count_left[class_name] = class_count_left.get(class_name, 0) + 1

            # ตรวจว่ารถ "เข้าเลน OUT"
            if cx < divider_x_at_vehicle and cy > line_y and track_id not in crossed_out_ids:
                # เงื่อนไข:
                # 1. cx < divider → อยู่ฝั่งซ้าย
                # 2. cy > line_y → อยู่ใต้เส้นนับรถ
                # 3. ยังไม่เคยนับ

                crossed_out_ids.add(track_id)
                class_count_right[class_name] = class_count_right.get(class_name, 0) + 1

    # ส่วนแสดงผลบนหน้าจอ
    y_offset = 30
    cv.putText(frame, "Vehicle Left Lane", (50, y_offset), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    y_offset += 25

    for class_name, count in class_count_left.items():
        cv.putText(frame, f"{class_name}: {count}", (70, y_offset), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_offset += 25

    y_offset += 10
    cv.putText(frame, "Vehicle Right Lane", (50, y_offset), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    y_offset += 25

    for class_name, count in class_count_right.items():
        cv.putText(frame, f"{class_name}: {count}", (70, y_offset), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        y_offset += 25

    # ย่อภาพ
    new_frame = cv.resize(frame, (new_wight, new_hight))

    # แสดงภาพ
    cv.imshow(name, new_frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
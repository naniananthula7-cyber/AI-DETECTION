import cv2
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Start webcam
cap = cv2.VideoCapture(0)

entered_count = 0
exited_count = 0
line_position = 250
person_positions = {}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Use tracking instead of plain detection
    results = model.track(frame, persist=True, tracker="bytetrack.yaml")

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            if label == "person":
                # Get center of bounding box
                x1, y1, x2, y2 = box.xyxy[0]
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                # Use tracker-assigned ID
                person_id = int(box.id[0]) if box.id is not None else cx
                prev_y = person_positions.get(person_id, None)

                if prev_y is not None:
                    if prev_y < line_position and cy >= line_position:
                        entered_count += 1
                        print(f"Person entered! Total entered: {entered_count}")
                    elif prev_y > line_position and cy <= line_position:
                        exited_count += 1
                        print(f"Person exited! Total exited: {exited_count}")

                person_positions[person_id] = cy

                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

    cv2.line(frame, (0, line_position), (frame.shape[1], line_position), (0, 0, 255), 2)
    cv2.putText(frame, f"Entered: {entered_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Exited: {exited_count}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Shop Entry/Exit Counter", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
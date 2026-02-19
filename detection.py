


'''''import cv2
from ultralytics import YOLO
from datetime import datetime
from save_counts import save_counts_to_drive   # <-- import the saving function
import sys
import traceback

try:
    # ---------------- YOLO + Counter ----------------
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("❌ Camera could not be opened. Please check your webcam connection.")

    entered_count = 0
    exited_count = 0
    line_position = 250
    person_positions = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to read frame from camera. Exiting loop.")
            break

        try:
            results = model.track(frame, persist=True, tracker="bytetrack.yaml")
        except Exception as e:
            print("❌ YOLO tracking failed:", e)
            traceback.print_exc()
            break

        for r in results:
            for box in r.boxes:
                try:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]

                    if label == "person":
                        x1, y1, x2, y2 = box.xyxy[0]
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)

                        person_id = int(box.id[0]) if box.id is not None else cx
                        prev_x = person_positions.get(person_id, None)

                        if prev_x is not None:
                            if prev_x < line_position and cx >= line_position:
                                entered_count += 1
                                print(f"✅ Person entered (Left → Right)! Total entered: {entered_count}")

                            elif prev_x > line_position and cx <= line_position:
                                exited_count += 1
                                print(f"✅ Person exited (Right → Left)! Total exited: {exited_count}")

                        person_positions[person_id] = cx
                        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                except Exception as e:
                    print("⚠️ Error processing box:", e)
                    traceback.print_exc()

        cv2.line(frame, (line_position, 0), (line_position, frame.shape[0]), (0, 0, 255), 2)
        cv2.putText(frame, f"Entered (L→R): {entered_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Exited (R→L): {exited_count}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Shop Entry/Exit Counter", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quit signal received. Stopping detection.")
            break

    cap.release()
    cv2.destroyAllWindows()

    try:
        save_counts_to_drive(entered_count, exited_count)
        print("💾 Counts saved successfully.")
    except Exception as e:
        print("❌ Failed to save counts:", e)
        traceback.print_exc()

except Exception as e:
    print("❌ Fatal error occurred:", e)
    traceback.print_exc()
    sys.exit(1)'''''
import cv2
from ultralytics import YOLO
from datetime import datetime
from save_counts import save_counts_to_drive
import sys
import traceback
import signal

# Flag to control loop
running = True

def handle_sigterm(signum, frame):
    global running
    print("🛑 SIGTERM received, stopping detection gracefully...")
    running = False

# Register signal handler
signal.signal(signal.SIGTERM, handle_sigterm)

try:
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("❌ Camera could not be opened. Please check your webcam connection.")

    entered_count = 0
    exited_count = 0
    line_position = 250
    person_positions = {}

    while running:   # <-- use flag instead of while True
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to read frame from camera. Exiting loop.")
            break

        try:
            results = model.track(frame, persist=True, tracker="bytetrack.yaml")
        except Exception as e:
            print("❌ YOLO tracking failed:", e)
            traceback.print_exc()
            break

        for r in results:
            for box in r.boxes:
                try:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]

                    if label == "person":
                        x1, y1, x2, y2 = box.xyxy[0]
                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)

                        person_id = int(box.id[0]) if box.id is not None else cx
                        prev_x = person_positions.get(person_id, None)

                        if prev_x is not None:
                            if prev_x < line_position and cx >= line_position:
                                entered_count += 1
                                print(f"✅ Person entered (Left → Right)! Total entered: {entered_count}")

                            elif prev_x > line_position and cx <= line_position:
                                exited_count += 1
                                print(f"✅ Person exited (Right → Left)! Total exited: {exited_count}")

                        person_positions[person_id] = cx
                        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                except Exception as e:
                    print("⚠️ Error processing box:", e)
                    traceback.print_exc()

        cv2.line(frame, (line_position, 0), (line_position, frame.shape[0]), (0, 0, 255), 2)
        cv2.putText(frame, f"Entered (L→R): {entered_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Exited (R→L): {exited_count}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Shop Entry/Exit Counter", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quit signal received. Stopping detection.")
            break

    cap.release()
    cv2.destroyAllWindows()

    try:
        save_counts_to_drive(entered_count, exited_count)
        print("💾 Counts saved successfully.")
    except Exception as e:
        print("❌ Failed to save counts:", e)
        traceback.print_exc()

except Exception as e:
    print("❌ Fatal error occurred:", e)
    traceback.print_exc()
    sys.exit(1)


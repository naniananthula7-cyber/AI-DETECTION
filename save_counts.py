"""
import cv2
import csv
import os
from datetime import datetime
from ultralytics import YOLO

# Google Drive imports
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# ---------------- Google Drive Auth ----------------
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def create_drive_file(filename):
    service = get_drive_service()
    file_metadata = {'name': os.path.basename(filename)}
    media = MediaFileUpload(filename, mimetype='text/csv')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Created file in Drive with ID: {file.get('id')}")
    return file.get('id')

def update_drive_file(file_id, filename):
    service = get_drive_service()
    media = MediaFileUpload(filename, mimetype='text/csv')
    updated_file = service.files().update(fileId=file_id, media_body=media).execute()
    print(f"Updated file {filename} in Drive (ID: {updated_file.get('id')})")

# ---------------- YOLO + Counter ----------------
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

entered_count = 0
exited_count = 0
line_position = 250   # vertical line at x = 250
person_positions = {}
counted_ids = set()   # track IDs already counted

# CSV file to log counts
csv_file = "counts.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Entered", "Exited"])

# Create the file once in Drive
drive_file_id = create_drive_file(csv_file)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, persist=True, tracker="bytetrack.yaml")

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            if label == "person":
                x1, y1, x2, y2 = box.xyxy[0]
                cx = int((x1 + x2) / 2)   # center X for vertical line crossing
                cy = int((y1 + y2) / 2)

                person_id = int(box.id[0]) if box.id is not None else cx
                prev_x = person_positions.get(person_id, None)

                if prev_x is not None and person_id not in counted_ids:
                    if prev_x < line_position and cx >= line_position:
                        entered_count += 1
                        counted_ids.add(person_id)
                        print(f"Person entered (Left → Right)! Total entered: {entered_count}")
                        with open(csv_file, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([datetime.now(), entered_count, exited_count])
                        update_drive_file(drive_file_id, csv_file)

                    elif prev_x > line_position and cx <= line_position:
                        exited_count += 1
                        counted_ids.add(person_id)
                        print(f"Person exited (Right → Left)! Total exited: {exited_count}")
                        with open(csv_file, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([datetime.now(), entered_count, exited_count])
                        update_drive_file(drive_file_id, csv_file)

                person_positions[person_id] = cx
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

    # Draw vertical line (x fixed, y spans full height)
    cv2.line(frame, (line_position, 0), (line_position, frame.shape[0]), (0, 0, 255), 2)

    # Show counts
    cv2.putText(frame, f"Entered (L→R): {entered_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Exited (R→L): {exited_count}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Shop Entry/Exit Counter", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
"""




'''''import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def update_drive_file(file_id, filename):
    service = get_drive_service()
    media = MediaFileUpload(filename, mimetype='text/csv')
    updated_file = service.files().update(fileId=file_id, media_body=media).execute()
    print(f"Updated file {filename} in Drive (ID: {updated_file.get('id')})")

# ---------------- Saving ----------------
csv_file = "counts.csv"

# IMPORTANT: Replace with your actual Drive file ID (create once manually or first run)
drive_file_id = "YOUR_EXISTING_FILE_ID"

update_drive_file(drive_file_id, csv_file)'''''






import os
import csv
import pickle
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def find_or_create_drive_file(filename):
    service = get_drive_service()
    results = service.files().list(q=f"name='{filename}'", fields="files(id, name)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        file_metadata = {'name': filename}
        media = MediaFileUpload(filename, mimetype='text/csv')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

def update_drive_file(file_id, filename):
    service = get_drive_service()
    media = MediaFileUpload(filename, mimetype='text/csv')
    service.files().update(fileId=file_id, media_body=media).execute()

def save_counts_to_drive(entered_count, exited_count, filename="counts.csv"):
    if not os.path.exists(filename):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Entered", "Exited"])

    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), entered_count, exited_count])

    drive_file_id = find_or_create_drive_file(filename)
    update_drive_file(drive_file_id, filename)
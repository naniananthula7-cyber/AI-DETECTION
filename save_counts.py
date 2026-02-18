import os
import csv
import pickle
import sys
import traceback
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    try:
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError("❌ Missing credentials.json file for Google Drive API.")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)

    except Exception as e:
        print("❌ Error initializing Google Drive service:", e)
        traceback.print_exc()
        sys.exit(1)

def find_or_create_drive_file(filename):
    try:
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
    except Exception as e:
        print("❌ Error finding or creating file on Drive:", e)
        traceback.print_exc()
        return None

def update_drive_file(file_id, filename):
    try:
        service = get_drive_service()
        media = MediaFileUpload(filename, mimetype='text/csv')
        service.files().update(fileId=file_id, media_body=media).execute()
        print("✅ Drive file updated successfully.")
    except Exception as e:
        print("❌ Error updating file on Drive:", e)
        traceback.print_exc()

def save_counts_to_drive(entered_count, exited_count, filename="counts.csv"):
    try:
        if not os.path.exists(filename):
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Entered", "Exited"])

        with open(filename, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), entered_count, exited_count])

        drive_file_id = find_or_create_drive_file(filename)
        if drive_file_id:
            update_drive_file(drive_file_id, filename)
            print("💾 Counts saved to Google Drive successfully.")
        else:
            print("⚠️ Counts saved locally, but failed to upload to Drive.")

    except Exception as e:
        print("❌ Error saving counts:", e)
        traceback.print_exc()
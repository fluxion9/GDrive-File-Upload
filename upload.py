import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import argparse


ap = argparse.ArgumentParser()

ap.add_argument('-f', '--file', required=True,
                help = 'path to input image')
args = ap.parse_args()

# Replace 'your-folder-id' with the actual folder ID from your Google Drive.
FOLDER_ID = '1PynHcBWHPCvTCbOGIej3W5YxKpiNmcjQ'

# Path to your service account key file (replace with the path to your downloaded file).
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Define the required scopes.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Authenticate using the service account.
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Drive API client.
drive_service = build('drive', 'v3', credentials=credentials)

def upload_file(file_path, file_name):
    """Uploads a file to the specified Google Drive folder."""
    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')} uploaded successfully.")

# Example usage:
# Replace with the path to your image file and the name you want it to have in Drive.

upload_file(args.file, os.path.basename(args.file))

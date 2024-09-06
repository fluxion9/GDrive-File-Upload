import os, argparse, requests, numpy as np, cv2
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
from time import sleep

default_IP = '192.168.4.1'

cam_route = '/capture'

cam_ping_route = '/ping'

ap = argparse.ArgumentParser()

ap.add_argument('-c', '--use_webcam', required=False,
                help = 'use built-in camera feed')
ap.add_argument('-i', '--IP', required=False,
                help = 'use built-in camera feed')
args = ap.parse_args()

if args.IP != None:
    IP_Address = args.IP
else:
    IP_Address = default_IP

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

if args.use_webcam == 'true':
    src, option = cv2.VideoCapture(0), True
else:
    src, option = cam_route, False
    while True:
        try:
            url = 'http://' + IP_Address + cam_ping_route
            res = requests.get(url, timeout=0.5)
        except requests.exceptions.RequestException as e:
            print("ESP32 CAM Connection Error")
            continue
        if res.status_code != 200:
            print("ESP32 CAM Response Error")
            continue
        else:
            break

while True:
    if option:
        _, frame = src.read()
        src.release()
        height, width, channels = frame.shape
        src = cv2.VideoCapture(0)
    else:
        try:
            url = 'http://' + IP_Address + src
            response = requests.get(url, timeout=0.5)
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            height, width, channels = frame.shape
        except Exception as e:
            print("No Camera or Valid Frame Found")
            continue
    cv2.imwrite('image.jpg', frame)
    filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    print("Uploading", filename)
    upload_file('image.jpg', filename)
    sleep(10.0)

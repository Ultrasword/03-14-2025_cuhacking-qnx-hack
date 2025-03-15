import os
import time
import requests
import shutil
import llm

# Configuration
WATCH_FOLDER = "/home/pi/videos"
PROCESSED_FOLDER = "/home/pi/videos/processed"

GEMINI = llm.Gemini()

# API_ENDPOINT = "http://your-api-endpoint/upload"  # Change to your actual API

POLL_INTERVAL = 5  # seconds between folder scans


def send_to_api(file_path):
    print(f"[Helper] Sending {file_path} to API...")
    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "video/mp4")}
            response = requests.post(API_ENDPOINT, files=files)

            if response.status_code == 200:
                print(f"[Helper] Successfully sent {file_path} to API.")
                return True
            else:
                print(
                    f"[Helper] Failed to send {file_path}. Status code: {response.status_code}"
                )
                return False
    except Exception as e:
        print(f"[Helper] Exception while sending {file_path}: {e}")
        return False


def process_files():
    """Process files in watch folder and send to API."""
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)

    while True:
        files = sorted([f for f in os.listdir(WATCH_FOLDER) if f.endswith(".mp4")])

        for filename in files:
            file_path = os.path.join(WATCH_FOLDER, filename)

            # Optionally check if file is still being written to (ensure no locks)
            if not is_file_ready(file_path):
                print(f"[Helper] {filename} is not ready yet, skipping for now.")
                continue

            success = send_to_api(file_path)

            if success:
                # Move file to processed folder after successful send
                dest_path = os.path.join(PROCESSED_FOLDER, filename)
                shutil.move(file_path, dest_path)
                print(f"[Helper] Moved {filename} to processed folder.")

        time.sleep(POLL_INTERVAL)


def is_file_ready(file_path):
    """Check if file is not being written to."""
    try:
        with open(file_path, "rb"):
            return True
    except IOError:
        return False


if __name__ == "__main__":
    process_files()

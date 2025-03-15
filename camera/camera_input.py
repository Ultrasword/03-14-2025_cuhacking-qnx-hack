import time
import os
import shutil
import cv2
from datetime import datetime


def record_continuous_clips(clip_duration=10, fps=30, resolution=(640, 480)):
    # Get base directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_directory = os.path.dirname(current_dir)  # Go up one level from server

    # Define the recording and videos directories
    recording_directory = os.path.join(base_directory, "assets", "storage", "recording")
    videos_directory = os.path.join(base_directory, "assets", "storage", "videos")

    # Ensure both directories exist
    os.makedirs(recording_directory, exist_ok=True)
    os.makedirs(videos_directory, exist_ok=True)

    # Initialize webcam using OpenCV
    cam = cv2.VideoCapture(
        2
    )  # Use the correct camera index (2 is usually for the external webcam)

    # Set the resolution of the camera
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    if not cam.isOpened():
        print("Error: Camera could not be opened.")
        return

    try:
        print("Starting continuous recording. Press Ctrl+C to stop.")
        while True:
            # Generate a timestamp-based filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"video_{timestamp}.mp4"
            recording_filepath = os.path.join(recording_directory, filename)

            print(f"Recording clip: {filename}...")

            # Initialize video writer with OpenCV
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for mp4
            writer = cv2.VideoWriter(recording_filepath, fourcc, fps, resolution)

            start_time = time.time()
            while (time.time() - start_time) < clip_duration:
                ret, frame = cam.read()
                if ret:
                    # Write frame to the video
                    writer.write(frame)
                else:
                    print("Error: Failed to capture frame.")
                    break
                time.sleep(1 / fps)

            # Release writer
            writer.release()
            print(
                f"Clip {filename} complete. Video saved temporarily as {recording_filepath}"
            )

            # Move the file to the videos directory
            final_filepath = os.path.join(videos_directory, filename)
            shutil.move(recording_filepath, final_filepath)
            print(f"Video moved to {final_filepath}")

    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    finally:
        # Release resources properly
        cam.release()
        print("Camera stopped. Exiting.")


if __name__ == "__main__":
    record_continuous_clips(resolution=(1280, 720))  # Change resolution if needed

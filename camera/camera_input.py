import time
import os
import shutil
import imageio
from webcam import Webcam
from datetime import datetime

def record_continuous_clips(clip_duration=10, fps=30, resolution=(640, 480)):
    # Get base directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_directory = os.path.dirname(current_dir)  # Go up one level from server
    
    # Define the recording and videos directories
    recording_directory = os.path.join(base_directory, 'assets', 'storage', 'recording')
    videos_directory = os.path.join(base_directory, 'assets', 'storage', 'videos')
    
    # Ensure both directories exist
    os.makedirs(recording_directory, exist_ok=True)
    os.makedirs(videos_directory, exist_ok=True)
    
    # Initialize webcam
    cam = Webcam(device="/dev/video2")
    cam.start()
    
    try:
        print("Starting continuous recording. Press Ctrl+C to stop.")
        while True:
            # Generate a timestamp-based filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"video_{timestamp}.mp4"
            recording_filepath = os.path.join(recording_directory, filename)
            
            print(f"Recording clip: {filename}...")
            
            # Initialize video writer
            writer = imageio.get_writer(recording_filepath, fps=fps)
            
            start_time = time.time()
            while (time.time() - start_time) < clip_duration:
                frame = cam.get_current_frame()
                if frame is not None:
                    writer.append_data(frame)
                time.sleep(1 / fps)
            
            # Release writer
            writer.close()
            print(f"Clip {filename} complete. Video saved temporarily as {recording_filepath}")
            
            # Move the file to the videos directory
            final_filepath = os.path.join(videos_directory, filename)
            shutil.move(recording_filepath, final_filepath)
            print(f"Video moved to {final_filepath}")
            
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    finally:
        # Ensure resources are released properly
        if 'writer' in locals():
            writer.close()
        cam.stop()
        print("Camera stopped. Exiting.")

if __name__ == "__main__":
    record_continuous_clips()
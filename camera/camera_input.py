import time
import os
import shutil
import cv2
from datetime import datetime
import pyaudio
import wave
import threading
import subprocess


def record_audio_segment(
    duration,
    audio_instance,
    audio_stream,
    chunk,
    audio_format,
    channels,
    rate,
    audio_filepath,
    start_event,
):
    start_event.wait()
    frames = []
    num_chunks = int(rate / chunk * duration)
    for _ in range(num_chunks):
        try:
            data = audio_stream.read(chunk, exception_on_overflow=False)
            frames.append(data)
        except Exception as e:
            print("Audio error:", e)
            break
    wf = wave.open(audio_filepath, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(audio_instance.get_sample_size(audio_format))
    wf.setframerate(rate)
    wf.writeframes(b"".join(frames))
    wf.close()


def merge_audio_video(video_filepath, audio_filepath, output_filepath):
    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_filepath,
        "-i",
        audio_filepath,
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        output_filepath,
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def record_continuous_clips(clip_duration=10, fps=30, resolution=(640, 480)):
    # Get base directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_directory = os.path.dirname(current_dir)  # Go up one level from server

    # Define the recording and videos directories
    recording_directory = os.path.join(
        base_directory, "server", "assets", "storage", "recording"
    )
    videos_directory = os.path.join(
        base_directory, "server", "assets", "storage", "videos"
    )
    audio_directory = os.path.join(
        base_directory, "server", "assets", "storage", "audio"
    )

    # Ensure both directories exist
    os.makedirs(recording_directory, exist_ok=True)
    os.makedirs(videos_directory, exist_ok=True)

    # Initialize webcam using OpenCV
    cam = cv2.VideoCapture(0)
    # Initialize audio recording

    audio = pyaudio.PyAudio()
    audio_format = pyaudio.paInt16  # 16-bit resolution
    channels = 1  # Mono audio
    rate = 44100  # 44.1kHz sampling rate
    chunk = 1024  # 2^10 samples for buffer

    # Create a stream object
    stream = audio.open(
        format=audio_format,
        channels=channels,
        rate=rate,
        input=True,
        frames_per_buffer=chunk,
    )
    # Use the correct camera index (2 is usually for the external webcam)

    # Set the resolution of the camera
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    if not cam.isOpened():
        print("Error: Camera could not be opened.")
        return

    try:
        print("Starting continuous recording. Press Ctrl+C to stop.")
        while True:
            # Generate timestamp-based filenames for video and audio
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            video_filename = f"video_{timestamp}.mp4"
            audio_filename = f"audio_{timestamp}.wav"
            final_filename = f"final_{timestamp}.mp4"

            video_filepath = os.path.join(recording_directory, video_filename)
            audio_filepath = os.path.join(recording_directory, audio_filename)
            final_filepath = os.path.join(recording_directory, final_filename)

            print(f"Recording clip: {video_filename}...")

            # Initialize video writer with OpenCV
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for mp4
            writer = cv2.VideoWriter(video_filepath, fourcc, fps, resolution)

            start_event = threading.Event()
            # Start audio recording in a separate thread
            audio_thread = threading.Thread(
                target=record_audio_segment,
                args=(
                    clip_duration,
                    audio,
                    stream,
                    chunk,
                    audio_format,
                    channels,
                    rate,
                    audio_filepath,
                    start_event,
                ),
            )
            audio_thread.start()
            start_event.set()

            start_time = time.time()
            frame_count = 0
            while (time.time() - start_time) < clip_duration:
                expected_time = start_time + frame_count / fps
                current_time = time.time()
                if current_time < expected_time:
                    time.sleep(expected_time - current_time)
                ret, frame = cam.read()
                if ret:
                    writer.write(frame)
                else:
                    print("Error: Failed to capture frame.")
                    break
                frame_count += 1

            writer.release()
            audio_thread.join()

            print(f"Clip {video_filename} recorded. Merging audio and video...")

            # Merge the video and audio files into a final file
            merge_audio_video(video_filepath, audio_filepath, final_filepath)
            print(f"Final clip saved as {final_filepath}")

            # move audio folder to correct place
            destination_path = os.path.join(audio_directory, audio_filename)
            shutil.move(audio_filepath, destination_path)
            print(f"Audio moved to {destination_path}")

            # Move the final file to the videos directory and remove temporary files
            destination_path = os.path.join(videos_directory, final_filename)
            shutil.move(final_filepath, destination_path)
            os.remove(video_filepath)
            print(f"Video moved to {destination_path}")

    except KeyboardInterrupt:
        print("\nRecording stopped by user.")

    finally:
        # Release resources properly
        cam.release()
        print("Camera stopped. Exiting.")


if __name__ == "__main__":
    record_continuous_clips(resolution=(1280, 720))  # Change resolution if needed

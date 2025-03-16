import time
import os
import shutil
import cv2
from datetime import datetime
import pyaudio
import wave
import threading
import subprocess
import platform


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
        base_directory, "server", "assets", "storage", "video"
    )
    audio_directory = os.path.join(
        base_directory, "server", "assets", "storage", "audio"
    )

    # Ensure both directories exist
    os.makedirs(recording_directory, exist_ok=True)
    os.makedirs(videos_directory, exist_ok=True)

    # Initialize webcam using OpenCV
    cam = cv2.VideoCapture(0)
    camera_fps = cam.get(cv2.CAP_PROP_FPS)
    if not camera_fps or camera_fps <= 0:
        camera_fps = fps  # Fallback if camera doesn't provide fps

    # audio_enabled = platform.system() != "Linux"
    audio_enabled = True

    # Initialize audio recording
    if audio_enabled:
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
    else:
        audio = None
        audio_format = None
        channels = None
        rate = None
        chunk = None
        stream = None

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
            if audio_enabled:
                audio_filename = f"audio_{timestamp}.wav"
                audio_filepath = os.path.join(recording_directory, audio_filename)

            video_filename = f"video_{timestamp}.mp4"
            final_filename = f"final_{timestamp}.mp4"
            temp_video_filename = f"video_{timestamp}-temp.mp4"
            video_filepath = os.path.join(recording_directory, video_filename)
            temp_video_filepath = os.path.join(recording_directory, temp_video_filename)
            if audio_enabled:
                final_filepath = os.path.join(recording_directory, final_filename)

            print(f"Recording clip: {temp_video_filename}.temp ...")

            # Initialize video writer with OpenCV
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for mp4
            writer = cv2.VideoWriter(
                temp_video_filepath, fourcc, camera_fps, resolution
            )

            if audio_enabled:
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
                ret, frame = cam.read()
                if ret:
                    writer.write(frame)
                else:
                    print("Error: Failed to capture frame.")
                    break
                frame_count += 1

            # update fps of writer + contents of video file
            camera_fps = frame_count / clip_duration
            writer.release()
            writer = cv2.VideoWriter(video_filepath, fourcc, camera_fps, resolution)
            print("Frames recorded:", frame_count)

            # read from temp file and write to final file
            cap_temp = cv2.VideoCapture(temp_video_filepath)
            while cap_temp.isOpened():
                ret, frame = cap_temp.read()
                if not ret:
                    break
                writer.write(frame)
            cap_temp.release()

            writer.release()
            if audio_enabled:
                audio_thread.join()
                print(f"Clip {video_filename} recorded. Merging audio and video...")

                # Merge the video and audio files into a final file
                merge_audio_video(video_filepath, audio_filepath, final_filepath)
                print(f"Final clip saved as {final_filepath}")

                # Move the audio file to the audio directory
                destination_path = os.path.join(audio_directory, audio_filename)
                shutil.move(audio_filepath, destination_path)
                print(f"Audio moved to {destination_path}")

                # Move the final merged file to the videos directory and remove the temporary video file
                destination_path = os.path.join(videos_directory, final_filename)
                shutil.move(final_filepath, destination_path)
                os.remove(video_filepath)
                print(f"Video moved to {destination_path}")
            else:
                print(f"Clip {video_filename} recorded.")
                # If audio is disabled, simply move the video file
                destination_path = os.path.join(videos_directory, video_filename)
                shutil.move(video_filepath, destination_path)
                print(f"Video moved to {destination_path}")

            # waiting 20s before next clip
            print("Waiting 20s before next clip...\n\n")
            time.sleep(20)
            print("Recording next clip...")

    except KeyboardInterrupt:
        print("\nRecording stopped by user.")

    finally:
        # Release resources properly
        cam.release()
        print("Camera stopped. Exiting.")
        if audio_enabled:
            stream.close()
            audio.terminate()


if __name__ == "__main__":
    record_continuous_clips(resolution=(1280, 720))  # Change resolution if needed

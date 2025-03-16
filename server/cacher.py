import os
import time
import json
import fcntl
import multiprocessing
import traceback
import logging

import llm
import moviepy

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ---------------------------------------------- #

_BASE_PATH = os.path.dirname(os.path.abspath(__file__))
BLOB_FOLDER = os.path.join("assets", "storage", "blobs")
VIDEO_FOLDER = os.path.join("assets", "storage", "video")
AUDIO_FOLDER = os.path.join("assets", "storage", "audio")

os.chdir(_BASE_PATH)


# Setup logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG or INFO depending on verbosity needed
    format="%(asctime)s [%(process)d] %(levelname)s - %(message)s",
)


class CacheAutoLoader(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self._llm = llm.Gemini()
        self._events = []

        # create folders if they don't exist
        for folder in [BLOB_FOLDER, VIDEO_FOLDER, AUDIO_FOLDER]:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def add_video_to_cache(self, video_path: str):
        """
        Same logic as your original code
        """

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"File not found: {video_path}")

        video_metadata = {
            "category": None,
            "context": None,
            "transcript": None,
            "video": video_path,
            "audio": None,
        }

        try:
            # Extract audio, get transcript, and video context
            video_clip = moviepy.VideoFileClip(video_path)
            audio_clip = video_clip.audio
            logging.info(f"Audio Clip: {audio_clip}, Video Clip: {video_clip}")
            filename = os.path.splitext(os.path.basename(video_path))[0]
            audio_file = os.path.join(AUDIO_FOLDER, filename + ".mp3")
            audio_clip.write_audiofile(audio_file, logger=None)
            video_clip.close()
            audio_clip.close()

            video_metadata["audio"] = audio_file

            # Request transcript from Gemini
            _audio_transcript = self._llm.transcript_audio(audio_file).text
            video_metadata["transcript"] = _audio_transcript

            # Request video context
            _video_context = self._llm.describe_video(video_path, _audio_transcript).text
            video_metadata["context"] = _video_context

            # Write the metadata to a JSON file
            metadata_path = os.path.join(BLOB_FOLDER, filename + ".json")
            with open(metadata_path, "w") as f:
                json.dump(video_metadata, f, indent=4)

        except Exception as e:
            logging.error(f"Error processing {video_path}: {str(e)}")
            traceback.print_exc()

    def on_created(self, event):
        """Called when a file or directory is created."""
        _filename = event.src_path
        _filename = os.path.relpath(_filename, _BASE_PATH)
        logging.info(f"{_filename} created")
        time.sleep(3)

        # Safely call add_video_to_cache
        try:
            self.add_video_to_cache(_filename)
        except Exception as e:
            logging.error(f"Error while adding video to cache: {str(e)}")
            traceback.print_exc()

    def on_modified(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_moved(self, event):
        pass


def monitor_directory(path: str):
    event_handler = CacheAutoLoader()
    observer = Observer()

    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    logging.info(f"Started monitoring {path} (press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


def worker():
    """Worker function that runs the process."""
    try:
        monitor_directory(VIDEO_FOLDER)
    except Exception as e:
        logging.error(f"Worker failed with error: {str(e)}")
        traceback.print_exc()


def start_worker():
    """Start the worker in a separate process and restart if it crashes."""
    while True:
        process = multiprocessing.Process(target=worker)
        process.start()
        process.join()  # Block until the worker process finishes

        logging.info("Worker crashed or completed. Restarting...")
        time.sleep(1)  # Optional: Add a small delay before restarting


if __name__ == "__main__":
    start_worker()

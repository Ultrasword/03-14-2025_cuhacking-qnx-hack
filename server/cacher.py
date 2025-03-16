import os
import time
import json
import fcntl

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


class CacheAutoLoader(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self._llm = llm.Gemini()

        self._events = []

        # create folders if they don't exist
        for folder in [BLOB_FOLDER, VIDEO_FOLDER, AUDIO_FOLDER]:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def is_file_locked(file_path):
        try:
            with open(file_path, 'r'):
                # Attempt to acquire an exclusive lock (non-blocking mode)
                with open(file_path, 'r') as f:
                    try:
                        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        fcntl.flock(f, fcntl.LOCK_UN)  # Release lock immediately
                        return False  # No lock, file is available
                    except IOError:
                        return True  # File is locked
        except Exception as e:
            print(f"Error checking file lock: {e}")
            return True  # Error implies file may be locked or inaccessible

    # ---------------------------------------------- #
    # logic
    # ---------------------------------------------- #

    def add_video_to_cache(self, video_path: str):
        """
        Given a video:
        1. extract audio from it and save to audio folder
        2. get transcript from audio + gemini
        3. send video get context from video + gemini
        4. create video.json file
        5. use context + transcript + (current) categories to find best category (or make a new one)
        6. update cache.json
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

        # step 1: request transcript
        # extract audio file from video
        video_clip = moviepy.VideoFileClip(video_path)
        audio_clip = video_clip.audio
        print(audio_clip, video_clip)
        filename = os.path.splitext(os.path.basename(video_path))[0]
        audio_file = os.path.join(AUDIO_FOLDER, filename + ".mp3")
        audio_clip.write_audiofile(audio_file, logger=None)
        video_clip.close()
        audio_clip.close()

        video_metadata["audio"] = audio_file

        # step 2: get transcript
        _audio_transcript = self._llm.transcript_audio(audio_file).text
        video_metadata["transcript"] = _audio_transcript

        # step 3: send video to get context from gemini
        _video_context = self._llm.describe_video(video_path, _audio_transcript).text
        video_metadata["context"] = _video_context

        # step 4: create blob file
        # determine category + etc
        print(video_metadata)
        metadata_path = os.path.join(BLOB_FOLDER, filename + ".json")
        with open(metadata_path, "w") as f:
            json.dump(video_metadata, f, indent=4)

    # ---------------------------------------------- #
    # event
    # ---------------------------------------------- #

    def on_created(self, event):
        """Called when a file or directory is created."""
        # main feature to create
        # check what the filename is
        # if it's a video, add it to the cache
        _filename = event.src_path
        # grab path relative to _BASE_PATH
        _filename = os.path.relpath(_filename, _BASE_PATH)
        print(_filename, "created")

        # Wait until the file is no longer locked
        while self.is_file_locked(_filename):
            print(f"File {_filename} is locked, waiting...")
            time.sleep(0.5)  # Sleep for 1 second before checking again

        self.add_video_to_cache(_filename)

    def on_modified(self, event):
        """Called when a file or directory is modified."""
        pass

    def on_deleted(self, event):
        """Called when a file or directory is deleted."""
        # should have no reaction -- for now
        pass

    def on_moved(self, event):
        """Called when a file or directory is moved."""
        # should have no reaction -- for now
        pass


# ---------------------------------------------- #


def monitor_directory(path: str):
    event_handler = CacheAutoLoader()
    observer = Observer()

    # Schedule the observer to monitor the specified directory recursively.
    observer.schedule(event_handler, path, recursive=True)

    # Start the observer in a separate thread.
    observer.start()
    print(f"Started monitoring {path} (press Ctrl+C to stop)")

    try:
        # Keep the script running to listen for events.
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # On a keyboard interrupt, stop the observer.
        print("Stopping the observer...")
        observer.stop()

    # Wait until the observer thread terminates.
    observer.join()
    print("Observer stopped.")


if __name__ == "__main__":
    # Replace '/path/to/directory' with the path of the directory you want to monitor.
    monitor_directory(VIDEO_FOLDER)

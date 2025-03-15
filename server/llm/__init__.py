import os
import time
import PIL

from google import genai

import moviepy

# ---------------------------------------------- #
# gemini
# ---------------------------------------------- #

API_KEY = "AIzaSyB251QquUkgdFhTUHjoWApdseA0Ffbmwl8"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_VIDEO_MODEL = "gemini-1.5-pro"


class Gemini:
    def __init__(self):
        self._client = genai.Client(api_key=API_KEY)

    # ---------------------------------------------- #
    # logic
    # ---------------------------------------------- #

    def query(self, query: str, files: list, model: str = GEMINI_MODEL):
        result = self._client.models.generate_content(
            model=model, contents=[query, *files]
        )
        return result

    def describe_image(self, image_path: str):
        image = PIL.Image.open(image_path)

        result = self.query(query="Describe the contents of this image", files=[image])
        return result

    def describe_image_sequence(self, image_paths: list):
        images = [PIL.Image.open(image_path) for image_path in image_paths]

        result = self.query(
            query="The following images are all from the same video clip. First describe what is going on in each of the images in 1 sentence. Then sumamrize the what you thiknk the context of the video clip is given all the images as the last sentence.",
            files=images,
        )
        return result

    def transcript_audio(self, audio_file: str):
        # check if file exists
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"File not found: {audio_file}")

        # upload file then request transcript
        audio = self._client.files.upload(file=audio_file)
        result = self.query(
            query="process what the audio is saying. then when you want to start actually writing down transcription (no extra comments), write a <<EOF>> and then start writing down the transcription.",
            files=[audio],
        )
        return result

    def describe_video(self, video_file: str):
        # check if file exists
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"File not found: {video_file}")

        # request transcript
        # extract audio file from video

        video_clip = moviepy.VideoFileClip(video_file)
        audio_clip = video_clip.audio
        audio_file = video_file.rsplit(".", 1)[0] + ".mp3"
        audio_clip.write_audiofile(audio_file, logger=None)

        # close both
        video_clip.close()
        audio_clip.close()

        _audio_transcript = self.transcript_audio(audio_file).text

        # send query about video file
        # upload file
        video = self._client.files.upload(file=video_file)

        # check if file got uploaded
        while video.state.name == "PROCESSING":
            time.sleep(0.3)
            video = self._client.files.get(name=video.name)

        if video.state.name == "FAILED":
            raise Exception("Failed to upload video", video.state.name)

        # send request for video
        result = self.query(
            query="Describe what is going on in this video clip",
            files=[video],
            model=GEMINI_VIDEO_MODEL,
        )

        return result

    def retrieve_request(self, request_result):
        return request_result.text

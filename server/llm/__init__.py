import os
import time
import PIL

from google import genai

import moviepy

# ---------------------------------------------- #
# gemini
# ---------------------------------------------- #

API_KEY = "AIzaSyC4hI8PGw7-jXe7loDCVTk6P2RwbCh3xGc"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_VIDEO_MODEL = "gemini-1.5-pro"


class Gemini:
    def __init__(self):
        self._client = genai.Client(api_key=API_KEY)

        self._running_chats = {}

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
            query="process what the audio is saying. then when you want to start actually writing down transcription (no extra comments).",
            files=[audio],
        )
        return result

    def describe_video(self, video_file: str, audio_transcript: str):
        # check if file exists
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"File not found: {video_file}")

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
            query=f"you are a professional scene analyzer that gives out great short descriptions of what the topic is in short video clips. you're given a transcript and a video clip and your goal is to output a short description of the context of the scene.  Here is the transcript: {audio_transcript}. The video is attached. Tell me the context of this scene in 1-2 sentences.",
            files=[video],
            model=GEMINI_VIDEO_MODEL,
        )

        return result

    def categorize_context(self, context: str, categories: list, transcript: str):
        # given a set of categories + context + transcript of the video
        # determine if an existing category is good
        # or make a new one

        query_string = f"""
        You are an AI engine that is designed to return relevant keywords that categorize a video based on its context and transcript.

Available categories: {", ".join(categories)}

Video Context: {context}
Video transcript: {transcript}

Return only matching categories in a JSON array format with a key called 'matching_categories'. If there are no valid matching categories, set the "new_category" key to be what you think the new category should be.
Just output the raw json. do not output anything else. NO need for formatting -- just text.
For example: {{"matching_categories": ["category1", "category2"], "new_category": null}}
        """

        result = self.query(query=query_string, files=[])
        return result

    def search_related_categories(self, search: str, cache_json: str):
        # load up the categories
        # search for related categories

        pass

    def retrieve_request(self, request_result):
        return request_result.text

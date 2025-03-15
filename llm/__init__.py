import os
import PIL
from google import genai

# ---------------------------------------------- #
# gemini
# ---------------------------------------------- #

API_KEY = "AIzaSyB251QquUkgdFhTUHjoWApdseA0Ffbmwl8"
GEMINI_MODEL = "gemini-2.0-flash"


class Gemini:
    def __init__(self):
        self._client = genai.Client(api_key=API_KEY)

    # ---------------------------------------------- #
    # logic
    # ---------------------------------------------- #

    def query(self, query: str, images: list):
        result = self._client.models.generate_content(
            model=GEMINI_MODEL, contents=[query, *images]
        )
        return result

    def describe_image(self, image_path: str):
        image = PIL.Image.open(image_path)

        result = self.query(query="Describe the contents of this image", images=[image])
        return result

    def describe_image_sequence(self, image_paths: list):
        images = [PIL.Image.open(image_path) for image_path in image_paths]

        result = self.query(
            query="The following images are all from the same video clip. First describe what is going on in each of the images in 1 sentence. Then sumamrize the what you thiknk the context of the video clip is given all the images as the last sentence.",
            images=images,
        )
        return result

    def transcript_audio(self, audio_file: str):
        # check if file exists
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"File not found: {audio_file}")

        # upload file then request transcript
        audio = self._client.files.upload(file=audio_file)
        result = self._client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                "process what the audio is saying. then when you want to start actually writing down transcription (no extra comments), write a <<EOF>> and then start writing down the transcription.",
                audio,
            ],
        )
        return result

    # def describe_video(self)

    def retrieve_request(self, request_result):
        return request_result.text

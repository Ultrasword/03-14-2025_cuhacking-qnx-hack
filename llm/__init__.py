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

    def query(self, query: str):
        result = self._client.models.generate_content(
            model=GEMINI_MODEL, contents=query
        )
        return result

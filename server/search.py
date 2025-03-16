from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
import os
import json
import re
from llm import Gemini  # Ensure this is properly imported

app = FastAPI()

# CORS setup to allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client
gemini_client = Gemini()

def iterfile(video_paths: List[str]):
    for video_path in video_paths:
        with open(video_path, "rb") as video_file:
            while chunk := video_file.read(1024 * 1024 * 4):  # Read in chunks of 4MB
                yield chunk

@app.get("/search_video")
async def search_categories(query: str):
    BLOB_FOLDER = os.path.join("assets", "storage", "blobs")

    if not os.path.exists(BLOB_FOLDER):
        # make path
        os.makedirs(BLOB_FOLDER)

    all_video_info = ""

    for filename in os.listdir(BLOB_FOLDER):
        if filename.endswith(".json"):
            file_path = os.path.join(BLOB_FOLDER, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    all_video_info += (
                        f.read() + "\n"
                    )  # Add newline for separation between json objects

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Error reading {filename}: {e}"
                )

    prompt = f"""
You are an advanced AI engine tasked with finding the most relevant video context based on a given search query. You will be provided with a set of video contexts and their corresponding audio transcripts. Your objective is to identify the video/audio pairs that best align with the provided search query. Return the JSON objects for up to 3 video/audio pairs that most accurately match the query. You are not required to return 3, but you must provide at least one relevant result. If no context matches the query closely, respond with "no match."

Return the data in the following format:


{
  "matches": [
    {
      "category": null,
      "context": "Brief description of the scene",
      "transcript": "Transcript of the video",
      "video": "Path to the video file",
      "audio": "Path to the audio file"
    },
    ...
    (up to 3 relevant matches)
  ]
}
Search query: {query}

Various video json objects: {all_video_info if all_video_info else "No video json objects found"}

"""
    result = gemini_client.query(query=prompt, files=[])  # Removed empty files list

    response_text = gemini_client.retrieve_request(result)

    pattern = r"```json(.*?)```"

    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        response_text = match.group(1).strip()
    try:
        selected_blob = json.loads(response_text)

        matches = selected_blob.get("matches", [])
        video_paths = [match["video"] for match in matches[:3]]

        print(f"video paths: {video_paths}")

        for path in video_paths:
            if not os.path.exists(path):
                raise HTTPException(status_code=404, detail="Video file not found")

        for path in video_paths:
         if not os.path.exists(path):
                return {"error": f"File {path} not found"}

         return StreamingResponse(iterfile(video_paths), media_type="video/mp4")

    except json.JSONDecodeError:
        raise HTTPException(status_code=404, detail="Search failed")

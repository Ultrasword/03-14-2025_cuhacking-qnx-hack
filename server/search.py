from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
You are an AI engine that needs to determine which video context most closely matches the search query. You will be given a set of video contexts, along with their audio transcripts and need to determine which one closely matches the provided search query. You are to only return the provided json object for the video/audio pair you choose to be the most accurate. 

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
        video_path = selected_blob["video"]

        print(f"Selected video: {video_path}")

        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")

        def iterfile():
            with open(video_path, "rb") as video_file:
                while chunk := video_file.read(
                    1024 * 1024 * 4
                ):  # Read in chunks of 1MB
                    yield chunk

        return StreamingResponse(iterfile(), media_type="video/mp4")

    except json.JSONDecodeError:
        raise HTTPException(status_code=404, detail="Search failed")

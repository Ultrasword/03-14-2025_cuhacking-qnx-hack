from fastapi import FastAPI, HTTPException
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

    print(f"Searching for: {query}")
    
    if not os.path.exists(BLOB_FOLDER):
        # make path
        os.makedirs(BLOB_FOLDER)
    
    print(f"Filepath to search: {BLOB_FOLDER}")

    all_video_info = ""
    
    for filename in os.listdir(BLOB_FOLDER):
        if filename.endswith('.json'):
            file_path = os.path.join(BLOB_FOLDER, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_video_info += f.read() + "\n"  # Add newline for separation between json objects
                    
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Error reading {filename}: {e}"
                )
    
    try:
        prompt = f"""
You are an AI engine that needs to determine which video context most closely matches the search query. You will be given a set of video contexts, along with their audio transcripts and need to determine which one closely matches the provided search query. You are to only return the provided json object for the video/audio pair you choose to be the most accurate. 

Search query: {query}

Various video json objects: {all_video_info if all_video_info else "No video json objects found"}

If there are no json objects found, just return "NULL" on its own.

"""
        result = gemini_client.query(query=prompt, files=[])  # Removed empty files list
        print(f"The request: {prompt}\n\n")

        response_text = gemini_client.retrieve_request(result)
        print(f"The response: {response_text}")

        pattern = r"```json(.*?)```"

        if response_text == "NULL":
            raise HTTPException(status_code=404, detail="No video context found")
        
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            response_text = match.group(1).strip()
        
        try:
            selected_blob = json.loads(response_text)
            video_title = selected_blob["video"]
            video_path = os.path.join(BLOB_FOLDER, video_title)
            
            if not os.path.exists(video_path):
                raise HTTPException(status_code=404, detail="Video file not found")
            
            video_file = open(video_path, "rb")  # Open the video file in binary read mode
            return StreamingResponse(video_file, media_type="video/mp4")

        except json.JSONDecodeError:
            raise HTTPException(
                status_code=404, detail="Search failed"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )

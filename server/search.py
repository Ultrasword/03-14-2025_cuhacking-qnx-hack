from pydantic import BaseModel
import json
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

import re

# Import the Gemini class from the parent directory
import sys

from llm import Gemini  # Import your Gemini class


app = FastAPI()


class SearchRequest(BaseModel):
    query: str  # User's search query


# Initialize the Gemini client
gemini_client = Gemini()


@app.get("/search_video")
async def search_categories(query: str):
    BLOB_FOLDER = os.path.join("assets", "storage", "blobs")
    
    if not os.path.exists(BLOB_FOLDER) or not os.listdir(BLOB_FOLDER):
        raise HTTPException(status_code=404, detail="Blob folder is empty or doesn't exist")
    
    all_video_info = ""
    
    for filename in os.listdir(BLOB_FOLDER):
        if filename.endswith('.json'):
            file_path = os.path.join(BLOB_FOLDER, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Read file content and concatenate
                    all_video_info += f.read() + "\n"  # Add newline for separation between json objects
                    
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Error reading {filename}: {e}"
                )
    
    try:
        prompt = f"""You are an AI engine that needs to determine which video context most closely matches the search query. You will be given a set of video contexts, along with their audio transcripts and need to determine which one closely matches the provided search query. You are to only return the provided json object for the video/audio pair you choose to be the most accurate. 
Search query: {query}
Various video json objects: {all_video_info}
"""


        # Query Gemini using the class
        result = gemini_client.query(query=prompt, files=[])  # Removed empty files list

        # Get the text response
        response_text = gemini_client.retrieve_request(result)
        print(response_text)

        pattern = r"^```json(.*?)```$"
        
        if re.match(pattern, response_text, re.DOTALL):
            response_text = re.sub(r"^```json|```$", "", response_text).strip()
        

        # Parse the JSON from the text response
        try:
            selected_blob = json.loads(response_text)
            video_title = selected_blob["video"]
            video_file = open(video_title, "rb")  # Open the video file in binary read mode
            return StreamingResponse(video_file, media_type="video/mp4")

        except json.JSONDecodeError:
            raise HTTPException(
                status_code=404, detail="Search failed"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )

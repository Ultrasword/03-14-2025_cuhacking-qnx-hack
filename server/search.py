from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import re
from typing import List

# Import the Gemini class from the parent directory
import sys
sys.path.append('..')  # Add parent directory to path if needed
from gemini import Gemini  # Import your Gemini class

# Path to categories file - update this path as needed
CATEGORY_FILE = "categories.json"  # Update this to the correct path

class SearchRequest(BaseModel):
    query: str  # User's search query

# Initialize the Gemini client
gemini_client = Gemini()

# Read categories from categories.json
def load_categories():
    try:
        with open(CATEGORY_FILE, "r") as f:
            categories_data = json.load(f)
            return categories_data.get("categories", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading categories: {e}")

async def search_categories(query: str):
    query = query.lower()  # Normalize query to lowercase
    
    # Load categories
    categories = load_categories()
    
    try:
        # Create the prompt for Gemini with instructions, categories, and query
        categories_str = ", ".join(categories)
        
        prompt = f"""You are an AI engine that is designed to return relevant keywords that match the search query.
        
Available categories: {categories_str}

Search query: {query}

Return only matching categories in a JSON array format with a key called 'matching_categories'. 
For example: {{"matching_categories": ["category1", "category2"]}}"""

        # Query Gemini using the class
        result = gemini_client.query(query=prompt, files=[])
        
        # Get the text response
        response_text = gemini_client.retrieve_request(result)
        
        # Parse the JSON from the text response
        try:
            # Handle potential text before or after the JSON
            # Try to extract just the JSON part
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            result_json = json.loads(response_text)
            
            if "matching_categories" not in result_json:
                raise ValueError("Response doesn't contain matching_categories")
            
            # Validate that all returned categories are in the original list
            valid_categories = [cat for cat in result_json["matching_categories"] if cat in categories]
            
            return {"matching_categories": valid_categories}
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON response from Gemini")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
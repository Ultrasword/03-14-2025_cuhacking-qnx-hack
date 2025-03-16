"use client";

import { useState, useEffect } from "react";
import './styles.css'; // Import the CSS file

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [videoUrl, setVideoUrl] = useState<string | null>(null); // Store the video URL
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    console.log("Client-side only");
  }, []);



  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Searching for:", searchQuery);
    setHasSearched(true);

    try {
      // Make the GET request to search endpoint
      const response = await fetch(`http://127.0.0.1:8000/search_video?query=${encodeURIComponent(searchQuery)}`);

      if (!response.ok) {
        throw new Error("Failed to fetch video");
      }

      // The backend returns a streaming response, so we need to convert it into a blob
      const videoBlob = await response.blob();
      
      if (videoBlob.size > 0) {
        // Create a URL for the video blob and set it as the video source
        const videoUrl = URL.createObjectURL(videoBlob);
        setVideoUrl(videoUrl);
      } else {
        setVideoUrl(null); // If no video is matched or returned, reset the video URL
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="container">
      <h1 className="heading">AI-Powered Video Search</h1>
      <p className="subheading">Find moments from your day with AI-assisted search.</p>

      <form onSubmit={handleSearch} className="form">
        <div className="input-group">
          <input
            type="text"
            placeholder="Search videos..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-field"
          />
          <button type="submit" className="button">
            Search
          </button>
        </div>
      </form>

      {/* Displaying the video */}
      <div className="video-results">
        {videoUrl ? (
          <div className="video-item">
            <video controls className="video-player">
              <source src={videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        ) : hasSearched ? (
          <p>No video found for the search term.</p>
        ) : null}
      </div>
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import "./styles.css"; // Import the CSS file

import ReactPlayer from "react-player";

const BACKEND_IP: string = "http://10.0.0.218:8000";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [videoUrl, setVideoUrl] = useState<string | null>(null); // Store the video URL
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    console.log("Client-side only");
  }, []);

  useEffect(() => {
    console.log(videoUrl);
  }, [videoUrl]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Searching for:", searchQuery);
    setHasSearched(true);

    try {
      // Make the GET request to search endpoint
      const response = await fetch(
      `${BACKEND_IP}/search_video?query=${encodeURIComponent(searchQuery)}`
      );

      if (!response.ok) {
      throw new Error("Failed to fetch video");
      }

      // Get the video blob directly from the response
      const videoBlob = await response.blob();
      console.log("Video Blob:", videoBlob.size, videoBlob.type, videoBlob);

      if (videoBlob.size > 0) {
      // Create a URL for the video blob and set it as the video source
      const videoUrl = URL.createObjectURL(videoBlob);
      setVideoUrl(videoUrl);
      console.log("Video URL:", videoUrl);
      } else {
      setVideoUrl(null); // If no video is returned, reset the video URL
      console.log("No video found for the search term:", searchQuery);
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

      {hasSearched && !videoUrl && (
        <div className="error-message" style={{ color: "black" }}>
          No video found for the search term &quot;{searchQuery}&quot;.
        </div>
      )}

      {/* Display and play the video using the HTML5 video player */}
      {videoUrl && (
        <ReactPlayer
          url={videoUrl}
          controls
          autoPlay
          width="640px"
          height="360px"
          style={{ marginTop: "1rem" }}
        />
        // <video width={640} height={360} controls>
        //   <source src={videoUrl} type="video/mp4" />
        //   Your browser does not support the video tag.
        // </video>
      )}
    </div>
  );
}

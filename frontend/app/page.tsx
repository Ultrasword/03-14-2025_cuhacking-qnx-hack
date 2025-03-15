"use client";

import { useState, useEffect } from "react";
import './styles.css'; // Import the CSS file

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [videos, setVideos] = useState<any[]>([]); 
  const [hasSearched, setHasSearched] = useState(false); // Add this state

  useEffect(() => {
    console.log("Client-side only");
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Searching for:", searchQuery);
    setHasSearched(true); // Set this to true when search is performed

    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch videos");
      }

      const data = await response.json();
      setVideos(data.videos);
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

      {/* Displaying the Videos */}
      <div className="video-results">
        {videos.length > 0 ? (
          videos.map((video) => (
            <div key={video.id} className="video-item">
              <img src={video.thumbnail} alt={video.title} className="video-thumbnail" />
              <h3 className="video-title">{video.title}</h3>
              <p className="video-description">{video.description}</p>
              <a href={video.url} target="_blank" rel="noopener noreferrer" className="watch-link">
                Watch
              </a>
            </div>
          ))
        ) : hasSearched ? (
          <p>No videos found</p>
        ) : null}
      </div>
    </div>
  );
}
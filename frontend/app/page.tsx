"use client";

import { useState, useEffect } from "react";
import './styles.css'; // Import the CSS file


const BACKEND_IP: string = "http://10.0.0.218:8000";


export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [videoUrl, setVideoUrl] = useState<string | null>(null); // Store the video URL
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    console.log("Client-side only");
  }, []);

  useEffect(() => {
    console.log(videoUrl)
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

      console.log(response);

      if (!response.ok) {
        throw new Error("Failed to fetch video");
      }

      // The backend returns the raw bytes of the video file
      const videoBlob = await response.blob();

      if (videoBlob.size > 0) {
        // If the browser supports the File System Access API,
        // attempt to save the video file without prompting the user.
        // Note: In many browsers, writing to disk silently is restricted.
        if ("showSaveFilePicker" in window) {
          try {
            const options = {
              suggestedName: "video.mp4",
              types: [
                {
                  description: "MP4 Video",
                  accept: { "video/mp4": [".mp4"] },
                },
              ],
            };
            // The file picker may still prompt the user for permission.
            const handle = await (window as any).showSaveFilePicker(options);
            const writable = await handle.createWritable();
            await writable.write(videoBlob);
            await writable.close();
          } catch (savingError) {
            console.error("Error saving file:", savingError);
          }
        }

        // Create a URL for the video blob and set it as the video source
        const videoUrl = URL.createObjectURL(videoBlob);
        setVideoUrl(videoUrl);
      } else {
        setVideoUrl(null); // If no video is returned, reset the video URL
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
        <div className="error-message" style={{color: "black"}}>
          No video found for the search term &quot;{searchQuery}&quot;.
        </div>
      )}

      {/* Displaying the video */}
      {videoUrl && (
        <Video url={videoUrl} />
      )}
    </div>
  );
}

function Video({ url }: { url: string }) {
  return (
    <video controls src={url} />
  );
}

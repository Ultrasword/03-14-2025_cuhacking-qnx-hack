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
      ).then((res) => {
        console.log(res);

        if (!res.ok) {
          throw new Error("Failed to fetch video");
        }

        // backend returns raw byte sof video file as a streamign response
        if (!res.body) {
          throw new Error("ReadableStream not supported in this browser.");
        }
        return res;
      });

      // The backend returns the raw bytes of the video file as a streaming response
      if (!response.body) {
        throw new Error("ReadableStream not supported in this browser.");
      }
      const reader = response.body.getReader();
      const chunks: Uint8Array[] = [];
      let receivedLength = 0;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        if (value) {
          chunks.push(value);
          receivedLength += value.length;
        }
      }

      // Combine the chunks into a single Uint8Array
      const videoArray = new Uint8Array(receivedLength);
      let position = 0;
      for (const chunk of chunks) {
        videoArray.set(chunk, position);
        position += chunk.length;
      }
      console.log(videoArray)

      // Create a video blob from the streamed data
      const videoBlob = new Blob([videoArray], { type: "video/mp4" });

      if (videoBlob.size > 0) {
        // Cache the video file using the Cache API
        try {
          const cache = await caches.open("video-cache");
          const cacheResponse = new Response(videoBlob, {
            headers: { "Content-Type": "video/mp4" },
          });
          await cache.put("/cached-video.mp4", cacheResponse).then(() => {
            console.log("Video cached successfully as '/cached-video.mp4'.");
          });
        } catch (cacheError) {
          console.error("Error caching video:", cacheError);
        }

        // Create a URL for the video blob and set it as the video source
        const videoUrl = URL.createObjectURL(videoBlob);
        setVideoUrl(videoUrl);

        console.log("Video URL:", videoUrl);
      } else {
        setVideoUrl(null); // If no video is returned, reset the video URL
      }

      console.log("Video URL:", videoUrl);
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

import React from "react";

import { BACKEND_IP } from "../constants";
import ReactPlayer from "react-player";

import styles from "./styles/ContentCard.module.css";

// -------------------------------------------------------- //

interface ContentCardProps {
  filename: string;
}

// -------------------------------------------------------- //

export function ContentCard({ filename }: ContentCardProps) {
  const [videoUrl, setVideoUrl] = React.useState<string | null>(null);
  const [context, setContext] = React.useState<string | null>(null);
  const errorRef = React.useRef<HTMLDivElement>(null);

  // -------------------------------------------------------- //
  // query backend for video context

  React.useEffect(() => {
    async function fetchContext() {
      try {
        // now query for the video context
        const contextResponse = await fetch(
          `${BACKEND_IP}/get_video_context?video_path=${encodeURIComponent(filename)}`
        );
        if (!contextResponse.ok) {
          throw new Error(`Error fetching video context: ${contextResponse.statusText}`);
        }

        const contextJson = await contextResponse.json();
        setContext(contextJson.context);
      } catch (error) {
        console.log(error);
      }

      // console.log(context);
    }

    if (filename) {
      fetchContext();
    }
  }, [filename]);

  // -------------------------------------------------------- //
  // send request to backend to get video on first render

  React.useEffect(() => {
    async function fetchVideo() {
      try {
        // fetch video data
        const response = await fetch(
          `${BACKEND_IP}/get_video_file?video_path=${encodeURIComponent(filename)}`
        );
        if (!response.ok) {
          errorRef.current?.style.setProperty("display", "none");
          throw new Error(`Error fetching video: ${response.statusText}`);
        }

        // convert data to json
        const videoBlob = await response.blob();

        if (videoBlob.size > 0) {
          const url = URL.createObjectURL(videoBlob);
          setVideoUrl(url);
        } else {
          setVideoUrl(null);
          errorRef.current?.style.setProperty("display", "block");
          console.log("Failed to load video:", filename);
        }
      } catch (error) {
        console.log(error);
        if (errorRef.current) {
          errorRef.current.textContent = `Failed to load video: ${error}`;
        }
      }
    }

    if (filename) {
      fetchVideo();
    }
  }, [filename]);
  // -------------------------------------------------------- //

  return (
    <div ref={errorRef} className={styles["container"]}>
      <div className={styles["card"]}>
        <div className={styles["video-container"]}>
          {/* <img src={filename} alt="video" className={styles["thumbnail"]} /> */}
          <ReactPlayer
            url={videoUrl ? videoUrl : ""}
            controls
            width="100%"
            height="auto"
            playing={false}
            config={{
              youtube: {
                playerVars: { modestbranding: 1, color: "white" },
              },
            }}
          />
        </div>
        <div className={styles["video-subtext"]}>{filename}</div>
      </div>

      {/* other informatino i can grab from backend */}
      <div className={styles["context-container"]}>
        <div className={styles["context"]}>Context: {context}</div>
      </div>
    </div>
  );
}

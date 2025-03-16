"use client";

import React from "react";

import { SectionProps } from "../constants";
import { ContentCard } from "./ContentCard";

import styles from "./styles/Library.module.css";

// -------------------------------------------------------- //

export function Library({ globals }: SectionProps) {
  // -------------------------------------------------------- //

  return (
    <div className={styles["container"]}>
      {globals.isSearching.getter && globals.result.urls.getter == null && (
        <div className="error-message" style={{ color: "black" }}>
          No video found for the search term &quot;{globals.searchQuery.getter}&quot;.
        </div>
      )}

      <div
        className={styles["card-container"]}
        style={{ gridTemplateColumns: `repeat(${Math.max(1, globals.result.size.getter)}, 1fr)` }}
      >
        {globals.result.urls.getter != null &&
          globals.result.urls.getter?.map((url, index) => {
            // if (index !== 1) {
            //   return null;
            // }

            if (url == null) {
              return null;
            }

            return <ContentCard key={index} filename={url} />;
          })}
      </div>

      {/* Display and play the video using the HTML5 video player */}
      {/* {videoUrl && (
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
      )} */}
    </div>
  );
}

import styles from "./styles/hero.module.css";

import { BACKEND_IP } from "../constants";
import { SectionProps } from "../constants";

import React from "react";

// -------------------------------------------------------- //

export function HeroSection({ globals }: SectionProps) {
  const [subBarText, setSubBarText] = React.useState<string>("");

  // -------------------------------------------------------- //
  // handle search
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    // reset available urls
    globals.result.urls.setter([]);
    console.log("Searching for:", globals.searchQuery.getter);
    globals.isSearching.setter(true);

    try {
      // Make the GET request to search endpoint
      await fetch(
        `${BACKEND_IP}/search_video?query=${encodeURIComponent(globals.searchQuery.getter)}`
      )
        .then((res) => {
          res.json().then((data) => {
            console.log(data);
            if (res.status !== 200) {
              console.error("Failed to fetch video:", data);
              setSubBarText(`There are no videos related to: ${globals.searchQuery.getter}`);
              globals.result.urls.setter([]);
              return;
            }
            globals.result.urls.setter(data);
            setSubBarText(`Found ${data.length} videos related to: ${globals.searchQuery.getter}!`);
            // console.log("URLs:", data);
          });
        })
        .catch((err) => {
          console.error("Failed to fetch video:", err);
        });
    } catch (error) {
      // TODO -- failed to fetch URL results
      console.error("Error:", error);
    }
    globals.isSearching.setter(false);
  };

  return (
    <div className={`${styles["container"]} morphing-gradient`}>
      <div className={styles["header-content"]}>
        <h1 className={styles["title"]}>Daily Vibez</h1>
        <p className={styles["subtitle"]}>
          For the the wonderful fuzzy warm memories of everyday life~
        </p>
      </div>

      <div className={styles["form-container"]}>
        <form onSubmit={handleSearch} className={styles["form"]}>
          <div className={styles["input-container"]}>
            <input
              type="text"
              placeholder="Search videos..."
              value={globals.searchQuery.getter}
              onChange={(e) => globals.searchQuery.setter(e.target.value)}
              className={styles["input"]}
            />
            <button
              type="submit"
              className={styles["button"]}
              onClick={(e) => {
                if (!globals.searchQuery.getter.trim()) {
                  e.preventDefault();
                  console.log("Search query is empty");
                  return;
                }
              }}
            >
              Search
            </button>
          </div>
        </form>
        <div className={styles["subbar-container"]}>{subBarText}</div>
      </div>
    </div>
  );
}

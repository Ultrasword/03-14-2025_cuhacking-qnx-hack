"use client";

import React from "react";

import { HeroSection } from "./components/Hero";
import { Library } from "./components/LIbrary";
import { MorphingGradient } from "./components/MorphingGradient";

import { ApplicationProps } from "./constants";

import styles from "./page.module.css";
// -------------------------------------------------------- //

export default function Home() {
  const [isSearching, setIsSearching] = React.useState<boolean>(false);
  const [searchQuery, setSearchQuery] = React.useState<string>("");
  const [videoURLs, setVideoURLs] = React.useState<(string | null)[]>([]);
  const [videoURLsSize, setVideoURLsSize] = React.useState<number>(0);

  const appProps: ApplicationProps = {
    isSearching: { getter: isSearching, setter: setIsSearching },
    searchQuery: { getter: searchQuery, setter: setSearchQuery },
    result: {
      urls: { getter: videoURLs, setter: setVideoURLs },
      size: { getter: videoURLsSize, setter: setVideoURLsSize },
    },
  };

  React.useEffect(() => {
    appProps.result.size.setter(appProps.result.urls.getter?.length);
  }, [appProps.result.urls.getter, appProps.result.size]);

  return (
    <div>
      <div className={styles["container"]}>
        <HeroSection globals={appProps} />
        <Library globals={appProps} />
      </div>
      <MorphingGradient />
    </div>
  );
}

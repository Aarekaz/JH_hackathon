"use client";
import React, { useEffect, useState } from "react";

import LeftChart from "../components/parliament/LeftChart";
import RightChat from "../components/parliament/RightChat";
import axios from "axios";

const ParliamentPage: React.FC = () => {
  const [paperInfo, setPaperInfo] = useState<any>(null);

  // Fetch paper info from localStorage and API (client-side only)
  useEffect(() => {
    // Access localStorage only in useEffect
    const paperid = localStorage.getItem("paperid");
    const cachedPaperInfo = localStorage.getItem("paper_info");

    if (cachedPaperInfo) {
      setPaperInfo(JSON.parse(cachedPaperInfo));
    }

    if (paperid) {
      axios.get(`http://localhost:8000/papers/${paperid}`).then((response) => {
        setPaperInfo(response.data);
        localStorage.setItem("paper_info", JSON.stringify(response.data));
      });
    }
  }, []); // Run only once on mount

  return (
    <div className="flex w-full h-screen">
      <div className="w-9/12 h-full">
        {paperInfo && (
          <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">{paperInfo.title}</h2>
            <p>{paperInfo.summary}</p>
          </div>
        )}
        <LeftChart />
      </div>
      <div className="w-3/12 h-full">
        <RightChat />
      </div>
    </div>
  );
};

export default ParliamentPage;

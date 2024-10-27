"use client";
import React, { useEffect, useState } from "react";

import LeftChart from "../components/parliament/LeftChart";
import RightChat from "../components/parliament/RightChat";
import axios from "axios";
const ParliamentPage: React.FC = () => {
  const paperid = localStorage.getItem("paperid");
  const [paperInfo, setPaperInfo] = useState<any>();
  
  // if you get paperid, fetch paper info from this url /papers/{paper_id} using axios
  useEffect(() => {
    if (paperid) {
      axios.get(`http://localhost:8000/papers/${paperid}`).then((response) => {
        setPaperInfo(response.data);
      });
    }
  }, [paperid]);

  

  // {
  //   "for": 1,
  //   "against": 0,
  //   "abstain": 3,
  //   "total": 4,
  //   "result": "passed"
  // }

  console.log("paperInfo", paperInfo);
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

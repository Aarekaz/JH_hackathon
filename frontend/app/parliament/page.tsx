"use client";
import React from "react";
import { useLocation } from "react-router-dom";
import LeftChart from "../components/parliament/LeftChart";
import RightChat from "../components/parliament/RightChat";

const ParliamentPage: React.FC = () => {
  const location = useLocation();
  const paper = location.state?.paper;

  return (
    <div className="flex w-full h-screen">
      <div className="w-9/12 h-full">
        {paper && (
          <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">{paper.title}</h2>
            <p>{paper.summary}</p>
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


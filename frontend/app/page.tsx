
"use client"
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./components/LandingPage";
import ParliamentPage from "./parliament/page";

const Home: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/parliament" element={<ParliamentPage />} />
        {/* Add other routes here */}
      </Routes>
    </Router>
  );
};

export default Home;

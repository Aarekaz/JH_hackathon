"use client";
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const LandingPage: React.FC = () => {
  const [papers, setPapers] = useState<any[]>([]);
  const navigate = useNavigate();

  // Function to fetch papers from the backend
  const getArxivPapers = async () => {
    try {
      const response = await axios.post(
        "http://localhost:8000/papers/arxiv/import?max_results=6",
        [],
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error("Failed to fetch papers:", error);
      alert("Failed to upload file");
      return [];
    }
  };

  // useEffect to fetch papers on component mount
  useEffect(() => {
    console.log("useEffect is invoked.");
    getArxivPapers().then((data) => {
      console.log(data);
      setPapers(data);
    });
  }, []); 

  const handleStartDebate = (paper: any) => {
    localStorage.setItem("paperid", paper.id);
    navigate("/parliament");
  };

  return (
    <div className="flex justify-center items-center h-screen">
      <section className="flex flex-col justify-center items-center h-full w-full">
        <div className="flex flex-col justify-center items-center gap-5 max-md:flex-col">
          <div className="flex flex-col w-[74%] max-md:ml-0 max-md:w-full">
            <div className="flex z-10 flex-col self-stretch my-auto mr-0 font-light text-black max-md:mt-10 max-md:max-w-full text-center">
              <h1 className="text-5xl max-md:max-w-full max-md:text-4xl">
                <span className="font-bold text-indigo-600">AI parliament</span>{" "}
                for regulations checking of new policies
              </h1>
              <p className="self-start mt-4 ml-11 text-3xl max-md:max-w-full">
                Let the AI decide which policy is good in a{" "}
                <span className="font-bold text-indigo-600">debate</span>{" "}
                session.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
              {papers.map((paper, index) => (
                <div
                  key={index}
                  className="relative bg-white shadow-md rounded-lg p-4 hover:shadow-lg transition-shadow duration-300 group"
                >
                  <h2 className="text-xl font-normal mb-6">{paper.title}</h2>
                  <button
                    onClick={() => handleStartDebate(paper)}
                    className="absolute mt-4 bottom-4 left-4 right-4 bg-indigo-600 text-white py-2 px-4 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  >
                    Start Debate
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;

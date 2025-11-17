'use client';

import React, { useEffect, useState } from "react";

const LeftChart = () => {
  const [votesFor, setVotesFor] = useState(0);
  const [votesAgainst, setVotesAgainst] = useState(0);
  const [votesAbstain, setVotesAbstain] = useState(0);
  const [votesResult, setVotesResult] = useState("");
  const [chartLoaded, setChartLoaded] = useState(false);

  useEffect(() => {
    // Load summary from localStorage (only runs on client)
    const summary = JSON.parse(localStorage.getItem("summary") || "{}");
    setVotesFor(summary.for || 0);
    setVotesAgainst(summary.against || 0);
    setVotesAbstain(summary.abstain || 0);
    setVotesResult(summary.result || "");

    // Dynamically import Highcharts only on client-side
    const initializeChart = async () => {
      try {
        const Highcharts = (await import('highcharts')).default;
        const HighchartsItem = (await import('highcharts/modules/item-series')).default;

        // Initialize the item module
        if (typeof HighchartsItem === 'function') {
          HighchartsItem(Highcharts);
        }

        // Create the chart
        Highcharts.chart("container", {
          chart: {
            type: "item",
          },
          title: {
            text: "Distribution of seats for AI member of parliaments",
          },
          subtitle: {
            text: "",
          },
          legend: {
            labelFormat: '{name} <span style="opacity: 0.4">{y}</span>',
          },
          series: [
            {
              name: "Representatives",
              keys: ["name", "y", "color", "label"],
              data: [
                [
                  "Corporations (Prioritize innovation and minimal regulations)",
                  45,
                  "#DA0211",
                  "Corporations",
                ],
                [
                  "Government (Seek a balance between innovation and public safety)",
                  45,
                  "#2CAFFE",
                  "Government",
                ],
                [
                  "Academics (Focus on long-term risks, ethical implications, and AI safety)",
                  45,
                  "#FDA003",
                  "Academics",
                ],
                [
                  "Civil Rights Advocates (Champion fairness, transparency, and social impact)",
                  45,
                  "#000099",
                  "CRA",
                ],
              ],
              dataLabels: {
                enabled: true,
                format: "{point.label}",
                style: {
                  textOutline: "3px contrast",
                },
              },
              // Circular options
              center: ["50%", "88%"],
              size: "170%",
              startAngle: -100,
              endAngle: 100,
            },
          ],
          responsive: {
            rules: [
              {
                condition: {
                  maxWidth: 600,
                },
                chartOptions: {
                  series: [
                    {
                      dataLabels: {
                        distance: -30,
                      },
                    },
                  ],
                },
              },
            ],
          },
        });

        setChartLoaded(true);
      } catch (error) {
        console.error("Failed to load Highcharts:", error);
      }
    };

    initializeChart();
  }, []);

  return (
    <div className="h-full flex flex-col items-center justify-center">
      <div id="container" style={{ width: "100%", height: "50%" }}>
        {!chartLoaded && (
          <div className="flex items-center justify-center h-full">
            <p>Loading chart...</p>
          </div>
        )}
      </div>
      <div className="votes bg-white shadow-md rounded-lg p-6 mt-6 w-full max-w-2xl">
        <h2 className="text-2xl font-bold mb-4 text-center">Votes Summary</h2>
        <div className="flex justify-around gap-4">
          <div className="text-center">
            <h3 className="text-lg font-semibold">For</h3>
            <p className="text-xl">{votesFor}</p>
          </div>
          <div className="text-center">
            <h3 className="text-lg font-semibold">Against</h3>
            <p className="text-xl">{votesAgainst}</p>
          </div>
          <div className="text-center">
            <h3 className="text-lg font-semibold">Abstain</h3>
            <p className="text-xl">{votesAbstain}</p>
          </div>
          <div className="text-center">
            <h3 className="text-lg font-semibold">Result</h3>
            <p className="text-xl">{votesResult}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeftChart;

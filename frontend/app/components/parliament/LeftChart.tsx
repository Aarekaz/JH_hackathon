import React, { useEffect, useState } from "react";
import Highcharts from "highcharts";
import HighchartsItem from "highcharts/modules/item-series";

// Initialize the item module
HighchartsItem(Highcharts);

const LeftChart = () => {
  // const debate_id = localStorage.getItem("debate_id");
  const summary = JSON.parse(localStorage.getItem("summary") || "{}");

  const [votesFor, setVotesFor] = useState(summary.for || 0);
  const [votesAgainst, setVotesAgainst] = useState(summary.against || 0);
  const [votesAbstain, setVotesAbstain] = useState(summary.abstain || 0);
  const [votesResult, setVotesResult] = useState(summary.result || "");

  useEffect(() => {
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
  }, []);

  return (
    <div className="h-full flex flex-col items-center justify-center">
      <div id="container" style={{ width: "100%", height: "50%" }}></div>
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

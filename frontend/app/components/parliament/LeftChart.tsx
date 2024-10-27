import React, { useEffect } from "react";
import Highcharts from "highcharts";
import HighchartsItem from "highcharts/modules/item-series";

// Initialize the item module
HighchartsItem(Highcharts);
const LeftChart = () => {
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
              "#CC0099",
              "Corporations",
            ],
            [
              "Government (Seek a balance between innovation and public safety)",
              45,
              "#EE0011",
              "Government",
            ],
            [
              "Academics (Focus on long-term risks, ethical implications, and AI safety)",
              45,
              "#448833",
              "Academics",
            ],
            [
              "Civil Rights Advocates (Champion fairness, transparency, and social impact)",
              45,
              "#FFA500",
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
    <div className="h-full">
      <div id="container" style={{ width: "100%", height: "50%" }}></div>
    </div>
  );
};

export default LeftChart;

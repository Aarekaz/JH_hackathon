import React, { useEffect, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBuilding,
  faGavel,
  faUniversity,
  faUsers,
} from "@fortawesome/free-solid-svg-icons";

const RightChat = ({ paperid }) => {
  const [messages, setMessages] = useState([]);
  const [displayedMessages, setDisplayedMessages] = useState([]);
  const [debateMessages, setDebateMessages] = useState([]);

  // useEffect(() => {
  //   if (paperid) {
  //     // Fetch debate messages based on paperid
  //     fetch(`/api/debate/${paperid}`)
  //       .then((response) => response.json())
  //       .then((response) => {
  //         setDebateMessages(response.data);
  //       });
  //   }
  // }, [paperid]);

  useEffect(() => {
    const initialMessages = [
      {
        id: 1,
        representative: "Corporations",
        message: "We need to prioritize innovation and minimal regulations",
        color: "#DA0211",
      },
      {
        id: 2,
        representative: "Government",
        message:
          "We need to seek a balance between innovation and public safety",
        color: "#2CAFFE",
      },
      {
        id: 3,
        representative: "Academics",
        message:
          "We need to focus on long-term risks, ethical implications, and AI safety",
        color: "#FDA003",
      },
      {
        id: 4,
        representative: "Civil Rights Advocates",
        message:
          "We need to champion fairness, transparency, and social impact",
        color: "#000099",
      },
      {
        id: 5,
        representative: "Academics",
        message: "We need to ensure that AI benefits all of society",
        color: "#FDA003",
      },
    ];
    setMessages(initialMessages);
  }, []);

  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      if (index < messages.length) {
        setDisplayedMessages((prev) => [...prev, messages[index]]);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [messages]);

  const handleVote = () => {
    console.log("Voting...");
  };

  const getIcon = (representative) => {
    switch (representative) {
      case "Corporations":
        return faBuilding;
      case "Government":
        return faGavel;
      case "Academics":
        return faUniversity;
      case "Civil Rights Advocates":
        return faUsers;
      default:
        return faUsers;
    }
  };

  console.log("displayMessages", displayedMessages);

  return (
    <div className="flex flex-col h-full p-4 border-l border-gray-300 bg-gray-400">
      <div className="flex-1 overflow-y-auto mb-4">
        {displayedMessages?.map((item, index) => (
          <div
            key={index}
            className={`flex items-end mb-4 ${
              index % 2 === 0 ? "justify-start" : "justify-end"
            }`}
          >
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <FontAwesomeIcon
                  icon={getIcon(item.representative)}
                  className="text-blue-500"
                />
              </div>
            </div>
            <div
              className={`ml-2 p-4 rounded-lg text-white`}
              style={{ backgroundColor: item.color }}
            >
              <div>{item.message}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="flex w-full p-4">
        <button
          onClick={handleVote}
          className="w-full p-2 bg-purple-600 text-white rounded"
        >
          It's time to VOTE!
        </button>
      </div>
    </div>
  );
};

export default RightChat;

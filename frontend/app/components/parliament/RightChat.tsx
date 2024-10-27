import React, { useEffect, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBuilding,
  faGavel,
  faUniversity,
  faUsers,
} from "@fortawesome/free-solid-svg-icons";
import axios from "axios";

const RightChat = () => {
  const [messages, setMessages] = useState([]);
  const paper_id = localStorage.getItem("paperid");
  const [displayedMessages, setDisplayedMessages] = useState([]);
  const [isButtonDisabled, setIsButtonDisabled] = useState(true);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const response = await axios.post(
          `
http://localhost:8000/debates/${paper_id}/start-full-debate`
        );
        setMessages(response.data);
        const debate_id = response.data.debate_id;
        localStorage.setItem("debate_id", debate_id);
      } catch (error) {
        console.error("Error fetching messages:", error);
      }
    };

    fetchMessages();
  }, [paper_id]);

  useEffect(() => {
    if (messages.length === 0) return;

    let index = 0;
    const interval = setInterval(() => {
      if (index < messages.length) {
        setDisplayedMessages((prev) => [...prev, messages[index]]);
        index++;
      } else {
        clearInterval(interval);
        setIsButtonDisabled(false); // Enable the button after all messages are displayed
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [messages]);

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
          disabled={isButtonDisabled}
          className="w-full p-2 bg-purple-600 text-white rounded"
        >
          It's time to VOTE!
        </button>
      </div>
    </div>
  );
};

export default RightChat;

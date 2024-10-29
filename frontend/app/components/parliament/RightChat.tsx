import React, { useEffect, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBuilding,
  faGavel,
  faUniversity,
  faUsers,
} from "@fortawesome/free-solid-svg-icons";
import axios from "axios";
import { TrophySpin } from "react-loading-indicators";

const RightChat = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const paper_id = localStorage.getItem("paperid");

  useEffect(() => {
    const fetchMessages = async () => {
      await axios
        .post(`http://localhost:8000/debates/${paper_id}/start-full-debate`)
        .then((response) => {
          console.log(response.data);
          setMessages(response.data.responses);
          const summary = response.data.summary;
          localStorage.setItem("summary", JSON.stringify(summary));
          setLoading(false);
        })
        .catch((error) => {
          console.error("Error fetching messages:", error);
          setLoading(false); // Set loading to false even if there's an error
        });
    };

    fetchMessages();
  }, [paper_id]);

  const getIcon = (representative) => {
    switch (representative) {
      case "corporate":
        return faBuilding;
      case "government":
        return faGavel;
      case "academic":
        return faUniversity;
      case "civil_rights":
        return faUsers;
      default:
        return faUsers;
    }
  };

  const handleVoteClick = () => {
    console.log("Voting...");
  };

  if (loading) {
    return <TrophySpin color="#32cd32" size="medium" text="" textColor="" />;
  }

  return (
    <div className="flex flex-col h-full p-4 border-l border-gray-300 bg-gray-400">
      <div className="flex-1 overflow-y-auto mb-4">
        {messages?.map((item, index) => (
          <div
            key={index}
            className={`flex items-end mb-4 ${
              index % 2 === 0 ? "justify-start" : "justify-end"
            }`}
          >
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <FontAwesomeIcon
                  icon={getIcon(item.mp_role)}
                  className="text-blue-500"
                />
              </div>
            </div>
            <div
              className={`ml-2 p-4 rounded-lg text-white`}
              style={{ backgroundColor: item.color }}
            >
              <div>{item.content}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="flex w-full p-4">
        <button
          className="w-full p-2 bg-purple-600 text-white rounded"
          onClick={handleVoteClick}
        >
          It's time to VOTE!
        </button>
      </div>
    </div>
  );
};

export default RightChat;

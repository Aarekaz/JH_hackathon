import React, { useState, useEffect } from "react";
import axios from "axios";
const RightChat = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState<string>("");
  const paperid = localStorage.getItem("paperid");
  const [debateMessages, setDebateMessages] = useState<any>();

  const handleSendMessage = () => {
    if (input.trim()) {
      setMessages([...messages, input]);
      setInput("");
    }
  };

  useEffect(() => {
    if (paperid) {
      axios
        .post(`http://localhost:8000/papers/${paperid}/debate`)
        .then((response) => {
          setDebateMessages(response.data);
        });
    }
  }, [paperid]);
  console.log("debate info", debateMessages);

  return (
    <div className="flex flex-col h-full p-4 border-l border-gray-300">
      <div className="flex-1 overflow-y-auto mb-4">
        {messages.map((message, index) => (
          <div key={index} className="mb-2 p-2 bg-gray-200 rounded">
            {message}
          </div>
        ))}
      </div>
      <div className="flex">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 p-2 border border-gray-300 rounded-l"
          placeholder="Type a message..."
        />
        <button
          onClick={handleSendMessage}
          className="p-2 bg-blue-500 text-white rounded-r"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default RightChat;

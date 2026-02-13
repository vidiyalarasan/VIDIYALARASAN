import { useState, useEffect, useRef } from "react";
import axios from "axios";
import MessageBubble from "./MessageBubble";

export default function ChatPanel({ chat, updateMessages }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat.messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [
      ...chat.messages,
      { role: "user", content: input },
    ];

    updateMessages(chat.id, newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/ask", {
        messages: newMessages,
      });

      updateMessages(chat.id, [
        ...newMessages,
        { role: "assistant", content: res.data.answer },
      ]);
    } catch {
      updateMessages(chat.id, [
        ...newMessages,
        {
          role: "assistant",
          content: "⚠️ Something went wrong.",
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        background: "#0b1120",
      }}
    >
      <div style={{ flex: 1, padding: "20px", overflowY: "auto" }}>
        {chat.messages.map((msg, index) => (
          <MessageBubble key={index} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div
        style={{
          display: "flex",
          padding: "16px",
          borderTop: "1px solid #1e293b",
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          style={{
            flex: 1,
            padding: "10px",
            borderRadius: "8px",
            border: "none",
            background: "#1e293b",
            color: "white",
          }}
        />
        <button
          onClick={sendMessage}
          style={{
            marginLeft: "10px",
            padding: "10px 16px",
            background: "#2563eb",
            border: "none",
            borderRadius: "8px",
            color: "white",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

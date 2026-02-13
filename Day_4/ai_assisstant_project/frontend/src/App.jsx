import { useState, useEffect } from "react";
import ChatPanel from "./components/ChatPanel";
import Sidebar from "./components/Sidebar";

export default function App() {
  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem("chat_sessions");
    return saved ? JSON.parse(saved) : [];
  });

  const [activeId, setActiveId] = useState(null);

  useEffect(() => {
    localStorage.setItem("chat_sessions", JSON.stringify(sessions));
  }, [sessions]);

  const createNewChat = () => {
    const newChat = {
      id: Date.now().toString(),
      title: "New Chat",
      messages: [
        {
          role: "assistant",
          content: "Hello 👋 How can I assist you today?",
        },
      ],
    };

    setSessions([newChat, ...sessions]);
    setActiveId(newChat.id);
  };

  const updateMessages = (id, messages) => {
    setSessions((prev) =>
      prev.map((chat) =>
        chat.id === id ? { ...chat, messages } : chat
      )
    );
  };

  const activeChat = sessions.find((s) => s.id === activeId);

  return (
<div
  style={{
    display: "flex",
    height: "100vh",
    backdropFilter: "blur(6px)",
  }}
>
      <Sidebar
        sessions={sessions}
        activeId={activeId}
        setActiveId={setActiveId}
        createNewChat={createNewChat}
      />

      {activeChat && (
        <ChatPanel
          chat={activeChat}
          updateMessages={updateMessages}
        />
      )}
    </div>
  );
}

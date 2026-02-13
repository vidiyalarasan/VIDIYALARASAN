export default function Sidebar({
  sessions,
  activeId,
  setActiveId,
  createNewChat,
}) {
  return (
    <div
      style={{
        width: "260px",
        background: "#0f172a",
        color: "white",
        padding: "16px",
        borderRight: "1px solid #1e293b",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <button
        onClick={createNewChat}
        style={{
          marginBottom: "20px",
          padding: "10px",
          background: "#2563eb",
          border: "none",
          borderRadius: "8px",
          color: "white",
          cursor: "pointer",
        }}
      >
        + New Chat
      </button>

      <div style={{ flex: 1, overflowY: "auto" }}>
        {sessions.map((chat) => (
          <div
            key={chat.id}
            onClick={() => setActiveId(chat.id)}
            style={{
              padding: "10px",
              marginBottom: "8px",
              borderRadius: "8px",
              cursor: "pointer",
              background:
                chat.id === activeId
                  ? "#1e293b"
                  : "transparent",
            }}
          >
            {chat.title}
          </div>
        ))}
      </div>
    </div>
  );
}

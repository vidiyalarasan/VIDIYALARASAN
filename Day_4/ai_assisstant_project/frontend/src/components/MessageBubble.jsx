import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function MessageBubble({ message }) {
  if (!message) return null;

  const isUser = message.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "12px",
      }}
    >
      <div
        style={{
          maxWidth: "75%",
          padding: "14px 18px",
          borderRadius: "14px",
          background: isUser ? "#2563eb" : "#1f2937",
          color: "white",
        }}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({ inline, children }) {
              if (inline) {
                return (
                  <code
                    style={{
                      background: "#0f172a",
                      padding: "3px 6px",
                      borderRadius: "6px",
                      color: "#38bdf8",
                    }}
                  >
                    {children}
                  </code>
                );
              }

              return (
                <pre
                  style={{
                    background: "#0b1120",
                    padding: "16px",
                    borderRadius: "12px",
                    overflowX: "auto",
                    border: "1px solid #1e293b",
                    marginTop: "10px",
                  }}
                >
                  <code style={{ color: "#22d3ee" }}>
                    {children}
                  </code>
                </pre>
              );
            },
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>
    </div>
  );
}

export default MessageBubble;

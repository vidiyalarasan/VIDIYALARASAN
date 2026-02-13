export default function Hero({ onLaunch }) {
  return (
    <div className="hero">
      <h1>Elite AI Assistant</h1>
      <p>Modern AI built with React + FastAPI + Groq</p>
      <button onClick={onLaunch}>
        Launch Assistant
      </button>
    </div>
  );
}

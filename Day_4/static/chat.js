async function sendMessage() {
    const input = document.getElementById("question");
    const message = input.value.trim();
    if (!message) return;

    const chat = document.getElementById("chat");

    chat.innerHTML += `<div class="message user">${message}</div>`;
    input.value = "";
    chat.scrollTop = chat.scrollHeight;

    const typing = document.createElement("div");
    typing.className = "message bot";
    typing.innerText = "Thinking...";
    chat.appendChild(typing);

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({question: message})
        });

        const data = await response.json();
        typing.remove();

        const botMessage = document.createElement("div");
        botMessage.className = "message bot";
        botMessage.innerHTML = marked.parse(data.answer);

        chat.appendChild(botMessage);

        document.querySelectorAll("pre code").forEach((block) => {
            hljs.highlightElement(block);
        });

        chat.scrollTop = chat.scrollHeight;

    } catch {
        typing.remove();
        chat.innerHTML += `<div class="message bot">⚠️ Server Error</div>`;
    }
}

function handleKey(e) {
    if (e.key === "Enter") sendMessage();
}

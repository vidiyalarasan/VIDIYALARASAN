from flask import Flask, request, jsonify, render_template_string
import requests
import os

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
app = Flask(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# 🔥 STEP 1: Load Documents Automatically
def load_documents():
    documents = []

    if not os.path.exists("documents"):
        print("❌ documents folder not found.")
        return []

    for file in os.listdir("documents"):
        path = os.path.join("documents", file)

        if file.endswith(".pdf"):
            loader = PyPDFLoader(path)
            documents.extend(loader.load())

        elif file.endswith(".txt"):
            loader = TextLoader(path)
            documents.extend(loader.load())

    return documents


# 🔥 STEP 2: Build Vectorstore (Auto)
def build_vectorstore():
    documents = load_documents()

    if not documents:
        print("❌ No documents found.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    splits = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(splits, embeddings)
    print("✅ Vectorstore created successfully!")
    return vectorstore


# 🔥 Create vectorstore when app starts
vectorstore = build_vectorstore()

# 🔒 Coding-only filter
CODING_KEYWORDS = [
    "python", "java", "c", "c++", "javascript", "html", "css",
    "sql", "mysql", "postgresql", "mongodb", "flask", "spring",
    "react", "node", "api", "backend", "frontend",
    "function", "class", "object", "loop", "array", "string",
    "database", "query", "algorithm", "data structure",
    "error", "exception", "bug", "debug", "compile",
    "code", "program", "build", "develop", "implement"
]

def is_allowed(message: str) -> bool:
    msg = message.lower()
    return any(word in msg for word in CODING_KEYWORDS)


@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Coding RAG Assistant</title>
        <style>
            body { font-family: Arial; background:#111; color:white; }
            .chat-box { width:700px; margin:40px auto; }
            .messages { height:450px; overflow-y:auto; border:1px solid #444; padding:10px; }
            input { width:80%; padding:10px; }
            button { padding:10px; }
        </style>
    </head>
    <body>
    <div class="chat-box">
        <h2>💻 Coding RAG Assistant</h2>
        <div class="messages" id="messages"></div>
        <br>
        <input type="text" id="message" placeholder="Ask coding question...">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
    function sendMessage() {
        const msgInput = document.getElementById("message");
        const msg = msgInput.value;
        const messagesDiv = document.getElementById("messages");

        messagesDiv.innerHTML += `<p><b>You:</b> ${msg}</p>`;

        fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: msg})
        })
        .then(res => res.json())
        .then(data => {
            messagesDiv.innerHTML += `<p><b>Bot:</b> ${data.reply}</p>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        });

        msgInput.value = "";
    }
    </script>
    </body>
    </html>
    """)


@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")

    if not is_allowed(user_msg):
        return jsonify({
            "reply": "❌ This assistant only supports coding-related questions."
        })

    if vectorstore is None:
        return jsonify({
            "reply": "⚠️ No documents loaded. Please add documents inside 'documents' folder."
        })

    # 🔍 RAG retrieval
    docs = vectorstore.similarity_search(user_msg, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert coding assistant. Use ONLY the provided context to answer. If not in context, say you don't know."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{user_msg}"
            }
        ]
    }

    try:
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
        print("Status:", r.status_code)
        print("Response:", r.text)
        r.raise_for_status()

        data = r.json()
        reply = data["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"⚠️ Error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True, port=5002)

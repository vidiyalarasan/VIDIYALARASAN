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
PYTHON_KEYWORDS = [
    "python", "py", "flask", "django",
    "loop", "for", "while",
    "function", "def",
    "class", "object",
    "list", "dict", "tuple", "set",
    "string", "int", "float",
    "exception", "error", "debug",
    "pandas", "numpy",
    "import", "module",
    "decorator", "lambda",
    "async", "await",
    "algorithm", "data structure"
]


def is_allowed(message: str) -> bool:
    msg = message.lower()

    # Must mention python explicitly OR contain strong python patterns
    if "python" in msg:
        return True

    return any(word in msg for word in PYTHON_KEYWORDS)

@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Python RAG Assistant</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<!-- Markdown -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

<!-- Syntax Highlight -->
<link rel="stylesheet"
href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

<styles>
:root{
    --bg1:#0f172a;
    --bg2:#1e293b;
    --glass:rgba(255,255,255,0.06);
    --border:rgba(255,255,255,0.08);
    --text:#f8fafc;
    --muted:#94a3b8;
    --accent:#3b82f6;
}

body{
    margin:0;
    font-family:'Inter',sans-serif;
    background:linear-gradient(135deg,var(--bg1),var(--bg2));
    height:100vh;
    display:flex;
    color:var(--text);
}

/* Sidebar */
.sidebar{
    width:240px;
    background:rgba(0,0,0,0.4);
    border-right:1px solid var(--border);
    padding:25px;
}

.sidebar h2{
    font-size:18px;
    margin-bottom:20px;
}

.status{
    font-size:13px;
    color:var(--muted);
}

/* Chat Container */
.chat{
    flex:1;
    display:flex;
    flex-direction:column;
}

/* Header */
.header{
    padding:20px;
    border-bottom:1px solid var(--border);
    font-weight:600;
    font-size:18px;
}

/* Messages */
.messages{
    flex:1;
    padding:30px;
    overflow-y:auto;
    display:flex;
    flex-direction:column;
    gap:20px;
}

.message{
    max-width:75%;
    padding:16px;
    border-radius:18px;
    line-height:1.6;
    animation:fadeIn 0.2s ease;
}

.user{
    align-self:flex-end;
    background:var(--accent);
}

.bot{
    align-self:flex-start;
    background:var(--glass);
    border:1px solid var(--border);
}

/* Code Blocks */
pre{
    background:#0f172a;
    padding:14px;
    border-radius:12px;
    overflow-x:auto;
}

code{
    font-family:monospace;
}

/* Input */
.input-area{
    padding:20px;
    border-top:1px solid var(--border);
    display:flex;
    gap:10px;
    background:rgba(0,0,0,0.4);
}

input{
    flex:1;
    padding:14px;
    border-radius:14px;
    border:none;
    background:rgba(255,255,255,0.05);
    color:white;
    font-size:15px;
    outline:none;
}

button{
    padding:14px 22px;
    border-radius:14px;
    border:none;
    background:var(--accent);
    color:white;
    font-weight:600;
    cursor:pointer;
    transition:0.2s;
}

button:hover{
    transform:scale(1.05);
}

/* Typing Animation */
.typing::after{
    content:"...";
    animation:dots 1.5s infinite;
}

@keyframes dots{
    0%{content:".";}
    33%{content:"..";}
    66%{content:"...";}
}

@keyframes fadeIn{
    from{opacity:0;transform:translateY(5px);}
    to{opacity:1;transform:translateY(0);}
}
</styles>
</head>

<body>

<div class="sidebar">
    <h2>🐍 Python RAG</h2>
    <div class="status">
        Python-only mode 🔒<br>
        Documents loaded ✔️
    </div>
</div>

<div class="chat">
    <div class="header">Python Documentation Assistant</div>

    <div class="messages" id="messages"></div>

    <div class="input-area">
        <input type="text" id="message"
        placeholder="Ask about Python..."
        onkeydown="handleKey(event)">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>

<script>

function handleKey(e){
    if(e.key==="Enter"){
        sendMessage();
    }
}

function addMessage(text,type){
    const div=document.createElement("div");
    div.classList.add("message",type);
    div.innerHTML=marked.parse(text);
    document.getElementById("messages").appendChild(div);

    document.querySelectorAll("pre code").forEach((block)=>{
        hljs.highlightElement(block);
    });

    document.getElementById("messages").scrollTop=
        document.getElementById("messages").scrollHeight;
}

function sendMessage(){
    const input=document.getElementById("message");
    const msg=input.value.trim();
    if(!msg) return;

    addMessage(msg,"user");
    input.value="";

    const typing=document.createElement("div");
    typing.classList.add("message","bot","typing");
    typing.id="typing";
    typing.innerHTML="Thinking";
    document.getElementById("messages").appendChild(typing);

    fetch("/chat",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({message:msg})
    })
    .then(res=>res.json())
    .then(data=>{
        document.getElementById("typing").remove();
        addMessage(data.reply,"bot");
    })
    .catch(()=>{
        document.getElementById("typing").remove();
        addMessage("⚠️ Server error.","bot");
    });
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
            "reply": "❌ This assistant only supports PYTHON-related questions."
        })

    if vectorstore is None:
        return jsonify({
            "reply": "⚠️ No documents loaded. Please add documents inside 'documents' folder."
        })

    # 🔍 RAG retrieval
    docs = vectorstore.similarity_search(
        f"Python topic: {user_msg}", k=3
    )
    context = "\n\n".join([doc.page_content for doc in docs])

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert Python assistant. Answer ONLY Python-related questions using the provided context. If the question is not about Python, refuse politely."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{user_msg}"
            }
        ]
    }

    try:
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        reply = data["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"⚠️ Error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True, port=5002)

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from agent import query_llm
from tools import execute_tool

app = FastAPI()
ACCESS_TOKEN = os.getenv("PC_AGENT_TOKEN", "shashank123")
history = []

HTML = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PC Agent</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: #0f0f0f; color: #f0f0f0; height: 100dvh; display: flex; flex-direction: column; }
  #header { background: #1a1a1a; padding: 14px 16px; border-bottom: 1px solid #333; display: flex; align-items: center; gap: 10px; }
  #header .dot { width: 10px; height: 10px; border-radius: 50%; background: #4ade80; }
  #header h1 { font-size: 16px; font-weight: 600; }
  #header small { color: #888; font-size: 12px; margin-left: auto; }
  #messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
  .msg { max-width: 85%; padding: 10px 14px; border-radius: 16px; font-size: 14px; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
  .user { align-self: flex-end; background: #2563eb; border-bottom-right-radius: 4px; }
  .bot { align-self: flex-start; background: #1e1e1e; border: 1px solid #333; border-bottom-left-radius: 4px; }
  .bot .tool-tag { font-size: 11px; color: #888; margin-bottom: 4px; }
  .thinking { color: #888; font-style: italic; }
  #bottom { padding: 12px; background: #1a1a1a; border-top: 1px solid #333; display: flex; gap: 8px; }
  #input { flex: 1; background: #2a2a2a; border: 1px solid #444; color: #f0f0f0; border-radius: 24px; padding: 10px 16px; font-size: 15px; outline: none; }
  #input:focus { border-color: #2563eb; }
  #send { background: #2563eb; border: none; color: white; width: 42px; height: 42px; border-radius: 50%; cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  #send:active { background: #1d4ed8; }
  #token-screen { position: fixed; inset: 0; background: #0f0f0f; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; padding: 24px; }
  #token-screen h2 { font-size: 20px; }
  #token-screen p { color: #888; font-size: 14px; text-align: center; }
  #token-input { width: 100%; max-width: 300px; background: #1e1e1e; border: 1px solid #444; color: white; padding: 12px 16px; border-radius: 12px; font-size: 16px; text-align: center; outline: none; }
  #token-btn { background: #2563eb; color: white; border: none; padding: 12px 32px; border-radius: 12px; font-size: 16px; cursor: pointer; }
  #suggestions { display: flex; gap: 8px; overflow-x: auto; padding: 0 12px 8px; scrollbar-width: none; }
  #suggestions::-webkit-scrollbar { display: none; }
  .chip { background: #1e1e1e; border: 1px solid #333; color: #ccc; padding: 6px 12px; border-radius: 20px; font-size: 12px; white-space: nowrap; cursor: pointer; flex-shrink: 0; }
  .chip:active { background: #2a2a2a; }
</style>
</head>
<body>

<div id="token-screen">
  <h2>🖥️ PC Agent</h2>
  <p>Enter your access token to connect</p>
  <input id="token-input" type="password" placeholder="Access token" />
  <button id="token-btn" onclick="saveToken()">Connect</button>
</div>

<div id="header" style="display:none">
  <div class="dot"></div>
  <h1>PC Agent</h1>
  <small id="model-label">phi3:mini</small>
</div>

<div id="messages" style="display:none"></div>

<div id="suggestions" style="display:none">
  <div class="chip" onclick="useChip(this)">Show Desktop files</div>
  <div class="chip" onclick="useChip(this)">System info</div>
  <div class="chip" onclick="useChip(this)">Open Chrome</div>
  <div class="chip" onclick="useChip(this)">List Downloads</div>
  <div class="chip" onclick="useChip(this)">Open Notepad</div>
</div>

<div id="bottom" style="display:none">
  <input id="input" type="text" placeholder="Type a command..." autocomplete="off" />
  <button id="send" onclick="send()">↑</button>
</div>

<script>
let token = localStorage.getItem("pc_agent_token") || "";
if (token) showMain();

function saveToken() {
  token = document.getElementById("token-input").value.trim();
  if (!token) return;
  localStorage.setItem("pc_agent_token", token);
  showMain();
}

function showMain() {
  document.getElementById("token-screen").style.display = "none";
  document.getElementById("header").style.display = "flex";
  document.getElementById("messages").style.display = "flex";
  document.getElementById("suggestions").style.display = "flex";
  document.getElementById("bottom").style.display = "flex";
  document.getElementById("input").focus();
  addMessage("bot", "Connected to your PC. What do you want to do?", "");
}

document.getElementById("input").addEventListener("keydown", e => {
  if (e.key === "Enter") send();
});

document.getElementById("token-input").addEventListener("keydown", e => {
  if (e.key === "Enter") saveToken();
});

function useChip(el) {
  document.getElementById("input").value = el.textContent;
  send();
}

function addMessage(role, text, tool) {
  const msgs = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = "msg " + role;
  if (role === "bot" && tool && tool !== "chat") {
    div.innerHTML = `<div class="tool-tag">🔧 ${tool}</div>${escapeHtml(text)}`;
  } else {
    div.textContent = text;
  }
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}

function escapeHtml(t) {
  return t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

async function send() {
  const input = document.getElementById("input");
  const msg = input.value.trim();
  if (!msg) return;
  input.value = "";

  addMessage("user", msg, "");
  const thinking = addMessage("bot", "Thinking...", "");
  thinking.classList.add("thinking");

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: msg, token: token})
    });

    if (res.status === 401) {
      thinking.textContent = "Invalid token. Please reload and try again.";
      localStorage.removeItem("pc_agent_token");
      return;
    }

    const data = await res.json();
    thinking.remove();
    addMessage("bot", data.response, data.tool);
  } catch(e) {
    thinking.textContent = "Connection error. Is the server running?";
  }
}
</script>
</body>
</html>"""


class Message(BaseModel):
    message: str
    token: str


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.post("/chat")
async def chat(msg: Message):
    if msg.token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    history.append({"role": "user", "content": msg.message})

    try:
        result = query_llm(msg.message, history)
        tool = result.get("tool", "chat")
        args = result.get("args", {})
        action_msg = result.get("message", "")

        output = execute_tool(tool, args)

        if action_msg and action_msg != output:
            response = f"{action_msg}\n\n{output}".strip()
        else:
            response = output

        history.append({"role": "assistant", "content": response})
        return {"response": response, "tool": tool}

    except Exception as e:
        return {"response": f"Error: {e}", "tool": "error"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    print("\n🖥️  PC Agent starting...")
    print(f"   Local:   http://localhost:8080")
    print(f"   Network: http://0.0.0.0:8080")
    print(f"   Token:   {ACCESS_TOKEN}")
    print("\n   For remote access run: ngrok http 8080\n")
    uvicorn.run(app, host="0.0.0.0", port=8080)

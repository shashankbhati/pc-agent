import json
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"

SYSTEM_PROMPT = """PC control agent. Respond ONLY with JSON, no other text.
Format: {"tool":"tool_name","args":{},"message":"short description"}

Tools:
- run_command: {"cmd":"shell command"}
- list_files: {"path":"C:/path"} (default: C:/Users/ShashankBhati)
- read_file: {"path":"C:/path/file"}
- create_folder: {"path":"C:/path/folder"}
- delete_file: {"path":"C:/path"}
- move_file: {"src":"C:/src","dst":"C:/dst"}
- open_app: {"name":"chrome|notepad|explorer|calculator|vscode|cmd|powershell"}
- system_info: {}
- chat: {"response":"your reply"}

Use absolute Windows paths. Never delete C:/Windows or Program Files."""


def query_llm(user_message: str, history: list) -> dict:
    context = ""
    for h in history[-8:]:
        context += f"{h['role']}: {h['content']}\n"

    prompt = f"{context}user: {user_message}\nassistant:"

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 150}
        }, timeout=120)

        text = response.json().get("response", "").strip()

        # Extract JSON from response
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())

        return {"tool": "chat", "args": {"response": text}, "message": ""}

    except requests.exceptions.ConnectionError:
        return {"tool": "chat", "args": {"response": "Ollama is not running. Start it with: ollama serve"}, "message": ""}
    except json.JSONDecodeError:
        return {"tool": "chat", "args": {"response": "Could not parse LLM response. Try again."}, "message": ""}
    except Exception as e:
        return {"tool": "chat", "args": {"response": f"LLM error: {e}"}, "message": ""}

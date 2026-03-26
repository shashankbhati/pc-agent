import os
import shutil
import subprocess
import psutil

HOME = "C:/Users/ShashankBhati"
PROTECTED = ["C:/Windows", "C:/Program Files", "C:/Program Files (x86)", f"{HOME}/AppData"]
DANGEROUS_CMDS = ["format", "rd /s", "rmdir /s /q", "del /f /s /q", "rm -rf", "mkfs", "dd if="]

APPS = {
    "chrome": "start chrome",
    "firefox": "start firefox",
    "notepad": "start notepad",
    "explorer": "start explorer",
    "calculator": "start calc",
    "vscode": "code",
    "vs code": "code",
    "cmd": "start cmd",
    "powershell": "start powershell",
    "task manager": "taskmgr",
    "edge": "start msedge",
}

SITES = {
    "linkedin": "https://www.linkedin.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "github": "https://www.github.com",
    "google": "https://www.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "twitter": "https://www.twitter.com",
    "instagram": "https://www.instagram.com",
    "chatgpt": "https://chat.openai.com",
    "netflix": "https://www.netflix.com",
}


def run_command(cmd: str) -> str:
    if any(d in cmd.lower() for d in DANGEROUS_CMDS):
        return "Blocked: dangerous command detected."
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        out = result.stdout.strip() or result.stderr.strip()
        return out or "Command executed with no output."
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds."
    except Exception as e:
        return f"Error: {e}"


def list_files(path: str = HOME) -> str:
    try:
        entries = os.listdir(path)
        if not entries:
            return "Empty folder."
        lines = []
        for e in sorted(entries):
            full = os.path.join(path, e)
            icon = "📁" if os.path.isdir(full) else "📄"
            size = ""
            if os.path.isfile(full):
                s = os.path.getsize(full)
                size = f" ({s // 1024} KB)" if s > 1024 else f" ({s} B)"
            lines.append(f"{icon} {e}{size}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(4000)
        return content if content else "(empty file)"
    except Exception as e:
        return f"Error: {e}"


def create_folder(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
        return f"Created: {path}"
    except Exception as e:
        return f"Error: {e}"


def delete_file(path: str) -> str:
    if any(path.startswith(p) for p in PROTECTED):
        return "Blocked: cannot delete protected system path."
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return f"Deleted: {path}"
    except Exception as e:
        return f"Error: {e}"


def move_file(src: str, dst: str) -> str:
    try:
        shutil.move(src, dst)
        return f"Moved: {src} → {dst}"
    except Exception as e:
        return f"Error: {e}"


def open_app(name: str, browser: str = "edge") -> str:
    name_lower = name.lower()

    # Check if it's a known website
    url = SITES.get(name_lower)
    if not url and name_lower.startswith("http"):
        url = name_lower

    if url:
        browser_cmd = {
            "edge": "start msedge",
            "chrome": "start chrome",
            "firefox": "start firefox",
        }.get(browser.lower(), "start msedge")
        try:
            subprocess.Popen(f'{browser_cmd} "{url}"', shell=True)
            return f"Opened {name} in {browser}"
        except Exception as e:
            return f"Error: {e}"

    # Otherwise open as app
    cmd = APPS.get(name_lower, f"start {name}")
    try:
        subprocess.Popen(cmd, shell=True)
        return f"Opened: {name}"
    except Exception as e:
        return f"Error: {e}"


def system_info() -> str:
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("C:/")
        return (
            f"CPU: {cpu}%\n"
            f"RAM: {ram.used // (1024**3)}GB / {ram.total // (1024**3)}GB ({ram.percent}%)\n"
            f"Disk C: {disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB ({disk.percent}%)"
        )
    except Exception as e:
        return f"Error: {e}"


def execute_tool(tool: str, args: dict) -> str:
    if tool == "run_command":
        return run_command(args.get("cmd", ""))
    elif tool == "list_files":
        return list_files(args.get("path", HOME))
    elif tool == "read_file":
        return read_file(args.get("path", ""))
    elif tool == "create_folder":
        return create_folder(args.get("path", ""))
    elif tool == "delete_file":
        return delete_file(args.get("path", ""))
    elif tool == "move_file":
        return move_file(args.get("src", ""), args.get("dst", ""))
    elif tool == "open_app":
        return open_app(args.get("name", ""), args.get("browser", "edge"))
    elif tool == "system_info":
        return system_info()
    elif tool == "chat":
        return args.get("response", "")
    return f"Unknown tool: {tool}"

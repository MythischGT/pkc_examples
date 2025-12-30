import subprocess
import sys
import time
import os
import platform

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PYTHON = sys.executable
SYSTEM = platform.system()

def spawn_terminal(title, script_path):
    if SYSTEM == "Linux":
        subprocess.Popen([
            "x-terminal-emulator",
            "-T", title,
            "-e", PYTHON, script_path
        ])

    elif SYSTEM == "Darwin":  # macOS
        subprocess.Popen([
            "osascript",
            "-e",
            f'''
            tell application "Terminal"
                do script "{PYTHON} {script_path}"
                set custom title of front window to "{title}"
            end tell
            '''
        ])

    elif SYSTEM == "Windows":
        subprocess.Popen([
            "powershell",
            "-NoExit",
            "-Command",
            (
                f"Start-Process powershell "
                f"-ArgumentList '-NoExit', "
                f"'-Command', "
                f"\"$Host.UI.RawUI.WindowTitle='{title}'; "
                f"cd '{BASE_DIR}'; "
                f"& '{PYTHON}' -m 'participants.{script_path}'\""
            )
        ])

    else:
        raise RuntimeError("Unsupported OS")

def main():
    print("[*] Starting Obo...")
    spawn_terminal("Obo", "obo")
    time.sleep(1.5)

    print("[*] Starting Korno...")
    spawn_terminal("Korno", "korno")
    time.sleep(1.5)

    print("[*] Starting Jacob...")
    spawn_terminal("Jacob", "jacob")
    print("[*] All parties launched.")

if __name__ == "__main__":
    main()

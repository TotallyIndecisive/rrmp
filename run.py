import threading
import time
import urllib.request
import subprocess
import uvicorn
import webview


def wait_for_server(url: str, timeout: int = 30) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def start_server():
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)


def open_browser(url: str):
    subprocess.Popen(["firefox", url])


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("Starting server...")
    if wait_for_server("http://127.0.0.1:8000/health"):
        print("Server ready! Opening browser...")
        webview.create_window(
            title="RetroReel MP",
            url="http://127.0.0.1:8000",
            width=1280,
            height=800,
            min_size=(900, 600),
        )
        try:
            webview.start(func=open_browser)
        except Exception:
            print("pywebview not available, opening with system browser...")
            open_browser("http://127.0.0.1:8000")
    else:
        print("Server failed to start within timeout")

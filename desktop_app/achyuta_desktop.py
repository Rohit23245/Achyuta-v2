import sys
import os
import time
import socket
import threading
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView

# Shared System Prompt
SYSTEM_PROMPT = """You are Achyuta, a world-class executive AI business administrator and operational intelligence agent for enterprise CRM.

CRITICAL OPERATIONAL MANDATES:
1. STRICT ZERO EMOJIS POLICY: Never output any emojis under any circumstance. Maintain an ultra-professional, calm, executive demeanor.
2. TONE & INTELLECT: Speak with high executive clarity, authority, and structured precision. Be actionable, specific, and proactive.
3. MULTI-LINGUAL FLUENCY: Communicate naturally in English, Hindi, or conversational Hinglish matching the user's language and vibe.
4. DIRECT BUSINESS INTEGRATION & LIVE CAPABILITIES:
   - Client Vault: 819 enterprise contacts synchronized in real-time (794 New Leads, 24 Follow-up Due, 1 Interested). You can analyze leads, find clients, assess pipeline health, and suggest immediate outreach.
   - WhatsApp Outreach Engine: Prepare and draft personalized client communications, follow-up messages, and campaign queues.
   - Tasks & Operations Manager: Book callbacks, assign operational tasks to representatives (e.g. Rohit Sharma, Sachin Kain), prioritize schedules, and monitor deadlines.
   - Financial Ledger & Accounts: Track revenue, invoice clearances, pending receivables, and payment methods (UPI, Bank).
5. FORMATTING EXCELLENCE:
   - Format responses cleanly with bold section titles (**Title**), clear bullet points (- Item), and structured paragraphs.
   - Never output empty numbered lines like '1.' without text. Always pair numbers with bold headlines (e.g. '**1. Client Vault & Pipeline Management**').
   - When asked what you can do ('Kaya kar sakte ho'), do not give vague generic answers. Deliver an authoritative executive overview of the exact CRM operations, live stats (819 clients), and actionable sample commands the user can give you right now."""
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
WEB_APP_DIR = os.path.join(PROJECT_ROOT, "web_app")
PANKH_ICON = os.path.join(BASE_DIR, "mor_pankh.png")
if not os.path.exists(PANKH_ICON):
    PANKH_ICON = os.path.join(PROJECT_ROOT, "mor_pankh.png")

PORT = 5000

def is_server_running(port=PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def run_local_server():
    if is_server_running(PORT):
        return
    import importlib.util
    server_py = os.path.join(WEB_APP_DIR, "server.py")
    if os.path.exists(server_py):
        spec = importlib.util.spec_from_file_location("server_module", server_py)
        srv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(srv)
        t = threading.Thread(target=srv.start_server, daemon=True)
        t.start()
        time.sleep(1)

class AchyutaDesktopWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Achyuta 2.0")
        self.resize(1220, 800)
        self.setMinimumSize(960, 640)

        # Set Window Icon
        if os.path.exists(PANKH_ICON):
            self.setWindowIcon(QIcon(PANKH_ICON))

        # Main Layout & Web Engine
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.browser = QWebEngineView(self)
        self.browser.setStyleSheet("background-color: #212121;")
        layout.addWidget(self.browser)

        # Load Achyuta Interface
        self.load_interface()

    def load_interface(self):
        url = f"http://localhost:{PORT}"
        self.browser.setUrl(QUrl(url))

def main():
    # Ensure server is running
    run_local_server()

    app = QApplication(sys.argv)
    app.setApplicationName("Achyuta 2.0")

    if os.path.exists(PANKH_ICON):
        app.setWindowIcon(QIcon(PANKH_ICON))

    window = AchyutaDesktopWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

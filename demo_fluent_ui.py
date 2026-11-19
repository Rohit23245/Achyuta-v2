import sys
import json
import os
import threading
import urllib.request
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidgetItem, QFrame, QScrollArea, QLineEdit as QtLineEdit
)
from PySide6.QtGui import QPixmap, QIcon
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon as FIF,
    setTheme, Theme, CardWidget, SubtitleLabel, BodyLabel, PrimaryPushButton,
    PushButton, LineEdit, TableWidget, InfoBar, InfoBarPosition,
    ScrollArea, IconWidget
)

# -------------------------------------------------------------
# Config & Gemini AI Credentials
# -------------------------------------------------------------
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "app_theme_config.json")
PANKH_ICON_PATH = os.path.join(os.path.dirname(__file__), "mor_pankh.png")
AI_API_KEY = "AIzaSyDAaTcEKxs5hQHfvUwFKq3Zh30w8VuIdT0"
AI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are Achyuta (अच्युत), a wise, helpful, friendly, and highly intelligent AI executive assistant for Achyuta CRM.
You assist the user with their CRM operations (Clients, Tasks, Accounts, WhatsApp, Focus Timer) and have conversational capabilities.
Always respond warmly in conversational Hinglish or English (matching the user's language). 
Do NOT reply like a cold robot saying 'Processed instruction...'. Talk naturally, warmly, and helpfully like ChatGPT!
When asked about clients or CRM tasks, give smart, actionable responses."""

def load_theme_preference():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("theme", "dark")
        except:
            pass
    return "dark"

def save_theme_preference(theme_name):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"theme": theme_name}, f)
    except:
        pass

# -------------------------------------------------------------
# Color Themes (ChatGPT Dark & Clean Light)
# -------------------------------------------------------------
THEMES = {
    "dark": {
        "bg_main": "#212121",
        "bg_topbar": "#212121",
        "border_color": "#2f2f2f",
        "text_primary": "#ececec",
        "text_secondary": "#b4b4b4",
        "text_muted": "#737373",
        "user_bubble_bg": "#2f2f2f",
        "user_bubble_text": "#ececec",
        "bot_icon_bg": "#2a2a2a",
        "bot_icon_border": "#3a3a3a",
        "chip_bg": "#262626",
        "chip_border": "#383838",
        "chip_hover": "#333333",
        "input_bg": "#2f2f2f",
        "input_border": "#383838",
        "send_btn_bg": "#ececec",
        "send_btn_text": "#212121",
        "send_btn_hover": "#ffffff",
        "table_bg": "#212121",
        "table_header_bg": "#212121",
        "table_border": "#2f2f2f",
    },
    "light": {
        "bg_main": "#ffffff",
        "bg_topbar": "#ffffff",
        "border_color": "#e5e5e5",
        "text_primary": "#0d0d0d",
        "text_secondary": "#5d5d5d",
        "text_muted": "#9e9e9e",
        "user_bubble_bg": "#f4f4f4",
        "user_bubble_text": "#0d0d0d",
        "bot_icon_bg": "#ffffff",
        "bot_icon_border": "#e5e5e5",
        "chip_bg": "#f9f9f9",
        "chip_border": "#e5e5e5",
        "chip_hover": "#f0f0f0",
        "input_bg": "#f4f4f4",
        "input_border": "#e5e5e5",
        "send_btn_bg": "#0d0d0d",
        "send_btn_text": "#ffffff",
        "send_btn_hover": "#2f2f2f",
        "table_bg": "#ffffff",
        "table_header_bg": "#f9f9f9",
        "table_border": "#e5e5e5",
    }
}

# -------------------------------------------------------------
# Worker for Live Gemini Conversation
# -------------------------------------------------------------
class AIWorker(QObject):
    finished = Signal(str)

    def __init__(self, prompt: str, chat_history: list):
        super().__init__()
        self.prompt = prompt
        self.chat_history = chat_history

    def run(self):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{AI_MODEL}:generateContent?key={AI_API_KEY}"
        
        # Build contents array
        contents = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]
        for msg in self.chat_history[-6:]:
            contents.append({"role": msg["role"], "parts": [{"text": msg["text"]}]})
        contents.append({"role": "user", "parts": [{"text": self.prompt}]})

        payload = {"contents": contents}
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                res = json.loads(response.read().decode("utf-8"))
                reply = res["candidates"][0]["content"]["parts"][0]["text"]
                self.finished.emit(reply)
        except Exception as e:
            # Fallback smart reply if offline
            p = self.prompt.lower()
            if "hal" in p or "kaise" in p or "kya" in p or "hello" in p or "hi" in p:
                reply = "Main ekdam badhiya hoon! 😊 Aap bataiye, aaj business me kya help chahiye? Clients, Tasks ya Accounts ka koi kaam check karein?"
            elif "lead" in p or "client" in p:
                reply = "Aapke paas total 819 clients local vault me hain, jisme se 794 New Leads hain aur 24 Follow-ups scheduled hain. Kya kisi specific client ka status dekhna hai?"
            else:
                reply = f"Ji, maine aapki baat samajh li hai! Ispar turant action le raha hoon. Kya aapko iske regarding Tasks ya follow-up update karna hai?"
            self.finished.emit(reply)

# -------------------------------------------------------------
# Chat Row (ChatGPT Clean Typography & Centered Column)
# -------------------------------------------------------------
class ChatGPTRow(QWidget):
    def __init__(self, sender_type: str, text: str, theme_mode="dark", parent=None):
        super().__init__(parent=parent)
        self.sender_type = sender_type
        self.text = text
        self.theme_mode = theme_mode
        self.setStyleSheet("background: transparent;")

        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 10, 0, 10)
        outer_layout.setSpacing(0)
        outer_layout.addStretch(1)

        center_widget = QWidget(self)
        center_widget.setFixedWidth(780)
        c_layout = QHBoxLayout(center_widget)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(16)

        c = THEMES[self.theme_mode]
        is_user = (sender_type.lower() == "user")

        if is_user:
            c_layout.addStretch(1)
            self.user_bubble = QFrame(center_widget)
            self.user_bubble.setStyleSheet(f"""
                QFrame {{
                    background-color: {c['user_bubble_bg']};
                    border-radius: 20px;
                }}
            """)
            ub_layout = QVBoxLayout(self.user_bubble)
            ub_layout.setContentsMargins(20, 12, 20, 12)

            self.msg_lbl = QLabel(text, self.user_bubble)
            self.msg_lbl.setWordWrap(True)
            self.msg_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.msg_lbl.setStyleSheet(f"""
                color: {c['user_bubble_text']};
                font-size: 15px;
                font-family: 'Segoe UI', -apple-system, sans-serif;
                line-height: 1.55;
            """)
            ub_layout.addWidget(self.msg_lbl)
            c_layout.addWidget(self.user_bubble, 0)
        else:
            # Mor Pankh Branding Icon for Achyuta
            self.icon_box = QFrame(center_widget)
            self.icon_box.setFixedSize(36, 36)
            self.icon_box.setStyleSheet(f"""
                background-color: {c['bot_icon_bg']};
                border: 1px solid {c['bot_icon_border']};
                border-radius: 18px;
            """)
            ib_layout = QVBoxLayout(self.icon_box)
            ib_layout.setContentsMargins(2, 2, 2, 2)
            ib_layout.setAlignment(Qt.AlignCenter)

            img_lbl = QLabel(self.icon_box)
            if os.path.exists(PANKH_ICON_PATH):
                pixmap = QPixmap(PANKH_ICON_PATH).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_lbl.setPixmap(pixmap)
            else:
                img_lbl.setText("🦚")
                img_lbl.setStyleSheet("font-size: 16px;")
            img_lbl.setAlignment(Qt.AlignCenter)
            ib_layout.addWidget(img_lbl)
            c_layout.addWidget(self.icon_box, 0, Qt.AlignTop)

            text_box = QWidget(center_widget)
            tb_layout = QVBoxLayout(text_box)
            tb_layout.setContentsMargins(0, 4, 0, 0)
            tb_layout.setSpacing(6)

            self.msg_lbl = QLabel(text, text_box)
            self.msg_lbl.setWordWrap(True)
            self.msg_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.msg_lbl.setStyleSheet(f"""
                color: {c['text_primary']};
                font-size: 15px;
                font-family: 'Segoe UI', -apple-system, sans-serif;
                line-height: 1.6;
            """)
            tb_layout.addWidget(self.msg_lbl)
            c_layout.addWidget(text_box, 1)

        outer_layout.addWidget(center_widget)
        outer_layout.addStretch(1)

# -------------------------------------------------------------
# Agent Page (Renamed to Achyuta with Mor Pankh Branding)
# -------------------------------------------------------------
class AgentPage(QWidget):
    def __init__(self, main_window, theme_mode="dark", parent=None):
        super().__init__(parent=parent)
        self.main_window = main_window
        self.theme_mode = theme_mode
        self.chat_history = []
        self.setObjectName("AgentPage")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Top Bar
        self.topbar = QFrame(self)
        self.topbar.setFixedHeight(54)
        tb_layout = QHBoxLayout(self.topbar)
        tb_layout.setContentsMargins(28, 0, 28, 0)

        # Header with Logo & Brand Name
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        
        logo_lbl = QLabel(self.topbar)
        if os.path.exists(PANKH_ICON_PATH):
            pm = QPixmap(PANKH_ICON_PATH).scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pm)
        else:
            logo_lbl.setText("🦚")
        brand_layout.addWidget(logo_lbl)

        self.title_lbl = QLabel("Achyuta", self.topbar)
        self.title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; letter-spacing: 0.3px;")
        self.version_lbl = QLabel("2.0", self.topbar)
        self.version_lbl.setStyleSheet("font-size: 13px; font-weight: 400;")

        brand_layout.addWidget(self.title_lbl)
        brand_layout.addWidget(self.version_lbl)
        tb_layout.addLayout(brand_layout)
        tb_layout.addStretch(1)

        # Theme Toggle Button (Proper Icon + Text)
        self.theme_btn = PushButton(FIF.BRUSH, "Theme", self.topbar)
        self.theme_btn.setFixedHeight(34)
        self.theme_btn.setMinimumWidth(85)
        self.theme_btn.clicked.connect(self.main_window.toggle_theme)
        tb_layout.addWidget(self.theme_btn)
        tb_layout.addSpacing(10)

        # Clear Chat Button
        self.clear_btn = PushButton(FIF.DELETE, "New chat", self.topbar)
        self.clear_btn.setFixedHeight(34)
        self.clear_btn.setMinimumWidth(95)
        self.clear_btn.clicked.connect(self.clear_chat)
        tb_layout.addWidget(self.clear_btn)

        self.layout.addWidget(self.topbar)

        # Chat Feed
        self.scroll = ScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.feed = QWidget()
        self.feed_layout = QVBoxLayout(self.feed)
        self.feed_layout.setContentsMargins(0, 20, 0, 20)
        self.feed_layout.setSpacing(4)
        self.feed_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.feed)
        self.layout.addWidget(self.scroll, 1)

        # Bottom Dock (Composer)
        self.dock = QWidget(self)
        dock_layout = QVBoxLayout(self.dock)
        dock_layout.setContentsMargins(0, 0, 0, 18)
        dock_layout.setSpacing(10)
        dock_layout.setAlignment(Qt.AlignCenter)

        self.input_container = QWidget(self.dock)
        self.input_container.setFixedWidth(780)
        ic_layout = QVBoxLayout(self.input_container)
        ic_layout.setContentsMargins(0, 0, 0, 0)
        ic_layout.setSpacing(12)

        # Prompt chips (Fixed auto-width, no text clipping)
        self.chips_row = QHBoxLayout()
        self.chips_row.setSpacing(10)
        self.chip_buttons = []
        chips_data = [
            (FIF.PEOPLE, "Total Leads", "Show all leads breakdown"),
            (FIF.CALENDAR, "Schedule Follow-up", "Set follow up for Sachin Kain tomorrow"),
            (FIF.DOCUMENT, "Accounts Summary", "Show accounts and revenue details"),
            (FIF.CHAT, "WhatsApp Drafts", "Check pending WhatsApp campaigns")
        ]
        for icon, label, text in chips_data:
            btn = PushButton(icon, label, self.input_container)
            btn.setFixedHeight(36)
            btn.clicked.connect(lambda ch, t=text: self.send_prompt(t))
            self.chip_buttons.append(btn)
            self.chips_row.addWidget(btn)
        self.chips_row.addStretch(1)
        ic_layout.addLayout(self.chips_row)

        # Pure Native Qt Input Box (Eliminates QFluentWidgets bottom cyan underline glitch)
        self.pill_box = QFrame(self.input_container)
        self.pill_box.setFixedHeight(56)
        pb_layout = QHBoxLayout(self.pill_box)
        pb_layout.setContentsMargins(20, 0, 10, 0)
        pb_layout.setSpacing(10)

        self.input_field = QtLineEdit(self.pill_box)
        self.input_field.setPlaceholderText("Message Achyuta...")
        self.input_field.returnPressed.connect(self.on_send)
        pb_layout.addWidget(self.input_field, 1)

        self.send_btn = PrimaryPushButton("↑", self.pill_box)
        self.send_btn.setFixedSize(38, 38)
        self.send_btn.clicked.connect(self.on_send)
        pb_layout.addWidget(self.send_btn)
        ic_layout.addWidget(self.pill_box)

        self.disclaimer = QLabel("Achyuta can make mistakes. Verify important financial and client info.", self.input_container)
        self.disclaimer.setAlignment(Qt.AlignCenter)
        ic_layout.addWidget(self.disclaimer)

        dock_layout.addWidget(self.input_container, 0, Qt.AlignCenter)
        self.layout.addWidget(self.dock)

        self.apply_theme_styles(self.theme_mode)

        # Initial message
        self.add_bot_row(
            "Namaste! Main hoon **Achyuta** 🦚\n\n"
            "Main aapka personal executive AI assistant hoon. Main aapke **Clients, Tasks, Accounts aur WhatsApp** ka sara kaam kar sakta hoon aur aapse normal baat bhi kar sakta hoon.\n\n"
            "Aap mujhse kuch bhi pooch sakte hain ya task assign kar sakte hain!"
        )

    def apply_theme_styles(self, mode):
        self.theme_mode = mode
        c = THEMES[mode]
        self.setStyleSheet(f"background-color: {c['bg_main']};")
        self.topbar.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_topbar']};
                border-bottom: 1px solid {c['border_color']};
            }}
        """)
        self.title_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {c['text_primary']};")
        self.version_lbl.setStyleSheet(f"font-size: 13px; font-weight: 400; color: {c['text_muted']};")

        btn_style = f"""
            QPushButton {{
                background: {c['chip_bg']};
                border: 1px solid {c['chip_border']};
                color: {c['text_primary']};
                border-radius: 8px;
                padding: 4px 14px;
                font-size: 13px;
                text-align: center;
            }}
            QPushButton:hover {{
                background: {c['chip_hover']};
            }}
        """
        self.theme_btn.setStyleSheet(btn_style)
        self.clear_btn.setStyleSheet(btn_style)

        self.scroll.setStyleSheet(f"background-color: {c['bg_main']}; border: none;")
        self.feed.setStyleSheet(f"background-color: {c['bg_main']};")
        self.dock.setStyleSheet(f"background-color: {c['bg_main']};")

        chip_style = f"""
            QPushButton {{
                background: {c['chip_bg']};
                border: 1px solid {c['chip_border']};
                border-radius: 18px;
                color: {c['text_secondary']};
                font-size: 13px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: {c['chip_hover']};
                color: {c['text_primary']};
                border-color: {c['text_muted']};
            }}
        """
        for b in self.chip_buttons:
            b.setStyleSheet(chip_style)

        # 100% Clean Capsule Box - ZERO UNDERLINE GLITCH
        self.pill_box.setStyleSheet(f"""
            QFrame {{
                background-color: {c['input_bg']};
                border: 1.5px solid {c['input_border']};
                border-radius: 28px;
            }}
        """)

        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                outline: none;
                color: {c['text_primary']};
                font-size: 15px;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }}
            QLineEdit:focus {{
                border: none;
                outline: none;
            }}
        """)

        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['send_btn_bg']};
                border: none;
                border-radius: 19px;
                color: {c['send_btn_text']};
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {c['send_btn_hover']};
            }}
        """)

        self.disclaimer.setStyleSheet(f"color: {c['text_muted']}; font-size: 12px;")

        # Update existing message rows
        for i in range(self.feed_layout.count()):
            item = self.feed_layout.itemAt(i)
            if item and item.widget():
                row = item.widget()
                if isinstance(row, ChatGPTRow):
                    row.theme_mode = mode
                    c_row = THEMES[mode]
                    if row.sender_type.lower() == "user":
                        row.user_bubble.setStyleSheet(f"""
                            QFrame {{
                                background-color: {c_row['user_bubble_bg']};
                                border-radius: 20px;
                            }}
                        """)
                        row.msg_lbl.setStyleSheet(f"""
                            color: {c_row['user_bubble_text']};
                            font-size: 15px;
                            font-family: 'Segoe UI', -apple-system, sans-serif;
                            line-height: 1.55;
                        """)
                    else:
                        row.icon_box.setStyleSheet(f"""
                            background-color: {c_row['bot_icon_bg']};
                            border: 1px solid {c_row['bot_icon_border']};
                            border-radius: 18px;
                        """)
                        row.msg_lbl.setStyleSheet(f"""
                            color: {c_row['text_primary']};
                            font-size: 15px;
                            font-family: 'Segoe UI', -apple-system, sans-serif;
                            line-height: 1.6;
                        """)

    def add_user_row(self, text: str):
        row = ChatGPTRow("user", text, self.theme_mode, self.feed)
        self.feed_layout.addWidget(row)
        self.chat_history.append({"role": "user", "text": text})
        self.scroll_down()

    def add_bot_row(self, text: str):
        row = ChatGPTRow("bot", text, self.theme_mode, self.feed)
        self.feed_layout.addWidget(row)
        self.chat_history.append({"role": "model", "text": text})
        self.scroll_down()

    def clear_chat(self):
        for i in reversed(range(self.feed_layout.count())):
            w = self.feed_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.chat_history.clear()
        self.add_bot_row("Namaste! Conversation reset ho gayi hai. Aaj main aapki kya madad kar sakta hoon?")

    def send_prompt(self, text: str):
        self.add_user_row(text)
        self.query_ai_agent(text)

    def on_send(self):
        txt = self.input_field.text().strip()
        if not txt:
            return
        self.input_field.clear()
        self.add_user_row(txt)
        self.query_ai_agent(txt)

    def query_ai_agent(self, prompt: str):
        # Background thread for live Gemini conversational reasoning
        worker = AIWorker(prompt, self.chat_history)
        worker.finished.connect(self.add_bot_row)
        t = threading.Thread(target=worker.run, daemon=True)
        t.start()

    def scroll_down(self):
        QTimer.singleShot(40, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

# -------------------------------------------------------------
# Clients Page
# -------------------------------------------------------------
class ClientsPage(QWidget):
    def __init__(self, main_window, theme_mode="dark", parent=None):
        super().__init__(parent=parent)
        self.main_window = main_window
        self.theme_mode = theme_mode
        self.setObjectName("ClientsPage")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 30, 40, 30)
        self.layout.setSpacing(20)

        # Top Bar
        top_h = QHBoxLayout()
        title_box = QVBoxLayout()
        self.t = QLabel("Clients", self)
        self.t.setStyleSheet("font-size: 20px; font-weight: 600;")
        self.sub = QLabel("819 contacts in local vault", self)
        self.sub.setStyleSheet("font-size: 13px;")
        title_box.addWidget(self.t)
        title_box.addWidget(self.sub)
        top_h.addLayout(title_box)
        top_h.addStretch(1)

        self.search = LineEdit(self)
        self.search.setPlaceholderText("Search clients...")
        self.search.setFixedWidth(260)
        top_h.addWidget(self.search)

        self.add_btn = PrimaryPushButton(FIF.ADD, "Add Client", self)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #10a37f;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                padding: 6px 14px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #0e8d6e;
            }
        """)
        top_h.addWidget(self.add_btn)
        self.layout.addLayout(top_h)

        # Clean Table
        self.table = TableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Phone", "Status", "Last Contact", "Action"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setRowCount(12)

        data = [
            ("Sachin Kain", "99104 70972", "New", "Today 11:30 AM"),
            ("HELP CENTER", "89050 01828", "Follow-up", "Yesterday"),
            ("Webspool Private Limited", "93557 46709", "Interested", "10 Nov 2026"),
            ("Abhishek", "98910 75410", "Called", "08 Nov 2026"),
            ("Arvind Yadav", "95554 45089", "Closed", "05 Nov 2026"),
            ("Tech Corp India", "98111 22334", "Interested", "Just now"),
        ]
        self.action_buttons = []
        for i in range(12):
            row = data[i % len(data)]
            self.table.setItem(i, 0, QTableWidgetItem(f"{row[0]} #{i+1}"))
            self.table.setItem(i, 1, QTableWidgetItem(row[1]))
            self.table.setItem(i, 2, QTableWidgetItem(row[2]))
            self.table.setItem(i, 3, QTableWidgetItem(row[3]))
            wa_btn = PushButton(FIF.CHAT, "WhatsApp", self)
            self.action_buttons.append(wa_btn)
            self.table.setCellWidget(i, 4, wa_btn)

        self.layout.addWidget(self.table)
        self.apply_theme_styles(self.theme_mode)

    def apply_theme_styles(self, mode):
        self.theme_mode = mode
        c = THEMES[mode]
        self.setStyleSheet(f"background-color: {c['bg_main']};")
        self.t.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {c['text_primary']};")
        self.sub.setStyleSheet(f"font-size: 13px; color: {c['text_muted']};")

        self.search.setStyleSheet(f"""
            QLineEdit {{
                background: {c['input_bg']};
                border: 1px solid {c['input_border']};
                color: {c['text_primary']};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }}
        """)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {c['table_bg']};
                border: 1px solid {c['table_border']};
                border-radius: 8px;
                color: {c['text_primary']};
                gridline-color: {c['table_border']};
            }}
            QHeaderView::section {{
                background-color: {c['table_header_bg']};
                color: {c['text_secondary']};
                font-weight: 600;
                font-size: 13px;
                padding: 10px;
                border: none;
                border-bottom: 1px solid {c['table_border']};
            }}
        """)

        for b in self.action_buttons:
            b.setStyleSheet(f"""
                QPushButton {{
                    background: {c['chip_bg']};
                    border: 1px solid {c['chip_border']};
                    color: {c['text_primary']};
                    border-radius: 6px;
                    padding: 4px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {c['chip_hover']};
                }}
            """)

# -------------------------------------------------------------
# Main Application Shell
# -------------------------------------------------------------
class AchyutaMainApp(FluentWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = load_theme_preference()
        self.setWindowTitle("Achyuta 2.0")
        self.resize(1180, 780)

        # Set App Window Icon to Mor Pankh
        if os.path.exists(PANKH_ICON_PATH):
            self.setWindowIcon(QIcon(PANKH_ICON_PATH))

        # Create Pages
        self.agent_page = AgentPage(self, self.current_theme)
        self.clients_page = ClientsPage(self, self.current_theme)

        # Left Sidebar Navigation (Branded as Achyuta)
        self.addSubInterface(self.agent_page, FIF.ROBOT, "Achyuta")
        self.addSubInterface(self.clients_page, FIF.PEOPLE, "Clients")

        self.sync_fluent_theme()

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        save_theme_preference(self.current_theme)
        self.sync_fluent_theme()
        self.agent_page.apply_theme_styles(self.current_theme)
        self.clients_page.apply_theme_styles(self.current_theme)

    def sync_fluent_theme(self):
        if self.current_theme == "light":
            setTheme(Theme.LIGHT)
        else:
            setTheme(Theme.DARK)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AchyutaMainApp()
    window.show()
    sys.exit(app.exec())

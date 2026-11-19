import os
import sys
import threading
import json
import time
import sqlite3
import shutil
import tempfile
import webbrowser
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import keyboard
import pyttsx3

# AI Intelligence Configuration (Internal Core)
AI_API_KEY = "AIzaSyDAaTcEKxs5hQHfvUwFKq3Zh30w8VuIdT0"
AI_MODEL = "gemini-2.5-flash"

# Data Services Configuration
try:
    import gspread
    from google.oauth2.service_account import Credentials
    DATA_SERVICE_AVAILABLE = True
except Exception:
    DATA_SERVICE_AVAILABLE = False

CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json.json")
DATA_VAULT_ID = "1z9iTH6lSXUiBxrFX1kqkdBvuAGl09oYlAL7nsA80o4A"
ICON_ICO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mor_pankh.ico")
ICON_PNG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mor_pankh.png")
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_settings.json")
CAMPAIGN_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_campaign_log.json")
CLIENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clients_vault.json")
EMPLOYEES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "employees_vault.json")
TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks_vault.json")
TRANSACTIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts_vault.json")

# =========================================================================
# 2027 LUXURY AIR-TABLE / LINEAR DESIGN SYSTEM
# =========================================================================
C_CANVAS        = "#f1f5f9"   # Modern slate-tinted canvas with contrast
C_SIDEBAR       = "#ffffff"   # Pure crisp white sidebar
C_CARD          = "#ffffff"   # Elevated card surface
C_BORDER        = "#e2e8f0"   # Light structured border
C_ROW_HOVER     = "#f0fdfa"   # Soft mint hover
C_ROW_SELECTED  = "#e0f2f1"   # Deep mint active row

# Peacock & Jewel Accents
C_TEAL_DARK     = "#004d40"   # Deep peacock core
C_TEAL_PRIMARY  = "#00838f"   # Vibrant brand cyan/teal
C_TEAL_LIGHT    = "#e0f2f1"   # Soft mint badge
C_GOLD          = "#d97706"

# Modern High-Contrast Typography
C_TEXT_HERO     = "#0f172a"   # Slate 900
C_TEXT_BODY     = "#334155"   # Slate 700
C_TEXT_MUTED    = "#64748b"   # Slate 500

# Professional Fonts
FONT_BRAND      = ("Segoe UI", 15, "bold")
FONT_NAV        = ("Segoe UI Semibold", 10)
FONT_SEARCH     = ("Segoe UI", 11)
FONT_HEAD       = ("Segoe UI Semibold", 10)
FONT_NAME       = ("Segoe UI Semibold", 10)
FONT_DATA       = ("Segoe UI", 10)
FONT_BADGE      = ("Segoe UI Bold", 9)
FONT_CHAT       = ("Segoe UI", 10)

# Status Badge Themes
STATUS_STYLES = {
    "New":        {"fg": "#0284c7", "bg": "#e0f2fe", "dot": "●"},
    "Follow-up":  {"fg": "#d97706", "bg": "#fef3c7", "dot": "●"},
    "Called":     {"fg": "#4f46e5", "bg": "#e0e7ff", "dot": "●"},
    "Interested": {"fg": "#059669", "bg": "#d1fae5", "dot": "★"},
    "Closed":     {"fg": "#16a34a", "bg": "#dcfce7", "dot": "✔"},
    "Lost":       {"fg": "#dc2626", "bg": "#fee2e2", "dot": "✖"},
}


def create_vector_icon(icon_type, color=C_TEAL_PRIMARY, size=(22, 22)):
    w, h = size
    scale = 4
    img = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if icon_type == "search":
        cx, cy, r = 9 * scale, 9 * scale, 5.5 * scale
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=int(2.0 * scale))
        draw.line([13.5 * scale, 13.5 * scale, 18.5 * scale, 18.5 * scale], fill=color, width=int(2.4 * scale))

    elif icon_type == "leads":
        draw.ellipse([6 * scale, 3 * scale, 12 * scale, 9 * scale], outline=color, width=int(1.8 * scale))
        draw.arc([3 * scale, 10 * scale, 15 * scale, 18 * scale], start=180, end=360, fill=color, width=int(1.8 * scale))
        draw.ellipse([13 * scale, 2 * scale, 18 * scale, 7 * scale], outline=color, width=int(1.8 * scale))
        draw.arc([11 * scale, 8 * scale, 20 * scale, 15 * scale], start=210, end=360, fill=color, width=int(1.8 * scale))

    elif icon_type == "ai":
        cx, cy = (w * scale) / 2, (h * scale) / 2
        r_out = 9 * scale
        r_in = 2.8 * scale
        points = [
            (cx, cy - r_out),
            (cx + r_in, cy - r_in),
            (cx + r_out, cy),
            (cx + r_in, cy + r_in),
            (cx, cy + r_out),
            (cx - r_in, cy + r_in),
            (cx - r_out, cy),
            (cx - r_in, cy - r_in)
        ]
        draw.polygon(points, fill=color)

    elif icon_type == "whatsapp":
        # Clean chat bubble representation
        draw.rounded_rectangle([3 * scale, 3 * scale, 19 * scale, 17 * scale], radius=4 * scale, outline=color, width=int(1.8 * scale))
        draw.polygon([(6 * scale, 17 * scale), (4 * scale, 21 * scale), (10 * scale, 17 * scale)], fill=color)

    elif icon_type == "employees":
        # Professional employee / team vector badge
        cx, cy = 11 * scale, 8 * scale
        r = 4.5 * scale
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=int(1.8 * scale))
        draw.arc([4 * scale, 13 * scale, 18 * scale, 21 * scale], start=180, end=360, fill=color, width=int(1.8 * scale))
        draw.line([7 * scale, 20 * scale, 15 * scale, 20 * scale], fill=color, width=int(1.8 * scale))

    elif icon_type == "tasks":
        # Clipboard / checklist vector badge
        draw.rounded_rectangle([5 * scale, 4 * scale, 17 * scale, 20 * scale], radius=2 * scale, outline=color, width=int(1.8 * scale))
        draw.line([7 * scale, 3 * scale, 15 * scale, 3 * scale], fill=color, width=int(2.0 * scale))
        draw.line([8 * scale, 9 * scale, 14 * scale, 9 * scale], fill=color, width=int(1.6 * scale))
        draw.line([8 * scale, 13 * scale, 14 * scale, 13 * scale], fill=color, width=int(1.6 * scale))
        draw.line([8 * scale, 17 * scale, 12 * scale, 17 * scale], fill=color, width=int(1.6 * scale))

    elif icon_type == "accounts":
        # Elegant ledger / rupee currency vault icon
        cx, cy, r = 11 * scale, 11 * scale, 7.5 * scale
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=int(1.8 * scale))
        draw.line([8 * scale, 8 * scale, 14 * scale, 8 * scale], fill=color, width=int(1.6 * scale))
        draw.line([8 * scale, 11 * scale, 13 * scale, 11 * scale], fill=color, width=int(1.6 * scale))
        draw.line([10 * scale, 8 * scale, 10 * scale, 15 * scale], fill=color, width=int(1.6 * scale))
        draw.line([10 * scale, 11 * scale, 13.5 * scale, 15 * scale], fill=color, width=int(1.6 * scale))

    elif icon_type == "settings":
        # Minimalist gear ring
        cx, cy, r = 11 * scale, 11 * scale, 6.5 * scale
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=int(2.2 * scale))
        draw.ellipse([cx - 2.5 * scale, cy - 2.5 * scale, cx + 2.5 * scale, cy + 2.5 * scale], fill=color)

    elif icon_type == "timer":
        # Minimalist stopwatch ring
        cx, cy, r = 11 * scale, 12 * scale, 6.5 * scale
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=int(1.8 * scale))
        draw.line([cx, cy, cx, cy - 4 * scale], fill=color, width=int(1.8 * scale))
        draw.line([cx, cy, cx + 3 * scale, cy], fill=color, width=int(1.8 * scale))
        draw.line([cx - 2.5 * scale, cy - 8 * scale, cx + 2.5 * scale, cy - 8 * scale], fill=color, width=int(1.8 * scale))

    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


class AchyutaAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Achyuta")
        self.geometry("1240x820")
        self.minsize(1040, 700)
        self.config(bg=C_CANVAS)
        
        # Set Window Mor Pankh Icon
        if os.path.exists(ICON_ICO_PATH):
            try:
                self.iconbitmap(ICON_ICO_PATH)
            except Exception:
                pass

        self.center_window()
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False))
        
        self.sidebar_width = 230

        # Normalized Client Records & Pagination State
        self.gc = None
        self.current_spreadsheet = None
        self.all_clients = []
        self.filtered_clients = []
        self.active_status_filter = "All"
        self.clients_limit = 25  # Crisp safe batch limit
        self.load_clients_data()

        # WhatsApp Campaign State & Persistence
        self.default_whatsapp_text = ""
        self.whatsapp_logs = {}  # {client_key: {"name": str, "phone": str, "time": str, "date": str}}
        self.load_whatsapp_data()

        # Employees Management State & Persistence
        self.all_employees = []
        self.filtered_employees = []
        self.active_emp_status_filter = "All"
        self.load_employees_data()

        # Task Management State & Persistence
        self.all_tasks = []
        self.filtered_tasks = []
        self.active_task_status_filter = "All"
        self.load_tasks_data()

        # Accounts Management State & Persistence (Income, Expenses, Salaries)
        self.all_transactions = []
        self.filtered_transactions = []
        self.active_acc_type_filter = "All"
        self.load_accounts_data()

        # Focus / Work Timer State
        self.timer_seconds_left = 0
        self.timer_initial_seconds = 0
        self.timer_is_running = False
        self.timer_after_id = None

        # TTS Engine
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 170)
            self.tts.setProperty("volume", 0.9)
        except Exception:
            self.tts = None

        self.load_icons()
        self.setup_ui()
        self.init_data_vault()

        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    def center_window(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        # Responsive default size for any display resolution (1366x768, 1080p, 2K, 4K)
        w = min(1400, int(sw * 0.92))
        h = min(880, int(sh * 0.88))
        x = max(0, int((sw - w) / 2))
        y = max(0, int((sh - h) / 2))
        self.geometry(f"{w}x{h}+{x}+{y}")
        # Start zoomed/maximized if on compact laptop screens
        if sw <= 1440:
            try:
                self.state('zoomed')
            except Exception:
                pass

    def hide_window(self):
        self.withdraw()

    def load_icons(self):
        self.mor_pankh_btn_photo = None
        self.mor_pankh_btn_hover = None
        self.mor_pankh_chat_icon = None
        if os.path.exists(ICON_PNG_PATH):
            try:
                raw = Image.open(ICON_PNG_PATH).convert("RGBA")
                
                # Render high-resolution luxury circular floating badge with soft drop shadow
                def _make_floating_badge(size=42, hover=False):
                    scale = 4
                    s = size * scale
                    pad = 6 * scale
                    total_s = s + pad * 2

                    shadow_img = Image.new("RGBA", (total_s, total_s), (0, 0, 0, 0))
                    d_sh = ImageDraw.Draw(shadow_img)
                    shadow_alpha = 75 if hover else 45
                    shadow_offset = int(3 * scale) if not hover else int(4 * scale)
                    d_sh.ellipse([pad, pad + shadow_offset, pad + s, pad + s + shadow_offset], fill=(15, 23, 42, shadow_alpha))
                    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=int(3 * scale)))

                    bg_color = (255, 255, 255, 255) if not hover else (240, 253, 250, 255)
                    border_color = (203, 213, 225, 255) if not hover else (15, 118, 110, 255)

                    btn_layer = Image.new("RGBA", (total_s, total_s), (0, 0, 0, 0))
                    d_btn = ImageDraw.Draw(btn_layer)
                    d_btn.ellipse([pad, pad, pad + s, pad + s], fill=bg_color, outline=border_color, width=int(1.5 * scale))

                    inner_s = int(s * 0.60)
                    mor_resized = raw.resize((inner_s, inner_s), Image.Resampling.LANCZOS)
                    off = pad + (s - inner_s) // 2
                    btn_layer.paste(mor_resized, (off, off), mor_resized)

                    final_img = Image.alpha_composite(shadow_img, btn_layer)
                    final_size = size + 12
                    return ImageTk.PhotoImage(final_img.resize((final_size, final_size), Image.Resampling.LANCZOS))

                self.mor_pankh_btn_photo = _make_floating_badge(42, hover=False)
                self.mor_pankh_btn_hover = _make_floating_badge(42, hover=True)

                raw_chat = raw.resize((18, 18), Image.Resampling.LANCZOS)
                self.mor_pankh_chat_icon = ImageTk.PhotoImage(raw_chat)
            except Exception:
                pass

        self.icons = {
            "leads": create_vector_icon("leads", color=C_TEAL_PRIMARY),
            "tasks": create_vector_icon("tasks", color=C_TEAL_PRIMARY),
            "accounts": create_vector_icon("accounts", color=C_TEAL_PRIMARY),
            "employees": create_vector_icon("employees", color=C_TEAL_PRIMARY),
            "ai": create_vector_icon("ai", color=C_TEAL_PRIMARY),
            "whatsapp": create_vector_icon("whatsapp", color=C_TEAL_PRIMARY),
            "timer": create_vector_icon("timer", color=C_TEAL_PRIMARY),
            "settings": create_vector_icon("settings", color=C_TEAL_PRIMARY),
            "search": create_vector_icon("search", color="#00838f", size=(20, 20))
        }

    def setup_ui(self):
        self.sidebar_frame = tk.Frame(self, bg=C_SIDEBAR, width=self.sidebar_width, highlightbackground=C_BORDER, highlightthickness=1)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        # Rightmost Sliding AI Copilot Panel (Google Gemini Studio Style Overlay)
        self.copilot_panel_width = 410
        self.copilot_is_open = False
        self.copilot_anim_id = None
        self.copilot_current_x = 9999

        self.content_frame = tk.Frame(self, bg=C_CANVAS)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.copilot_side_frame = tk.Frame(self, bg="#ffffff", highlightbackground="#cbd5e1", highlightthickness=1)
        # Positioned via .place as an ultra-fast smooth overlay over content_frame (zero layout recalculation lag)

        self.build_sidebar()
        self.build_copilot_side_panel()
        self.build_pages()
        self.switch_view("leads")

    def build_sidebar(self):
        self.sb_top = tk.Frame(self.sidebar_frame, bg=C_SIDEBAR, pady=22, padx=18)
        self.sb_top.pack(fill=tk.X)

        self.brand_box = tk.Frame(self.sb_top, bg=C_SIDEBAR)
        self.brand_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.brand_icon_photo = None
        if os.path.exists(ICON_PNG_PATH):
            try:
                raw_img = Image.open(ICON_PNG_PATH).convert("RGBA")
                raw_img = raw_img.resize((36, 36), Image.Resampling.LANCZOS)
                self.brand_icon_photo = ImageTk.PhotoImage(raw_img)
                self.logo_lbl = tk.Label(self.brand_box, image=self.brand_icon_photo, bg=C_SIDEBAR)
                self.logo_lbl.pack(side=tk.LEFT, padx=(0, 10))
            except Exception:
                pass

        self.title_lbl = tk.Label(
            self.brand_box,
            text="Achyuta",
            font=FONT_BRAND,
            fg=C_TEAL_DARK,
            bg=C_SIDEBAR
        )
        self.title_lbl.pack(side=tk.LEFT)

        self.sb_div = tk.Frame(self.sidebar_frame, bg=C_BORDER, height=1)
        self.sb_div.pack(fill=tk.X, padx=16, pady=(10, 18))

        self.nav_buttons = {}
        self.nav_data = [
            ("assistant", "ai", "Agent"),
            ("leads", "leads", "Clients"),
            ("tasks", "tasks", "Tasks"),
            ("accounts", "accounts", "Accounts"),
            ("employees", "employees", "Employees"),
            ("whatsapp", "whatsapp", "WhatsApp"),
            ("timer", "timer", "Focus Timer")
        ]

        for view_id, icon_key, label_text in self.nav_data:
            btn = tk.Button(
                self.sidebar_frame,
                image=self.icons[icon_key],
                compound=tk.LEFT,
                text=f"  {label_text}",
                font=FONT_NAV,
                bg=C_SIDEBAR,
                fg=C_TEXT_BODY,
                activebackground=C_TEAL_LIGHT,
                activeforeground=C_TEAL_DARK,
                bd=0,
                padx=16,
                pady=12,
                anchor=tk.W,
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda v=view_id: self.switch_view(v)
            )
            btn.pack(fill=tk.X, padx=10, pady=4)
            self.nav_buttons[view_id] = btn

    def switch_view(self, view_id):
        for v, btn in self.nav_buttons.items():
            if v == view_id:
                btn.config(bg=C_TEAL_LIGHT, fg=C_TEAL_DARK)
            else:
                btn.config(bg=C_SIDEBAR, fg=C_TEXT_BODY)

        for page_name, frame in self.pages.items():
            if page_name == view_id:
                frame.pack(fill=tk.BOTH, expand=True)
                if view_id == "whatsapp":
                    self.refresh_whatsapp_page()
                elif view_id == "employees":
                    self.refresh_employees_page()
                elif view_id == "tasks":
                    self.refresh_tasks_page()
                elif view_id == "accounts":
                    self.refresh_accounts_page()
            else:
                frame.pack_forget()

    def build_pages(self):
        self.pages = {}
        self.pages["leads"] = tk.Frame(self.content_frame, bg=C_CANVAS)
        self.build_clients_page(self.pages["leads"])

        self.pages["tasks"] = tk.Frame(self.content_frame, bg=C_CANVAS)
        self.build_tasks_page(self.pages["tasks"])

        self.pages["accounts"] = tk.Frame(self.content_frame, bg=C_CANVAS)
        self.build_accounts_page(self.pages["accounts"])

        self.pages["employees"] = tk.Frame(self.content_frame, bg=C_CANVAS)
        self.build_employees_page(self.pages["employees"])

        self.pages["whatsapp"] = tk.Frame(self.content_frame, bg=C_CANVAS)
        self.build_whatsapp_page(self.pages["whatsapp"])

        self.pages["timer"] = tk.Frame(self.content_frame, bg=C_CANVAS)
        self.build_timer_page(self.pages["timer"])

        self.pages["assistant"] = tk.Frame(self.content_frame, bg=C_CANVAS)
        self.build_assistant_page(self.pages["assistant"])

    def build_clients_page(self, parent):
        # 1. STUDIO HEADER ROW: SEARCH BAR + ACTION TOOLBAR (+ Add Lead)
        top_bar = tk.Frame(parent, bg=C_CANVAS, height=56)
        top_bar.pack(fill=tk.X, padx=20, pady=(16, 12))
        top_bar.pack_propagate(False)

        # Search Bar on Left / Center
        search_card = tk.Frame(top_bar, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        search_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        search_wrap = tk.Frame(search_card, bg="#ffffff")
        search_wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        tk.Label(search_wrap, image=self.icons["search"], bg="#ffffff").pack(side=tk.LEFT, padx=(6, 8))

        self.search_entry = tk.Entry(
            search_wrap,
            font=FONT_SEARCH,
            bg="#ffffff",
            fg=C_TEXT_HERO,
            insertbackground=C_TEAL_PRIMARY,
            relief=tk.FLAT,
            bd=0
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, ipady=4)
        self.search_entry.insert(0, "Search clients by name, phone number, status, notes...")
        self.search_entry.config(fg=C_TEXT_MUTED)

        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # Action Buttons on Right (Luxury Mor Pankh AI Trigger Badge + Add New Lead)
        ai_logo_kw = {"image": self.mor_pankh_btn_photo} if self.mor_pankh_btn_photo else {"image": self.icons["ai"]}
        self.copilot_trigger_btn = tk.Button(
            top_bar,
            **ai_logo_kw,
            bg=C_CANVAS,
            activebackground=C_CANVAS,
            relief=tk.FLAT,
            bd=0,
            padx=0,
            pady=0,
            cursor="hand2",
            command=self.toggle_copilot_side_panel
        )
        if self.mor_pankh_btn_hover:
            self.copilot_trigger_btn.bind("<Enter>", lambda e: self.copilot_trigger_btn.config(image=self.mor_pankh_btn_hover))
            self.copilot_trigger_btn.bind("<Leave>", lambda e: self.copilot_trigger_btn.config(image=self.mor_pankh_btn_photo))
        self.copilot_trigger_btn.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 4))

        add_lead_btn = tk.Button(
            top_bar,
            text="+ Add New Lead",
            font=("Segoe UI Semibold", 10),
            bg=C_TEAL_PRIMARY,
            fg="#ffffff",
            activebackground=C_TEAL_DARK,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.open_add_lead_modal
        )
        add_lead_btn.pack(side=tk.RIGHT, fill=tk.Y)

        # 2. STATUS FILTER CARDS BAR (Modern Floating Metric Cards)
        self.filter_cards_bar = tk.Frame(parent, bg=C_CANVAS)
        self.filter_cards_bar.pack(fill=tk.X, padx=20, pady=(0, 14))

        self.status_card_widgets = {}
        self.status_categories = [
            ("All", "All Clients", "#0284c7", "#eff6ff"),
            ("New", "New", "#0284c7", "#f0f9ff"),
            ("Follow-up", "Follow-up", "#d97706", "#fffbeb"),
            ("Called", "Called", "#6366f1", "#eef2ff"),
            ("Interested", "Interested", "#059669", "#ecfdf5"),
            ("Closed", "Closed", "#16a34a", "#f0fdf4"),
            ("Lost", "Lost", "#e11d48", "#fff1f2")
        ]

        for s_key, s_title, s_color, s_bg in self.status_categories:
            card = tk.Frame(
                self.filter_cards_bar,
                bg=C_CARD,
                highlightbackground="#e2e8f0",
                highlightthickness=1,
                padx=12,
                pady=8,
                cursor="hand2"
            )
            card.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)

            # Top indicator row
            top_line = tk.Frame(card, bg=C_CARD)
            top_line.pack(fill=tk.X)

            dot = tk.Label(top_line, text="●", font=("Segoe UI", 9), fg=s_color, bg=C_CARD)
            dot.pack(side=tk.LEFT, padx=(0, 5))

            title_lbl = tk.Label(top_line, text=s_title, font=("Segoe UI Semibold", 9), fg="#64748b", bg=C_CARD)
            title_lbl.pack(side=tk.LEFT)

            # Count row
            count_lbl = tk.Label(card, text="0", font=("Segoe UI", 16, "bold"), fg=C_TEXT_HERO, bg=C_CARD, anchor=tk.W)
            count_lbl.pack(anchor=tk.W, pady=(3, 0))

            self.status_card_widgets[s_key] = {
                "frame": card,
                "top_line": top_line,
                "dot": dot,
                "title": title_lbl,
                "count": count_lbl,
                "color": s_color,
                "bg_accent": s_bg
            }

            # Click binding to filter
            def _bind_filter_card(c_frame, key=s_key, widgets=[card, top_line, dot, title_lbl, count_lbl]):
                for w in widgets:
                    w.bind("<Button-1>", lambda e, k=key: self.select_status_filter(k))

            _bind_filter_card(card)

        # 3. 2027 BESPOKE MODERN DATA TABLE CONTAINER (Clean Elevated Card)
        self.table_card = tk.Frame(parent, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        self.table_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 18))

        # Modern Structured Header Row (Fixed Top with clean divider)
        self.col_widths = {
            "name": 200,
            "phone": 130,
            "status": 100,
            "last": 110,
            "next": 110,
            "action": 170
        }

        self.header_frame = tk.Frame(self.table_card, bg="#f8fafc", height=46, highlightbackground="#e2e8f0", highlightthickness=1)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)

        # Name fixed width
        f_name = tk.Frame(self.header_frame, bg="#f8fafc", width=self.col_widths["name"])
        f_name.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        f_name.pack_propagate(False)
        tk.Label(f_name, text="CLIENT NAME", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Phone fixed width
        f_phone = tk.Frame(self.header_frame, bg="#f8fafc", width=self.col_widths["phone"])
        f_phone.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        f_phone.pack_propagate(False)
        tk.Label(f_phone, text="PHONE NUMBER", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Status fixed width
        f_stat = tk.Frame(self.header_frame, bg="#f8fafc", width=self.col_widths["status"])
        f_stat.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        f_stat.pack_propagate(False)
        tk.Label(f_stat, text="STATUS", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Last Follow-up fixed width
        f_last = tk.Frame(self.header_frame, bg="#f8fafc", width=self.col_widths["last"])
        f_last.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        f_last.pack_propagate(False)
        tk.Label(f_last, text="LAST FOLLOW-UP", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Next Scheduled fixed width
        f_next = tk.Frame(self.header_frame, bg="#f8fafc", width=self.col_widths["next"])
        f_next.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        f_next.pack_propagate(False)
        tk.Label(f_next, text="NEXT SCHEDULED", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Notes expands dynamically to fill screen width
        f_notes = tk.Frame(self.header_frame, bg="#f8fafc")
        f_notes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        tk.Label(f_notes, text="NOTES", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Actions fixed width right
        f_act = tk.Frame(self.header_frame, bg="#f8fafc", width=self.col_widths["action"])
        f_act.pack(side=tk.RIGHT, fill=tk.Y, padx=4)
        f_act.pack_propagate(False)
        tk.Label(f_act, text="ACTIONS", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Scrollable Rows Stage using Coords-Driven Smooth Stage (Zero-Smear Architecture)
        self.canvas_wrap = tk.Frame(self.table_card, bg="#ffffff")
        self.canvas_wrap.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_wrap, bg="#ffffff", bd=0, highlightthickness=0)
        self.rows_frame = tk.Frame(self.canvas, bg="#ffffff")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        
        self.vsb = ttk.Scrollbar(self.canvas_wrap, orient="vertical")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.setup_zero_smear_scroll(self.canvas, self.canvas_window, self.rows_frame, self.vsb)

        # 3. MODERN SKELETON PRELOADER
        self.skeleton_overlay = tk.Frame(self.table_card, bg=C_CARD)
        self.skeleton_bars = []

        sk_head = tk.Frame(self.skeleton_overlay, bg="#f8fafc", height=46)
        sk_head.pack(fill=tk.X, padx=16, pady=(12, 10))
        sk_head.pack_propagate(False)

        col_ws = [200, 140, 100, 120, 120, 280]
        for cw in col_ws:
            b = tk.Frame(sk_head, bg="#cbd5e1", width=cw, height=14)
            b.pack(side=tk.LEFT, padx=14, pady=16)
            self.skeleton_bars.append(b)

        for i in range(9):
            rf = tk.Frame(self.skeleton_overlay, bg=C_CARD, height=44)
            rf.pack(fill=tk.X, padx=16, pady=3)
            rf.pack_propagate(False)

            r_bars = [180, 120, 90, 110, 110, 260]
            for bw in r_bars:
                bg_c = "#f1f5f9" if i % 2 == 0 else "#e2e8f0"
                b = tk.Frame(rf, bg=bg_c, width=bw, height=14)
                b.pack(side=tk.LEFT, padx=14, pady=15)
                self.skeleton_bars.append(b)

        self.loading_badge = tk.Label(
            self.skeleton_overlay,
            text="⚡ Loading Clients...",
            font=FONT_HEAD,
            fg=C_TEAL_DARK,
            bg=C_TEAL_LIGHT,
            padx=18,
            pady=6
        )
        self.loading_badge.place(relx=0.5, rely=0.88, anchor=tk.CENTER)

        self.show_skeleton()

    def setup_zero_smear_scroll(self, canvas, window_id, rows_frame, vsb):
        def _update_scrollbar():
            h_content = rows_frame.winfo_reqheight()
            h_view = canvas.winfo_height()
            max_off = max(0, h_content - h_view)
            curr = getattr(canvas, "_custom_offset", 0)
            if max_off <= 0:
                vsb.set(0.0, 1.0)
            else:
                top = curr / h_content
                bottom = (curr + h_view) / h_content
                vsb.set(top, min(1.0, bottom))

        def _scroll_to(new_offset):
            h_content = rows_frame.winfo_reqheight()
            h_view = canvas.winfo_height()
            max_off = max(0, h_content - h_view)
            clamped = max(0, min(max_off, new_offset))
            canvas._custom_offset = clamped
            canvas.coords(window_id, 0, -clamped)
            _update_scrollbar()

        def _on_vsb_command(*args):
            h_content = rows_frame.winfo_reqheight()
            h_view = canvas.winfo_height()
            max_off = max(0, h_content - h_view)
            curr = getattr(canvas, "_custom_offset", 0)
            if args[0] == "moveto":
                fraction = float(args[1])
                _scroll_to(int(fraction * h_content))
            elif args[0] == "scroll":
                num = int(args[1])
                if args[2] == "units":
                    _scroll_to(curr + num * 45)
                elif args[2] == "pages":
                    _scroll_to(curr + num * h_view)

        vsb.config(command=_on_vsb_command)

        def _on_mousewheel(e):
            if not canvas.winfo_ismapped():
                return
            delta = int(-1 * (e.delta / 120))
            curr = getattr(canvas, "_custom_offset", 0)
            _scroll_to(curr + delta * 48)

        def _on_canvas_configure(e):
            canvas.itemconfig(window_id, width=e.width)
            _update_scrollbar()

        def _on_rows_configure(e):
            _update_scrollbar()

        canvas.bind("<Configure>", _on_canvas_configure)
        rows_frame.bind("<Configure>", _on_rows_configure)

        canvas.bind("<MouseWheel>", _on_mousewheel)
        rows_frame.bind("<MouseWheel>", _on_mousewheel)

        canvas._custom_scroll_to = _scroll_to
        canvas._custom_update_sb = _update_scrollbar
        canvas._custom_wheel = _on_mousewheel

    def _smooth_mousewheel(self, canvas, event):
        if canvas and hasattr(canvas, "_custom_wheel"):
            canvas._custom_wheel(event)

    def bind_smooth_wheel_recursive(self, widget, canvas):
        if canvas and hasattr(canvas, "_custom_wheel"):
            widget.bind("<MouseWheel>", canvas._custom_wheel, add="+")
        for child in widget.winfo_children():
            self.bind_smooth_wheel_recursive(child, canvas)

    def _on_mousewheel(self, event):
        self._smooth_mousewheel(getattr(self, "canvas", None), event)

    def _on_search_focus_in(self, event):
        if self.search_entry.get() == "Search clients by name, phone number, status, notes...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=C_TEXT_HERO)

    def _on_search_focus_out(self, event):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search clients by name, phone number, status, notes...")
            self.search_entry.config(fg=C_TEXT_MUTED)

    def show_skeleton(self):
        self.skeleton_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    def hide_skeleton(self):
        self.skeleton_overlay.place_forget()

    # =========================================================================
    # SAFE LIMIT RENDERING WITH "LOAD MORE" (PREVENTS CRASHES & FREEZES)
    # =========================================================================
    def render_clients_table(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        if not self.filtered_clients:
            empty_box = tk.Frame(self.rows_frame, bg="#ffffff", pady=60)
            empty_box.pack(fill=tk.BOTH, expand=True)
            tk.Label(empty_box, text="🔍 No matching clients found", font=("Segoe UI Semibold", 12), fg=C_TEXT_MUTED, bg="#ffffff").pack()
            tk.Label(empty_box, text="Try searching with a different name, phone number or status keyword.", font=FONT_DATA, fg="#94a3b8", bg="#ffffff").pack(pady=(4, 0))
            return

        total_available = len(self.filtered_clients)
        limit_to_show = min(getattr(self, "clients_limit", 25), total_available)

        # Render rows strictly up to safe limit
        self._build_row_elements(0, limit_to_show)

        # "Load More" Card Bar if more items remain
        if limit_to_show < total_available:
            remaining = total_available - limit_to_show
            next_batch = min(25, remaining)

            footer_bar = tk.Frame(self.rows_frame, bg="#ffffff", pady=18)
            footer_bar.pack(fill=tk.X)

            info_lbl = tk.Label(
                footer_bar,
                text=f"Showing {limit_to_show} of {total_available} clients",
                font=("Segoe UI", 9),
                fg=C_TEXT_MUTED,
                bg="#ffffff"
            )
            info_lbl.pack(pady=(0, 8))

            load_more_btn = tk.Button(
                footer_bar,
                text=f"⬇  Load More ({next_batch} More)",
                font=("Segoe UI Semibold", 10),
                bg="#f1f5f9",
                fg=C_TEAL_DARK,
                activebackground=C_TEAL_LIGHT,
                activeforeground=C_TEAL_DARK,
                relief=tk.FLAT,
                bd=0,
                padx=24,
                pady=9,
                cursor="hand2",
                command=self.load_more_clients
            )
            load_more_btn.pack()

    def load_more_clients(self):
        total_available = len(self.filtered_clients)
        current = getattr(self, "clients_limit", 25)
        self.clients_limit = min(current + 25, total_available)
        self.render_clients_table()

    def _build_row_elements(self, start, end):
        for idx in range(start, end):
            client = self.filtered_clients[idx]
            bg_row = "#ffffff" if idx % 2 == 0 else "#fbfcfd"

            row = tk.Frame(self.rows_frame, bg=bg_row, height=54, highlightbackground="#f1f5f9", highlightthickness=1)
            row.pack(fill=tk.X)
            row.pack_propagate(False)

            # Cell 1: Client Name with Avatar Pill
            c1 = tk.Frame(row, bg=bg_row, width=self.col_widths["name"])
            c1.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c1.pack_propagate(False)

            avatar_text = (client["name"][:1] if client["name"] else "C").upper()
            avatar = tk.Label(c1, text=avatar_text, font=("Segoe UI", 9, "bold"), fg=C_TEAL_DARK, bg="#ccfbf1", width=2, height=1)
            avatar.pack(side=tk.LEFT, padx=(10, 10))

            clean_name = client["name"].lstrip("-~").strip()
            name_lbl = tk.Label(c1, text=clean_name if clean_name else client["name"], font=FONT_NAME, fg=C_TEXT_HERO, bg=bg_row, anchor=tk.W)
            name_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Cell 2: Phone Number (Modern High-Contrast Format)
            c2 = tk.Frame(row, bg=bg_row, width=self.col_widths["phone"])
            c2.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c2.pack_propagate(False)

            phone_lbl = tk.Label(c2, text=client["phone"], font=("Segoe UI Semibold", 9), fg="#0e7490", bg=bg_row, anchor=tk.W)
            phone_lbl.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

            # Cell 3: Status Pill Badge
            c3 = tk.Frame(row, bg=bg_row, width=self.col_widths["status"])
            c3.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c3.pack_propagate(False)

            st = client["status"].strip()
            style_info = STATUS_STYLES.get(st, {"fg": "#475569", "bg": "#f1f5f9", "dot": "●"})
            
            badge_wrap = tk.Frame(c3, bg=bg_row)
            badge_wrap.pack(side=tk.LEFT, padx=6)
            
            badge = tk.Label(
                badge_wrap,
                text=f"{style_info['dot']} {st}",
                font=FONT_BADGE,
                fg=style_info["fg"],
                bg=style_info["bg"],
                padx=10,
                pady=3
            )
            badge.pack(side=tk.LEFT)

            # Cell 4: Last Follow-up
            c4 = tk.Frame(row, bg=bg_row, width=self.col_widths["last"])
            c4.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c4.pack_propagate(False)

            last_f = client["last_followup"]
            last_lbl = tk.Label(c4, text=last_f, font=FONT_DATA, fg=C_TEXT_BODY if last_f != "-" else "#94a3b8", bg=bg_row, anchor=tk.W)
            last_lbl.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

            # Cell 5: Next Follow-up
            c5 = tk.Frame(row, bg=bg_row, width=self.col_widths["next"])
            c5.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c5.pack_propagate(False)

            next_f = client["next_followup"]
            next_lbl = tk.Label(c5, text=next_f, font=FONT_DATA, fg="#b45309" if next_f != "-" else "#94a3b8", bg=bg_row, anchor=tk.W)
            next_lbl.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

            # Cell 6: Notes Preview (Dynamically fills all remaining horizontal space)
            c6 = tk.Frame(row, bg=bg_row)
            c6.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

            notes_prev = client["notes"] if client["notes"] != "-" else "-"
            notes_fg = C_TEXT_BODY if client["notes"] != "-" else "#cbd5e1"
            notes_lbl = tk.Label(c6, text=notes_prev, font=FONT_DATA, fg=notes_fg, bg=bg_row, anchor=tk.W)
            notes_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

            # Cell 7: Minimalist Text Action Buttons (Manage & WhatsApp - Anchored Right)
            c7 = tk.Frame(row, bg=bg_row, width=self.col_widths["action"])
            c7.pack(side=tk.RIGHT, fill=tk.Y, padx=4)
            c7.pack_propagate(False)

            is_sent_today = self.is_whatsapp_sent_today(client)

            wa_bg = "#ecfdf5" if is_sent_today else "#f0fdf4"
            wa_fg = "#047857" if is_sent_today else "#15803d"
            wa_text = "Sent Today" if is_sent_today else "WhatsApp"

            wa_btn = tk.Button(
                c7,
                text=wa_text,
                font=("Segoe UI Semibold", 8),
                bg=wa_bg,
                fg=wa_fg,
                activebackground="#dcfce7",
                activeforeground="#15803d",
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda c=client: self.send_whatsapp_to_client(c)
            )
            wa_btn.pack(side=tk.LEFT, padx=(4, 4), pady=12)

            manage_btn = tk.Button(
                c7,
                text="Manage",
                font=("Segoe UI Semibold", 8),
                bg=C_TEAL_LIGHT,
                fg=C_TEAL_DARK,
                activebackground=C_TEAL_PRIMARY,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda c=client: self.open_note_modal(c)
            )
            manage_btn.pack(side=tk.LEFT, padx=(0, 4), pady=12)

            def _on_enter(e, r=row, ob=bg_row):
                r.config(bg=C_ROW_HOVER)

            def _on_leave(e, r=row, ob=bg_row):
                r.config(bg=ob)

            row.bind("<Enter>", _on_enter)
            row.bind("<Leave>", _on_leave)

            # Bind mousewheel to row and all children so cursor anywhere scrolls the canvas
            self.bind_smooth_wheel_recursive(row, self.canvas)

    def update_status_cards_ui(self):
        # Calculate dynamic counts for each category
        counts = {
            "All": len(self.all_clients),
            "New": 0,
            "Follow-up": 0,
            "Called": 0,
            "Interested": 0,
            "Closed": 0,
            "Lost": 0
        }

        for c in self.all_clients:
            st = c.get("status", "").strip().lower()
            if "new" in st:
                counts["New"] += 1
            elif "follow" in st:
                counts["Follow-up"] += 1
            elif "call" in st:
                counts["Called"] += 1
            elif "interest" in st:
                counts["Interested"] += 1
            elif "close" in st or "won" in st:
                counts["Closed"] += 1
            elif "lost" in st or "drop" in st:
                counts["Lost"] += 1
            else:
                counts["New"] += 1

        for s_key, widgets in self.status_card_widgets.items():
            cnt = counts.get(s_key, 0)
            widgets["count"].config(text=str(cnt))

            # Highlight selected card
            bg_target = widgets["bg_accent"] if s_key == self.active_status_filter else C_CARD
            border_target = widgets["color"] if s_key == self.active_status_filter else C_BORDER
            thick_target = 2 if s_key == self.active_status_filter else 1
            fg_title = widgets["color"] if s_key == self.active_status_filter else C_TEXT_BODY
            font_title = ("Segoe UI Bold", 9) if s_key == self.active_status_filter else ("Segoe UI Semibold", 9)
            fg_count = widgets["color"] if s_key == self.active_status_filter else C_TEXT_HERO

            widgets["frame"].config(bg=bg_target, highlightbackground=border_target, highlightthickness=thick_target)
            widgets["top_line"].config(bg=bg_target)
            widgets["dot"].config(bg=bg_target)
            widgets["title"].config(bg=bg_target, fg=fg_title, font=font_title)
            widgets["count"].config(bg=bg_target, fg=fg_count)

    def select_status_filter(self, status_key):
        self.active_status_filter = status_key
        self.apply_combined_filters()

    def on_search(self, event=None):
        self.apply_combined_filters()

    def apply_combined_filters(self):
        query = self.search_entry.get().strip().lower()
        has_query = query and query != "search clients by name, phone number, status, notes..."

        filtered = []
        for c in self.all_clients:
            # 1. Search Query check
            if has_query:
                matches_search = (
                    query in c["name"].lower() or 
                    query in c["phone"].lower() or 
                    query in c["phone"].replace(" ", "").replace("-", "") or 
                    query in c["status"].lower() or 
                    query in c["notes"].lower()
                )
                if not matches_search:
                    continue

            # 2. Status Card filter check
            if self.active_status_filter != "All":
                c_status = c.get("status", "").strip().lower()
                req_status = self.active_status_filter.lower()

                if req_status == "follow-up":
                    if "follow" not in c_status:
                        continue
                elif req_status == "closed":
                    if "close" not in c_status and "won" not in c_status:
                        continue
                elif req_status == "lost":
                    if "lost" not in c_status and "drop" not in c_status:
                        continue
                elif req_status not in c_status:
                    continue

            filtered.append(c)

        self.filtered_clients = filtered
        self.clients_limit = 25  # Reset to default limit on filter/search change
        self.render_clients_table()
        self.update_status_cards_ui()

    # =========================================================================
    # LEADS MANAGEMENT: ADD, EDIT, DELETE, STATUS UPDATE
    # =========================================================================
    def open_add_lead_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Add New Lead")
        modal.geometry("540x530")
        modal.minsize(480, 480)
        modal.config(bg="#ffffff")
        modal.transient(self)
        modal.grab_set()

        head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=22, pady=18)
        head.pack(fill=tk.X)
        tk.Label(head, text="Create New Lead", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(head, text="Enter client contact information and initial follow-up status", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(modal, bg="#ffffff", padx=24, pady=18)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text="Client Full Name *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        name_entry = tk.Entry(body, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        name_entry.pack(fill=tk.X, pady=(4, 10), ipady=4)

        tk.Label(body, text="Phone Number *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        phone_entry = tk.Entry(body, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        phone_entry.pack(fill=tk.X, pady=(4, 10), ipady=4)

        row_meta = tk.Frame(body, bg="#ffffff")
        row_meta.pack(fill=tk.X, pady=(0, 10))

        col_st = tk.Frame(row_meta, bg="#ffffff")
        col_st.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(col_st, text="Initial Status", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        status_cb = ttk.Combobox(col_st, values=["New", "Follow-up", "Called", "Interested", "Closed", "Lost"], font=FONT_DATA, state="readonly")
        status_cb.set("New")
        status_cb.pack(fill=tk.X, pady=(4, 0))

        col_dt = tk.Frame(row_meta, bg="#ffffff")
        col_dt.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))
        tk.Label(col_dt, text="Next Follow-up Date", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        next_entry = tk.Entry(col_dt, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        next_entry.pack(fill=tk.X, pady=(4, 0), ipady=3)

        tk.Label(body, text="Initial Discussion Notes:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        notes_txt = tk.Text(body, font=FONT_DATA, bg="#f8fafc", fg=C_TEXT_HERO, relief=tk.SOLID, bd=1, height=4, padx=10, pady=8)
        notes_txt.pack(fill=tk.BOTH, expand=True, pady=(4, 16))

        def _save_new_lead():
            lead_name = name_entry.get().strip()
            lead_phone = phone_entry.get().strip()
            if not lead_name or not lead_phone:
                messagebox.showwarning("Missing Fields", "Client ka Name aur Phone Number daalna zaroori hai.")
                return

            new_client = {
                "id": f"lead_{int(time.time()*1000)}_{lead_phone}",
                "sheet_row": None,
                "name": lead_name,
                "phone": lead_phone,
                "status": status_cb.get().strip() or "New",
                "last_followup": datetime.now().strftime("%Y-%m-%d"),
                "next_followup": next_entry.get().strip() or "-",
                "notes": notes_txt.get("1.0", tk.END).strip() or "-"
            }

            # 1. Update In-Memory & Local JSON Cache Immediately
            self.all_clients.insert(0, new_client)
            self.save_clients_data()
            self.apply_combined_filters()

            # 2. Asynchronously sync change to live Google Sheet
            self.sync_client_to_sheet_async("add", new_client)

            modal.destroy()
            messagebox.showinfo("Success", f"Lead '{lead_name}' successfully add ho gayi hai!")

        btn_bar = tk.Frame(body, bg="#ffffff")
        btn_bar.pack(fill=tk.X)

        create_btn = tk.Button(btn_bar, text="Add Lead", font=FONT_HEAD, bg=C_TEAL_PRIMARY, fg="#ffffff", activebackground=C_TEAL_DARK, relief=tk.FLAT, padx=20, pady=7, cursor="hand2", command=_save_new_lead)
        create_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(btn_bar, text="Cancel", font=FONT_DATA, bg="#f1f5f9", fg=C_TEXT_BODY, relief=tk.FLAT, padx=14, pady=7, cursor="hand2", command=modal.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=8)

    def delete_lead(self, client, modal=None):
        c_name = client.get("name", "Client")
        confirm = messagebox.askyesno("Confirm Delete", f"Kya aap sach me '{c_name}' ko delete karna chahte hain?")
        if confirm:
            if client in self.all_clients:
                self.all_clients.remove(client)
            if client in self.filtered_clients:
                self.filtered_clients.remove(client)
            
            # 1. Update In-Memory & Local JSON Cache Immediately
            self.save_clients_data()

            # 2. Remove from campaign log if exists
            c_key = self.get_client_key(client)
            if c_key in self.whatsapp_logs:
                del self.whatsapp_logs[c_key]
                self.save_whatsapp_logs()

            # 3. Asynchronously sync deletion to live Google Sheet
            self.sync_client_to_sheet_async("delete", client)

            self.apply_combined_filters()
            if modal:
                modal.destroy()
            messagebox.showinfo("Deleted", f"Lead '{c_name}' delete ho chuki hai.")

    def open_note_modal(self, client):
        client_name = client["name"]
        client_phone = client["phone"]
        client_status = client["status"].strip()
        client_last_f = client["last_followup"]
        client_next_f = client["next_followup"]
        current_notes = client["notes"]

        modal = tk.Toplevel(self)
        modal.title(f"Manage Lead — {client_name}")
        modal.geometry("560x540")
        modal.minsize(480, 480)
        modal.config(bg="#ffffff")
        modal.transient(self)
        modal.grab_set()

        m_head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=22, pady=16)
        m_head.pack(fill=tk.X)

        tk.Label(m_head, text=client_name, font=("Segoe UI", 14, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(m_head, text=f"Phone: {client_phone}  •  Status: {client_status}", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        m_body = tk.Frame(modal, bg="#ffffff", padx=24, pady=16)
        m_body.pack(fill=tk.BOTH, expand=True)

        # Edit Name & Phone row
        name_phone_row = tk.Frame(m_body, bg="#ffffff")
        name_phone_row.pack(fill=tk.X, pady=(0, 10))

        col_n = tk.Frame(name_phone_row, bg="#ffffff")
        col_n.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(col_n, text="Client Name:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        edit_name_entry = tk.Entry(col_n, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        edit_name_entry.pack(fill=tk.X, pady=(4, 0), ipady=3)
        edit_name_entry.insert(0, client_name)

        col_p = tk.Frame(name_phone_row, bg="#ffffff")
        col_p.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))
        tk.Label(col_p, text="Phone Number:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        edit_phone_entry = tk.Entry(col_p, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        edit_phone_entry.pack(fill=tk.X, pady=(4, 0), ipady=3)
        edit_phone_entry.insert(0, client_phone)

        # Status & Follow-up Row
        status_row = tk.Frame(m_body, bg="#ffffff")
        status_row.pack(fill=tk.X, pady=(0, 10))

        col_s = tk.Frame(status_row, bg="#ffffff")
        col_s.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(col_s, text="Update Status:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        status_combo = ttk.Combobox(col_s, values=["New", "Follow-up", "Called", "Interested", "Closed", "Lost"], font=FONT_DATA, state="readonly")
        status_combo.set(client_status if client_status else "New")
        status_combo.pack(fill=tk.X, pady=(4, 0))

        col_f = tk.Frame(status_row, bg="#ffffff")
        col_f.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))
        tk.Label(col_f, text="Next Follow-up Date:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        next_entry = tk.Entry(col_f, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        next_entry.pack(fill=tk.X, pady=(4, 0), ipady=3)
        next_entry.insert(0, client_next_f if client_next_f != "-" else "")

        tk.Label(m_body, text="Type Notes & Discussion Details:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        notes_text = tk.Text(m_body, font=FONT_DATA, bg="#f8fafc", fg=C_TEXT_HERO, relief=tk.SOLID, bd=1, height=5, padx=10, pady=8)
        notes_text.pack(fill=tk.BOTH, expand=True, pady=(4, 16))
        notes_text.insert(tk.END, current_notes if current_notes != "-" else "")

        def _save_notes():
            new_name = edit_name_entry.get().strip() or client_name
            new_phone = edit_phone_entry.get().strip() or client_phone
            new_status = status_combo.get().strip()
            new_next = next_entry.get().strip() or "-"
            new_notes = notes_text.get("1.0", tk.END).strip() or "-"

            # 1. Update client in memory & local JSON cache immediately
            client["name"] = new_name
            client["phone"] = new_phone
            client["status"] = new_status
            client["next_followup"] = new_next
            client["notes"] = new_notes

            self.save_clients_data()

            # 2. Asynchronously sync updates to live Google Sheet
            self.sync_client_to_sheet_async("update", client)

            # Re-render table rows & status counts
            self.apply_combined_filters()

            modal.destroy()
            messagebox.showinfo("Saved", f"Lead '{new_name}' updated successfully!")

        btn_bar = tk.Frame(m_body, bg="#ffffff")
        btn_bar.pack(fill=tk.X)

        # Delete Lead on Left
        delete_btn = tk.Button(
            btn_bar,
            text="Delete Lead",
            font=FONT_HEAD,
            bg="#fff1f2",
            fg="#e11d48",
            activebackground="#ffe4e6",
            activeforeground="#be123c",
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
            command=lambda: self.delete_lead(client, modal)
        )
        delete_btn.pack(side=tk.LEFT)

        save_btn = tk.Button(btn_bar, text="Save Changes", font=FONT_HEAD, bg=C_TEAL_PRIMARY, fg="#ffffff", activebackground=C_TEAL_DARK, activeforeground="#ffffff", relief=tk.FLAT, padx=20, pady=7, cursor="hand2", command=_save_notes)
        save_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(btn_bar, text="Cancel", font=FONT_DATA, bg="#f1f5f9", fg=C_TEXT_BODY, relief=tk.FLAT, padx=14, pady=7, cursor="hand2", command=modal.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=8)

    # =========================================================================
    # EMPLOYEE MANAGEMENT DATA LOGIC & UI (ADD, EDIT, DELETE, SEARCH, STATUS)
    # =========================================================================
    def load_employees_data(self):
        if os.path.exists(EMPLOYEES_FILE):
            try:
                with open(EMPLOYEES_FILE, "r", encoding="utf-8") as f:
                    self.all_employees = json.load(f)
            except Exception as e:
                print("Error loading employees vault:", e)
                self.all_employees = []
        else:
            # Default Starter Employees
            self.all_employees = [
                {
                    "id": "EMP-101",
                    "name": "Rohit Sharma",
                    "role": "Sales Lead",
                    "department": "Business Development",
                    "phone": "98212 02936",
                    "email": "rohit@smartbharattech.com",
                    "status": "Active",
                    "join_date": "2024-02-15",
                    "notes": "Handles key CRM conversions and client relationships."
                },
                {
                    "id": "EMP-102",
                    "name": "Punit Verma",
                    "role": "Operations Manager",
                    "department": "Operations",
                    "phone": "98910 75410",
                    "email": "punit@smartbharattech.com",
                    "status": "Active",
                    "join_date": "2024-03-01",
                    "notes": "Manages day-to-day business operations & WhatsApp workflow."
                },
                {
                    "id": "EMP-103",
                    "name": "Rajat Gupta",
                    "role": "Client Support Specialist",
                    "department": "Customer Success",
                    "phone": "93557 46709",
                    "email": "rajat@smartbharattech.com",
                    "status": "Active",
                    "join_date": "2024-04-10",
                    "notes": "Focuses on daily follow-ups, payment reminders, and onboarding."
                },
                {
                    "id": "EMP-104",
                    "name": "Aman Khan",
                    "role": "Marketing & Creative Lead",
                    "department": "Marketing",
                    "phone": "94040 85316",
                    "email": "aman@smartbharattech.com",
                    "status": "On Leave",
                    "join_date": "2024-05-20",
                    "notes": "Designs brand assets, posters, reels & campaign banners."
                }
            ]
            self.save_employees_data()

        self.filtered_employees = list(self.all_employees)

    def save_employees_data(self):
        try:
            with open(EMPLOYEES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.all_employees, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Error saving employees vault:", e)

    def build_employees_page(self, parent):
        # 1. STUDIO HEADER ROW: SEARCH BAR + ACTION TOOLBAR (+ Add Employee)
        top_bar = tk.Frame(parent, bg=C_CANVAS, height=56)
        top_bar.pack(fill=tk.X, padx=20, pady=(16, 12))
        top_bar.pack_propagate(False)

        # Search Bar
        search_card = tk.Frame(top_bar, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        search_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        search_wrap = tk.Frame(search_card, bg="#ffffff")
        search_wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        tk.Label(search_wrap, image=self.icons["search"], bg="#ffffff").pack(side=tk.LEFT, padx=(6, 8))

        self.emp_search_entry = tk.Entry(
            search_wrap,
            font=FONT_SEARCH,
            bg="#ffffff",
            fg=C_TEXT_HERO,
            insertbackground=C_TEAL_PRIMARY,
            relief=tk.FLAT,
            bd=0
        )
        self.emp_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, ipady=4)
        self.emp_search_entry.insert(0, "Search employees by name, role, department, phone or email...")
        self.emp_search_entry.config(fg=C_TEXT_MUTED)

        def _emp_s_in(e):
            if self.emp_search_entry.get() == "Search employees by name, role, department, phone or email...":
                self.emp_search_entry.delete(0, tk.END)
                self.emp_search_entry.config(fg=C_TEXT_HERO)

        def _emp_s_out(e):
            if not self.emp_search_entry.get().strip():
                self.emp_search_entry.insert(0, "Search employees by name, role, department, phone or email...")
                self.emp_search_entry.config(fg=C_TEXT_MUTED)

        self.emp_search_entry.bind("<FocusIn>", _emp_s_in)
        self.emp_search_entry.bind("<FocusOut>", _emp_s_out)
        self.emp_search_entry.bind("<KeyRelease>", lambda e: self.apply_employee_filters())

        # Action Buttons on Right (Floating Mor Pankh Copilot Button + Add New Employee)
        ai_logo_kw = {"image": self.mor_pankh_btn_photo} if self.mor_pankh_btn_photo else {"image": self.icons["ai"]}
        self.copilot_trigger_emp = tk.Button(
            top_bar,
            **ai_logo_kw,
            bg=C_CANVAS,
            activebackground=C_CANVAS,
            relief=tk.FLAT,
            bd=0,
            padx=0,
            pady=0,
            cursor="hand2",
            command=self.toggle_copilot_side_panel
        )
        if self.mor_pankh_btn_hover:
            self.copilot_trigger_emp.bind("<Enter>", lambda e: self.copilot_trigger_emp.config(image=self.mor_pankh_btn_hover))
            self.copilot_trigger_emp.bind("<Leave>", lambda e: self.copilot_trigger_emp.config(image=self.mor_pankh_btn_photo))
        self.copilot_trigger_emp.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 4))

        # + Add Employee Button
        add_emp_btn = tk.Button(
            top_bar,
            text="+ Add New Employee",
            font=("Segoe UI Semibold", 10),
            bg=C_TEAL_PRIMARY,
            fg="#ffffff",
            activebackground=C_TEAL_DARK,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.open_add_employee_modal
        )
        add_emp_btn.pack(side=tk.RIGHT, fill=tk.Y)

        # 2. STATUS QUICK-FILTER PILL STATS CARDS
        self.emp_filter_cards_bar = tk.Frame(parent, bg=C_CANVAS, height=64)
        self.emp_filter_cards_bar.pack(fill=tk.X, padx=20, pady=(0, 14))
        self.emp_filter_cards_bar.pack_propagate(False)

        self.emp_status_categories = [
            ("All", "All Staff", "#0e7490", "#e0f2fe"),
            ("Active", "Active", "#059669", "#ecfdf5"),
            ("On Leave", "On Leave", "#d97706", "#fef3c7"),
            ("Probation", "Probation", "#6366f1", "#eef2ff"),
            ("Inactive", "Inactive", "#e11d48", "#fff1f2")
        ]

        self.emp_status_card_widgets = {}
        for s_key, s_title, s_color, s_bg in self.emp_status_categories:
            card = tk.Frame(
                self.emp_filter_cards_bar,
                bg=C_CARD,
                highlightbackground="#e2e8f0",
                highlightthickness=1,
                padx=12,
                pady=8,
                cursor="hand2"
            )
            card.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)

            top_line = tk.Frame(card, bg=C_CARD)
            top_line.pack(fill=tk.X)

            dot = tk.Label(top_line, text="●", font=("Segoe UI", 9), fg=s_color, bg=C_CARD)
            dot.pack(side=tk.LEFT, padx=(0, 5))

            title_lbl = tk.Label(top_line, text=s_title, font=("Segoe UI Semibold", 9), fg="#64748b", bg=C_CARD)
            title_lbl.pack(side=tk.LEFT)

            count_lbl = tk.Label(card, text="0", font=("Segoe UI", 16, "bold"), fg=C_TEXT_HERO, bg=C_CARD, anchor=tk.W)
            count_lbl.pack(anchor=tk.W, pady=(3, 0))

            self.emp_status_card_widgets[s_key] = {
                "frame": card,
                "top_line": top_line,
                "dot": dot,
                "title": title_lbl,
                "count": count_lbl,
                "color": s_color,
                "bg_accent": s_bg
            }

            def _bind_emp_filter(key=s_key, widgets=[card, top_line, dot, title_lbl, count_lbl]):
                for w in widgets:
                    w.bind("<Button-1>", lambda e, k=key: self.select_emp_status_filter(k))

            _bind_emp_filter()

        # 3. MODERN EMPLOYEES TABLE CONTAINER
        self.emp_table_card = tk.Frame(parent, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        self.emp_table_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

        # Column Layout Widths
        self.emp_col_widths = {
            "name": 220,
            "role": 180,
            "department": 160,
            "contact": 220,
            "status": 120,
            "action": 150
        }

        # Table Header
        emp_hdr = tk.Frame(self.emp_table_card, bg="#f8fafc", height=42, highlightbackground=C_BORDER, highlightthickness=1)
        emp_hdr.pack(fill=tk.X)
        emp_hdr.pack_propagate(False)

        h_name = tk.Frame(emp_hdr, bg="#f8fafc", width=self.emp_col_widths["name"])
        h_name.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_name.pack_propagate(False)
        tk.Label(h_name, text="EMPLOYEE NAME", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=12)

        h_role = tk.Frame(emp_hdr, bg="#f8fafc", width=self.emp_col_widths["role"])
        h_role.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_role.pack_propagate(False)
        tk.Label(h_role, text="ROLE / POSITION", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_dept = tk.Frame(emp_hdr, bg="#f8fafc", width=self.emp_col_widths["department"])
        h_dept.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_dept.pack_propagate(False)
        tk.Label(h_dept, text="DEPARTMENT", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_cont = tk.Frame(emp_hdr, bg="#f8fafc", width=self.emp_col_widths["contact"])
        h_cont.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_cont.pack_propagate(False)
        tk.Label(h_cont, text="PHONE & EMAIL", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_stat = tk.Frame(emp_hdr, bg="#f8fafc", width=self.emp_col_widths["status"])
        h_stat.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_stat.pack_propagate(False)
        tk.Label(h_stat, text="STATUS", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_act = tk.Frame(emp_hdr, bg="#f8fafc", width=self.emp_col_widths["action"])
        h_act.pack(side=tk.RIGHT, fill=tk.Y, padx=4)
        h_act.pack_propagate(False)
        tk.Label(h_act, text="ACTIONS", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Scrollable rows stage (Zero-Smear Architecture)
        emp_canvas_wrap = tk.Frame(self.emp_table_card, bg="#ffffff")
        emp_canvas_wrap.pack(fill=tk.BOTH, expand=True)

        self.emp_canvas = tk.Canvas(emp_canvas_wrap, bg="#ffffff", bd=0, highlightthickness=0)
        self.emp_rows_frame = tk.Frame(self.emp_canvas, bg="#ffffff")
        self.emp_canvas_window = self.emp_canvas.create_window((0, 0), window=self.emp_rows_frame, anchor="nw")

        self.emp_vsb = ttk.Scrollbar(emp_canvas_wrap, orient="vertical")
        self.emp_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.emp_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.setup_zero_smear_scroll(self.emp_canvas, self.emp_canvas_window, self.emp_rows_frame, self.emp_vsb)

        self.refresh_employees_page()

    def select_emp_status_filter(self, key):
        self.active_emp_status_filter = key
        self.apply_employee_filters()

    def apply_employee_filters(self):
        q = self.emp_search_entry.get().strip().lower()
        has_query = q and q != "search employees by name, role, department, phone or email..."

        filtered = []
        for emp in self.all_employees:
            # Query match
            if has_query:
                phone_raw = emp.get("phone", "").lower().replace(" ", "").replace("-", "")
                matches = (
                    q in emp.get("name", "").lower() or
                    q in emp.get("role", "").lower() or
                    q in emp.get("department", "").lower() or
                    q in emp.get("phone", "").lower() or
                    q in phone_raw or
                    q in emp.get("email", "").lower() or
                    q in emp.get("id", "").lower() or
                    q in emp.get("notes", "").lower()
                )
                if not matches:
                    continue

            # Status match
            if self.active_emp_status_filter != "All":
                if emp.get("status", "").strip().lower() != self.active_emp_status_filter.lower():
                    continue

            filtered.append(emp)

        self.filtered_employees = filtered
        self.render_employees_table()
        self.update_emp_status_cards_ui()

    def update_emp_status_cards_ui(self):
        counts = {k: 0 for k, _, _, _ in self.emp_status_categories}
        counts["All"] = len(self.all_employees)

        for emp in self.all_employees:
            st = emp.get("status", "Active").strip()
            if st in counts:
                counts[st] += 1
            else:
                counts["Active"] += 1

        for s_key, widgets in self.emp_status_card_widgets.items():
            cnt = counts.get(s_key, 0)
            widgets["count"].config(text=str(cnt))

            bg_target = widgets["bg_accent"] if s_key == self.active_emp_status_filter else C_CARD
            border_target = widgets["color"] if s_key == self.active_emp_status_filter else C_BORDER
            thick_target = 2 if s_key == self.active_emp_status_filter else 1
            fg_title = widgets["color"] if s_key == self.active_emp_status_filter else C_TEXT_BODY
            font_title = ("Segoe UI Bold", 9) if s_key == self.active_emp_status_filter else ("Segoe UI Semibold", 9)
            fg_count = widgets["color"] if s_key == self.active_emp_status_filter else C_TEXT_HERO

            widgets["frame"].config(bg=bg_target, highlightbackground=border_target, highlightthickness=thick_target)
            widgets["top_line"].config(bg=bg_target)
            widgets["dot"].config(bg=bg_target)
            widgets["title"].config(bg=bg_target, fg=fg_title, font=font_title)
            widgets["count"].config(bg=bg_target, fg=fg_count)

    def refresh_employees_page(self):
        self.apply_employee_filters()

    def render_employees_table(self):
        for w in self.emp_rows_frame.winfo_children():
            w.destroy()

        if not self.filtered_employees:
            empty_box = tk.Frame(self.emp_rows_frame, bg="#ffffff", pady=60)
            empty_box.pack(fill=tk.BOTH, expand=True)
            tk.Label(empty_box, text="🔍 No employees found", font=("Segoe UI Semibold", 12), fg=C_TEXT_MUTED, bg="#ffffff").pack()
            tk.Label(empty_box, text="Try adjusting your search query or click '+ Add New Employee'.", font=FONT_DATA, fg="#94a3b8", bg="#ffffff").pack(pady=(4, 0))
            return

        status_colors = {
            "Active": {"fg": "#047857", "bg": "#ecfdf5", "dot": "●"},
            "On Leave": {"fg": "#b45309", "bg": "#fef3c7", "dot": "●"},
            "Probation": {"fg": "#4338ca", "bg": "#eef2ff", "dot": "●"},
            "Inactive": {"fg": "#be123c", "bg": "#fff1f2", "dot": "●"}
        }

        for idx, emp in enumerate(self.filtered_employees):
            bg_row = "#ffffff" if idx % 2 == 0 else "#fbfcfd"
            row = tk.Frame(self.emp_rows_frame, bg=bg_row, height=56, highlightbackground="#f1f5f9", highlightthickness=1)
            row.pack(fill=tk.X)
            row.pack_propagate(False)

            # Col 1: Avatar & Name
            c1 = tk.Frame(row, bg=bg_row, width=self.emp_col_widths["name"])
            c1.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c1.pack_propagate(False)

            av_char = (emp.get("name", "E")[:1] if emp.get("name") else "E").upper()
            avatar = tk.Label(c1, text=av_char, font=("Segoe UI", 9, "bold"), fg=C_TEAL_DARK, bg="#ccfbf1", width=2, height=1)
            avatar.pack(side=tk.LEFT, padx=(10, 10))

            info_b = tk.Frame(c1, bg=bg_row)
            info_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tk.Label(info_b, text=emp.get("name", "Employee"), font=FONT_NAME, fg=C_TEXT_HERO, bg=bg_row, anchor=tk.W).pack(anchor=tk.W)
            tk.Label(info_b, text=f"ID: {emp.get('id', '-')}", font=("Segoe UI", 8), fg="#94a3b8", bg=bg_row, anchor=tk.W).pack(anchor=tk.W)

            # Col 2: Role
            c2 = tk.Frame(row, bg=bg_row, width=self.emp_col_widths["role"])
            c2.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c2.pack_propagate(False)
            tk.Label(c2, text=emp.get("role", "-"), font=("Segoe UI Semibold", 9), fg=C_TEXT_HERO, bg=bg_row, anchor=tk.W).pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

            # Col 3: Department
            c3 = tk.Frame(row, bg=bg_row, width=self.emp_col_widths["department"])
            c3.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c3.pack_propagate(False)
            tk.Label(c3, text=emp.get("department", "-"), font=FONT_DATA, fg=C_TEXT_BODY, bg=bg_row, anchor=tk.W).pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

            # Col 4: Contact (Phone & Email)
            c4 = tk.Frame(row, bg=bg_row, width=self.emp_col_widths["contact"])
            c4.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c4.pack_propagate(False)
            c_info = tk.Frame(c4, bg=bg_row)
            c_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
            tk.Label(c_info, text=emp.get("phone", "-"), font=("Segoe UI Semibold", 8), fg="#0e7490", bg=bg_row, anchor=tk.W).pack(anchor=tk.W)
            tk.Label(c_info, text=emp.get("email", "-"), font=("Segoe UI", 8), fg="#64748b", bg=bg_row, anchor=tk.W).pack(anchor=tk.W)

            # Col 5: Status Badge
            c5 = tk.Frame(row, bg=bg_row, width=self.emp_col_widths["status"])
            c5.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c5.pack_propagate(False)
            st_val = emp.get("status", "Active")
            st_style = status_colors.get(st_val, {"fg": "#475569", "bg": "#f1f5f9", "dot": "●"})
            badge = tk.Label(c5, text=f"{st_style['dot']} {st_val}", font=FONT_BADGE, fg=st_style["fg"], bg=st_style["bg"], padx=10, pady=3)
            badge.pack(side=tk.LEFT, padx=6)

            # Col 6: Minimalist Text Action Buttons (Edit & Delete)
            c6 = tk.Frame(row, bg=bg_row, width=self.emp_col_widths["action"])
            c6.pack(side=tk.RIGHT, fill=tk.Y, padx=4)
            c6.pack_propagate(False)

            del_b = tk.Button(
                c6,
                text="Delete",
                font=("Segoe UI Semibold", 8),
                bg="#fff1f2",
                fg="#e11d48",
                activebackground="#ffe4e6",
                activeforeground="#be123c",
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda e=emp: self.delete_employee(e)
            )
            del_b.pack(side=tk.RIGHT, padx=(4, 8), pady=12)

            edit_b = tk.Button(
                c6,
                text="Edit",
                font=("Segoe UI Semibold", 8),
                bg=C_TEAL_LIGHT,
                fg=C_TEAL_DARK,
                activebackground=C_TEAL_PRIMARY,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                bd=0,
                padx=12,
                pady=4,
                cursor="hand2",
                command=lambda e=emp: self.open_edit_employee_modal(e)
            )
            edit_b.pack(side=tk.RIGHT, padx=(0, 4), pady=12)

            # Hover effect
            def _on_e(e, r=row):
                r.config(bg=C_ROW_HOVER)
            def _on_l(e, r=row, ob=bg_row):
                r.config(bg=ob)

            row.bind("<Enter>", _on_e)
            row.bind("<Leave>", _on_l)
            self.bind_smooth_wheel_recursive(row, self.emp_canvas)

    def open_add_employee_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Add New Employee")
        modal.geometry("540x560")
        modal.minsize(480, 500)
        modal.config(bg="#ffffff")
        modal.transient(self)
        modal.grab_set()

        head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=22, pady=18)
        head.pack(fill=tk.X)
        tk.Label(head, text="Add New Employee", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(head, text="Enter employee information, role, contact details and status", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(modal, bg="#ffffff", padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        # Name & ID
        r1 = tk.Frame(body, bg="#ffffff")
        r1.pack(fill=tk.X, pady=(0, 10))
        c_name = tk.Frame(r1, bg="#ffffff")
        c_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_name, text="Full Name *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        name_ent = tk.Entry(c_name, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        name_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)

        c_id = tk.Frame(r1, bg="#ffffff")
        c_id.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_id, text="Employee ID", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        auto_id = f"EMP-{len(self.all_employees) + 101}"
        id_ent = tk.Entry(c_id, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        id_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        id_ent.insert(0, auto_id)

        # Role & Department
        r2 = tk.Frame(body, bg="#ffffff")
        r2.pack(fill=tk.X, pady=(0, 10))
        c_role = tk.Frame(r2, bg="#ffffff")
        c_role.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_role, text="Role / Position *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        role_ent = tk.Entry(c_role, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        role_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)

        c_dept = tk.Frame(r2, bg="#ffffff")
        c_dept.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_dept, text="Department", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        dept_cb = ttk.Combobox(c_dept, values=["Sales & CRM", "Operations", "Customer Success", "Marketing", "Finance & Accounts", "IT & Tech", "Management"], font=FONT_DATA)
        dept_cb.set("Sales & CRM")
        dept_cb.pack(fill=tk.X, pady=(4, 0))

        # Phone & Email
        r3 = tk.Frame(body, bg="#ffffff")
        r3.pack(fill=tk.X, pady=(0, 10))
        c_ph = tk.Frame(r3, bg="#ffffff")
        c_ph.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_ph, text="Phone Number *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        ph_ent = tk.Entry(c_ph, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        ph_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)

        c_em = tk.Frame(r3, bg="#ffffff")
        c_em.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_em, text="Work Email", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        em_ent = tk.Entry(c_em, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        em_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)

        # Status & Join Date
        r4 = tk.Frame(body, bg="#ffffff")
        r4.pack(fill=tk.X, pady=(0, 10))
        c_st = tk.Frame(r4, bg="#ffffff")
        c_st.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_st, text="Status", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        st_cb = ttk.Combobox(c_st, values=["Active", "On Leave", "Probation", "Inactive"], font=FONT_DATA, state="readonly")
        st_cb.set("Active")
        st_cb.pack(fill=tk.X, pady=(4, 0))

        c_jd = tk.Frame(r4, bg="#ffffff")
        c_jd.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_jd, text="Joining Date", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        jd_ent = tk.Entry(c_jd, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        jd_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        jd_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Notes
        tk.Label(body, text="Notes & Responsibilities:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        notes_box = tk.Text(body, font=FONT_DATA, bg="#f8fafc", fg=C_TEXT_HERO, relief=tk.SOLID, bd=1, height=4, padx=10, pady=8)
        notes_box.pack(fill=tk.BOTH, expand=True, pady=(4, 16))

        def _save_emp():
            emp_name = name_ent.get().strip()
            emp_role = role_ent.get().strip()
            emp_phone = ph_ent.get().strip()
            if not emp_name or not emp_role or not emp_phone:
                messagebox.showwarning("Missing Fields", "Employee Name, Role aur Phone number daalna zaroori hai.")
                return

            new_emp = {
                "id": id_ent.get().strip() or f"EMP-{len(self.all_employees)+101}",
                "name": emp_name,
                "role": emp_role,
                "department": dept_cb.get().strip() or "General",
                "phone": emp_phone,
                "email": em_ent.get().strip(),
                "status": st_cb.get().strip() or "Active",
                "join_date": jd_ent.get().strip() or datetime.now().strftime("%Y-%m-%d"),
                "notes": notes_box.get("1.0", tk.END).strip() or "-"
            }

            self.all_employees.insert(0, new_emp)
            self.save_employees_data()
            self.apply_employee_filters()
            modal.destroy()
            messagebox.showinfo("Success", f"Employee '{emp_name}' successfully add ho gaya!")

        # Action Buttons
        btn_bar = tk.Frame(body, bg="#ffffff")
        btn_bar.pack(fill=tk.X)

        create_btn = tk.Button(btn_bar, text="Add Employee", font=FONT_HEAD, bg=C_TEAL_PRIMARY, fg="#ffffff", activebackground=C_TEAL_DARK, relief=tk.FLAT, padx=20, pady=7, cursor="hand2", command=_save_emp)
        create_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(btn_bar, text="Cancel", font=FONT_DATA, bg="#f1f5f9", fg=C_TEXT_BODY, relief=tk.FLAT, padx=14, pady=7, cursor="hand2", command=modal.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=8)

    def open_edit_employee_modal(self, emp):
        modal = tk.Toplevel(self)
        modal.title(f"Edit Employee — {emp.get('name')}")
        modal.geometry("540x560")
        modal.minsize(480, 500)
        modal.config(bg="#ffffff")
        modal.transient(self)
        modal.grab_set()

        head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=22, pady=18)
        head.pack(fill=tk.X)
        tk.Label(head, text=f"Edit Employee — {emp.get('name')}", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(head, text=f"Update employee credentials, role, status and department", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(modal, bg="#ffffff", padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        # Name & ID
        r1 = tk.Frame(body, bg="#ffffff")
        r1.pack(fill=tk.X, pady=(0, 10))
        c_name = tk.Frame(r1, bg="#ffffff")
        c_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_name, text="Full Name *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        name_ent = tk.Entry(c_name, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        name_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        name_ent.insert(0, emp.get("name", ""))

        c_id = tk.Frame(r1, bg="#ffffff")
        c_id.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_id, text="Employee ID", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        id_ent = tk.Entry(c_id, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        id_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        id_ent.insert(0, emp.get("id", ""))

        # Role & Department
        r2 = tk.Frame(body, bg="#ffffff")
        r2.pack(fill=tk.X, pady=(0, 10))
        c_role = tk.Frame(r2, bg="#ffffff")
        c_role.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_role, text="Role / Position *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        role_ent = tk.Entry(c_role, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        role_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        role_ent.insert(0, emp.get("role", ""))

        c_dept = tk.Frame(r2, bg="#ffffff")
        c_dept.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_dept, text="Department", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        dept_cb = ttk.Combobox(c_dept, values=["Sales & CRM", "Operations", "Customer Success", "Marketing", "Finance & Accounts", "IT & Tech", "Management"], font=FONT_DATA)
        dept_cb.set(emp.get("department", "Sales & CRM"))
        dept_cb.pack(fill=tk.X, pady=(4, 0))

        # Phone & Email
        r3 = tk.Frame(body, bg="#ffffff")
        r3.pack(fill=tk.X, pady=(0, 10))
        c_ph = tk.Frame(r3, bg="#ffffff")
        c_ph.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_ph, text="Phone Number *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        ph_ent = tk.Entry(c_ph, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        ph_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        ph_ent.insert(0, emp.get("phone", ""))

        c_em = tk.Frame(r3, bg="#ffffff")
        c_em.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_em, text="Work Email", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        em_ent = tk.Entry(c_em, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        em_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        em_ent.insert(0, emp.get("email", ""))

        # Status & Join Date
        r4 = tk.Frame(body, bg="#ffffff")
        r4.pack(fill=tk.X, pady=(0, 10))
        c_st = tk.Frame(r4, bg="#ffffff")
        c_st.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_st, text="Status", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        st_cb = ttk.Combobox(c_st, values=["Active", "On Leave", "Probation", "Inactive"], font=FONT_DATA, state="readonly")
        st_cb.set(emp.get("status", "Active"))
        st_cb.pack(fill=tk.X, pady=(4, 0))

        c_jd = tk.Frame(r4, bg="#ffffff")
        c_jd.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_jd, text="Joining Date", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        jd_ent = tk.Entry(c_jd, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        jd_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        jd_ent.insert(0, emp.get("join_date", datetime.now().strftime("%Y-%m-%d")))

        # Notes
        tk.Label(body, text="Notes & Responsibilities:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        notes_box = tk.Text(body, font=FONT_DATA, bg="#f8fafc", fg=C_TEXT_HERO, relief=tk.SOLID, bd=1, height=4, padx=10, pady=8)
        notes_box.pack(fill=tk.BOTH, expand=True, pady=(4, 16))
        notes_box.insert(tk.END, emp.get("notes", ""))

        def _save_changes():
            emp_name = name_ent.get().strip()
            emp_role = role_ent.get().strip()
            emp_phone = ph_ent.get().strip()
            if not emp_name or not emp_role or not emp_phone:
                messagebox.showwarning("Missing Fields", "Employee Name, Role aur Phone number daalna zaroori hai.")
                return

            emp["id"] = id_ent.get().strip() or emp.get("id", "EMP-000")
            emp["name"] = emp_name
            emp["role"] = emp_role
            emp["department"] = dept_cb.get().strip() or "General"
            emp["phone"] = emp_phone
            emp["email"] = em_ent.get().strip()
            emp["status"] = st_cb.get().strip() or "Active"
            emp["join_date"] = jd_ent.get().strip()
            emp["notes"] = notes_box.get("1.0", tk.END).strip() or "-"

            self.save_employees_data()
            self.apply_employee_filters()
            modal.destroy()
            messagebox.showinfo("Saved", f"Employee '{emp_name}' updated successfully!")

        # Action Buttons
        btn_bar = tk.Frame(body, bg="#ffffff")
        btn_bar.pack(fill=tk.X)

        del_b = tk.Button(
            btn_bar,
            text="Delete Employee",
            font=FONT_DATA,
            bg="#fff1f2",
            fg="#e11d48",
            activebackground="#ffe4e6",
            activeforeground="#be123c",
            relief=tk.FLAT,
            padx=14,
            pady=7,
            cursor="hand2",
            command=lambda: [modal.destroy(), self.delete_employee(emp)]
        )
        del_b.pack(side=tk.LEFT)

        save_btn = tk.Button(btn_bar, text="Save Changes", font=FONT_HEAD, bg=C_TEAL_PRIMARY, fg="#ffffff", activebackground=C_TEAL_DARK, relief=tk.FLAT, padx=20, pady=7, cursor="hand2", command=_save_changes)
        save_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(btn_bar, text="Cancel", font=FONT_DATA, bg="#f1f5f9", fg=C_TEXT_BODY, relief=tk.FLAT, padx=14, pady=7, cursor="hand2", command=modal.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=8)

    def delete_employee(self, emp):
        e_name = emp.get("name", "Employee")
        confirm = messagebox.askyesno("Confirm Delete", f"Kya aap sach me employee '{e_name}' ko delete karna chahte hain?")
        if confirm:
            if emp in self.all_employees:
                self.all_employees.remove(emp)
            if emp in self.filtered_employees:
                self.filtered_employees.remove(emp)
            self.save_employees_data()
            self.apply_employee_filters()
            messagebox.showinfo("Deleted", f"Employee '{e_name}' delete ho chuka hai.")

    # =========================================================================
    # TASK MANAGEMENT DATA LOGIC & UI (ADD, EDIT, DELETE, SEARCH, STATUS, FOLLOW-UPS VIA CALL & WA)
    # =========================================================================
    def load_tasks_data(self):
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, "r", encoding="utf-8") as f:
                    self.all_tasks = json.load(f)
            except Exception as e:
                print("Error loading tasks vault:", e)
                self.all_tasks = []
        else:
            # Starter sample tasks tailored for business operations
            self.all_tasks = [
                {
                    "id": "TSK-201",
                    "title": "Payment Follow-up for Invoice #489",
                    "client_name": "Rajesh Kumar",
                    "phone": "98910 75410",
                    "type": "Payment Collection",
                    "due_date": datetime.now().strftime("%Y-%m-%d"),
                    "priority": "High",
                    "status": "Pending",
                    "assigned_to": "Rohit Sharma",
                    "notes": "Follow-up for pending milestone payment of Rs 15,000."
                },
                {
                    "id": "TSK-202",
                    "title": "Service Demo & Software Pitch Call",
                    "client_name": "Webspool Private Limited",
                    "phone": "93557 46709",
                    "type": "Calling Follow-up",
                    "due_date": datetime.now().strftime("%Y-%m-%d"),
                    "priority": "Urgent",
                    "status": "In Progress",
                    "assigned_to": "Rajat Gupta",
                    "notes": "Explain CRM automation & WhatsApp campaigns over phone call."
                },
                {
                    "id": "TSK-203",
                    "title": "Send Promotional Catalog on WhatsApp",
                    "client_name": "Kavya Traders",
                    "phone": "94040 85316",
                    "type": "WhatsApp Follow-up",
                    "due_date": datetime.now().strftime("%Y-%m-%d"),
                    "priority": "Normal",
                    "status": "Pending",
                    "assigned_to": "Punit Verma",
                    "notes": "Share the updated festive product catalog and pricing sheet."
                },
                {
                    "id": "TSK-204",
                    "title": "Contract Renewal & Final Sign-off",
                    "client_name": "Aman Enterprises",
                    "phone": "98212 02936",
                    "type": "Calling Follow-up",
                    "due_date": "2026-11-12",
                    "priority": "High",
                    "status": "Completed",
                    "assigned_to": "Rohit Sharma",
                    "notes": "Client agreed to annual maintenance contract."
                }
            ]
            self.save_tasks_data()

        self.filtered_tasks = list(self.all_tasks)

    def save_tasks_data(self):
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.all_tasks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Error saving tasks vault:", e)

    def build_tasks_page(self, parent):
        # 1. STUDIO HEADER ROW: SEARCH BAR + ACTION TOOLBAR (+ Add Task)
        top_bar = tk.Frame(parent, bg=C_CANVAS, height=56)
        top_bar.pack(fill=tk.X, padx=20, pady=(16, 12))
        top_bar.pack_propagate(False)

        search_card = tk.Frame(top_bar, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        search_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        search_wrap = tk.Frame(search_card, bg="#ffffff")
        search_wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        tk.Label(search_wrap, image=self.icons["search"], bg="#ffffff").pack(side=tk.LEFT, padx=(6, 8))

        self.task_search_entry = tk.Entry(
            search_wrap,
            font=FONT_SEARCH,
            bg="#ffffff",
            fg=C_TEXT_HERO,
            insertbackground=C_TEAL_PRIMARY,
            relief=tk.FLAT,
            bd=0
        )
        self.task_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, ipady=4)
        self.task_search_entry.insert(0, "Search tasks by title, client, phone, assignee or notes...")
        self.task_search_entry.config(fg=C_TEXT_MUTED)

        def _task_s_in(e):
            if self.task_search_entry.get() == "Search tasks by title, client, phone, assignee or notes...":
                self.task_search_entry.delete(0, tk.END)
                self.task_search_entry.config(fg=C_TEXT_HERO)

        def _task_s_out(e):
            if not self.task_search_entry.get().strip():
                self.task_search_entry.insert(0, "Search tasks by title, client, phone, assignee or notes...")
                self.task_search_entry.config(fg=C_TEXT_MUTED)

        self.task_search_entry.bind("<FocusIn>", _task_s_in)
        self.task_search_entry.bind("<FocusOut>", _task_s_out)
        self.task_search_entry.bind("<KeyRelease>", lambda e: self.apply_task_filters())

        # Action Buttons on Right (Floating Mor Pankh Copilot Button + Add New Task)
        ai_logo_kw = {"image": self.mor_pankh_btn_photo} if self.mor_pankh_btn_photo else {"image": self.icons["ai"]}
        self.copilot_trigger_tasks = tk.Button(
            top_bar,
            **ai_logo_kw,
            bg=C_CANVAS,
            activebackground=C_CANVAS,
            relief=tk.FLAT,
            bd=0,
            padx=0,
            pady=0,
            cursor="hand2",
            command=self.toggle_copilot_side_panel
        )
        if self.mor_pankh_btn_hover:
            self.copilot_trigger_tasks.bind("<Enter>", lambda e: self.copilot_trigger_tasks.config(image=self.mor_pankh_btn_hover))
            self.copilot_trigger_tasks.bind("<Leave>", lambda e: self.copilot_trigger_tasks.config(image=self.mor_pankh_btn_photo))
        self.copilot_trigger_tasks.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 4))

        # + Add Task Button
        add_task_btn = tk.Button(
            top_bar,
            text="+ Add New Task",
            font=("Segoe UI Semibold", 10),
            bg=C_TEAL_PRIMARY,
            fg="#ffffff",
            activebackground=C_TEAL_DARK,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.open_add_task_modal
        )
        add_task_btn.pack(side=tk.RIGHT, fill=tk.Y)

        # 2. STATUS QUICK-FILTER PILL STATS CARDS
        self.task_filter_cards_bar = tk.Frame(parent, bg=C_CANVAS, height=64)
        self.task_filter_cards_bar.pack(fill=tk.X, padx=20, pady=(0, 14))
        self.task_filter_cards_bar.pack_propagate(False)

        self.task_status_categories = [
            ("All", "All Tasks", "#0e7490", "#e0f2fe"),
            ("Pending", "Pending", "#d97706", "#fef3c7"),
            ("In Progress", "In Progress", "#6366f1", "#eef2ff"),
            ("Urgent", "Urgent / Due", "#e11d48", "#fff1f2"),
            ("Completed", "Completed", "#059669", "#ecfdf5")
        ]

        self.task_status_card_widgets = {}
        for s_key, s_title, s_color, s_bg in self.task_status_categories:
            card = tk.Frame(
                self.task_filter_cards_bar,
                bg=C_CARD,
                highlightbackground="#e2e8f0",
                highlightthickness=1,
                padx=12,
                pady=8,
                cursor="hand2"
            )
            card.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)

            top_line = tk.Frame(card, bg=C_CARD)
            top_line.pack(fill=tk.X)

            dot = tk.Label(top_line, text="●", font=("Segoe UI", 9), fg=s_color, bg=C_CARD)
            dot.pack(side=tk.LEFT, padx=(0, 5))

            title_lbl = tk.Label(top_line, text=s_title, font=("Segoe UI Semibold", 9), fg="#64748b", bg=C_CARD)
            title_lbl.pack(side=tk.LEFT)

            count_lbl = tk.Label(card, text="0", font=("Segoe UI", 16, "bold"), fg=C_TEXT_HERO, bg=C_CARD, anchor=tk.W)
            count_lbl.pack(anchor=tk.W, pady=(3, 0))

            self.task_status_card_widgets[s_key] = {
                "frame": card,
                "top_line": top_line,
                "dot": dot,
                "title": title_lbl,
                "count": count_lbl,
                "color": s_color,
                "bg_accent": s_bg
            }

            def _bind_task_filter(key=s_key, widgets=[card, top_line, dot, title_lbl, count_lbl]):
                for w in widgets:
                    w.bind("<Button-1>", lambda e, k=key: self.select_task_status_filter(k))

            _bind_task_filter()

        # 3. MODERN TASKS TABLE CONTAINER
        self.task_table_card = tk.Frame(parent, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        self.task_table_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

        # Column Layout Widths
        self.task_col_widths = {
            "title": 260,
            "client": 170,
            "type": 130,
            "due": 110,
            "status": 110,
            "action": 280
        }

        # Table Header
        task_hdr = tk.Frame(self.task_table_card, bg="#f8fafc", height=42, highlightbackground=C_BORDER, highlightthickness=1)
        task_hdr.pack(fill=tk.X)
        task_hdr.pack_propagate(False)

        h_title = tk.Frame(task_hdr, bg="#f8fafc", width=self.task_col_widths["title"])
        h_title.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_title.pack_propagate(False)
        tk.Label(h_title, text="TASK TITLE & DETAILS", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=12)

        h_client = tk.Frame(task_hdr, bg="#f8fafc", width=self.task_col_widths["client"])
        h_client.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_client.pack_propagate(False)
        tk.Label(h_client, text="CONTACT / CLIENT", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_type = tk.Frame(task_hdr, bg="#f8fafc", width=self.task_col_widths["type"])
        h_type.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_type.pack_propagate(False)
        tk.Label(h_type, text="TASK TYPE", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_due = tk.Frame(task_hdr, bg="#f8fafc", width=self.task_col_widths["due"])
        h_due.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_due.pack_propagate(False)
        tk.Label(h_due, text="DUE DATE", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_stat = tk.Frame(task_hdr, bg="#f8fafc", width=self.task_col_widths["status"])
        h_stat.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_stat.pack_propagate(False)
        tk.Label(h_stat, text="STATUS", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_act = tk.Frame(task_hdr, bg="#f8fafc", width=self.task_col_widths["action"])
        h_act.pack(side=tk.RIGHT, fill=tk.Y, padx=4)
        h_act.pack_propagate(False)
        tk.Label(h_act, text="FOLLOW-UP ACTIONS (CALL & WA)", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Scrollable rows stage (Zero-Smear Architecture)
        task_canvas_wrap = tk.Frame(self.task_table_card, bg="#ffffff")
        task_canvas_wrap.pack(fill=tk.BOTH, expand=True)

        self.task_canvas = tk.Canvas(task_canvas_wrap, bg="#ffffff", bd=0, highlightthickness=0)
        self.task_rows_frame = tk.Frame(self.task_canvas, bg="#ffffff")
        self.task_canvas_window = self.task_canvas.create_window((0, 0), window=self.task_rows_frame, anchor="nw")

        self.task_vsb = ttk.Scrollbar(task_canvas_wrap, orient="vertical")
        self.task_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.task_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.setup_zero_smear_scroll(self.task_canvas, self.task_canvas_window, self.task_rows_frame, self.task_vsb)

        self.refresh_tasks_page()

    def select_task_status_filter(self, key):
        self.active_task_status_filter = key
        self.apply_task_filters()

    def apply_task_filters(self):
        q = self.task_search_entry.get().strip().lower()
        has_query = q and q != "search tasks by title, client, phone, assignee or notes..."

        filtered = []
        for t in self.all_tasks:
            # Query filter
            if has_query:
                phone_raw = t.get("phone", "").lower().replace(" ", "").replace("-", "")
                matches = (
                    q in t.get("title", "").lower() or
                    q in t.get("client_name", "").lower() or
                    q in t.get("phone", "").lower() or
                    q in phone_raw or
                    q in t.get("type", "").lower() or
                    q in t.get("assigned_to", "").lower() or
                    q in t.get("priority", "").lower() or
                    q in t.get("id", "").lower() or
                    q in t.get("notes", "").lower()
                )
                if not matches:
                    continue

            # Status card filter
            if self.active_task_status_filter != "All":
                if self.active_task_status_filter == "Urgent":
                    if t.get("priority") != "Urgent" and t.get("status") != "Urgent":
                        continue
                elif t.get("status", "").strip().lower() != self.active_task_status_filter.lower():
                    continue

            filtered.append(t)

        self.filtered_tasks = filtered
        self.render_tasks_table()
        self.update_task_status_cards_ui()

    def update_task_status_cards_ui(self):
        counts = {k: 0 for k, _, _, _ in self.task_status_categories}
        counts["All"] = len(self.all_tasks)

        for t in self.all_tasks:
            st = t.get("status", "Pending").strip()
            pr = t.get("priority", "Normal").strip()
            if pr == "Urgent":
                counts["Urgent"] += 1
            if st in counts:
                counts[st] += 1
            else:
                counts["Pending"] += 1

        for s_key, widgets in self.task_status_card_widgets.items():
            cnt = counts.get(s_key, 0)
            widgets["count"].config(text=str(cnt))

            bg_target = widgets["bg_accent"] if s_key == self.active_task_status_filter else C_CARD
            border_target = widgets["color"] if s_key == self.active_task_status_filter else C_BORDER
            thick_target = 2 if s_key == self.active_task_status_filter else 1
            fg_title = widgets["color"] if s_key == self.active_task_status_filter else C_TEXT_BODY
            font_title = ("Segoe UI Bold", 9) if s_key == self.active_task_status_filter else ("Segoe UI Semibold", 9)
            fg_count = widgets["color"] if s_key == self.active_task_status_filter else C_TEXT_HERO

            widgets["frame"].config(bg=bg_target, highlightbackground=border_target, highlightthickness=thick_target)
            widgets["top_line"].config(bg=bg_target)
            widgets["dot"].config(bg=bg_target)
            widgets["title"].config(bg=bg_target, fg=fg_title, font=font_title)
            widgets["count"].config(bg=bg_target, fg=fg_count)

    def refresh_tasks_page(self):
        self.apply_task_filters()

    def render_tasks_table(self):
        for w in self.task_rows_frame.winfo_children():
            w.destroy()

        if not self.filtered_tasks:
            empty_box = tk.Frame(self.task_rows_frame, bg="#ffffff", pady=60)
            empty_box.pack(fill=tk.BOTH, expand=True)
            tk.Label(empty_box, text="🔍 No tasks found", font=("Segoe UI Semibold", 12), fg=C_TEXT_MUTED, bg="#ffffff").pack()
            tk.Label(empty_box, text="Try adjusting your search query or click '+ Add New Task'.", font=FONT_DATA, fg="#94a3b8", bg="#ffffff").pack(pady=(4, 0))
            return

        status_colors = {
            "Pending": {"fg": "#b45309", "bg": "#fef3c7", "dot": "●"},
            "In Progress": {"fg": "#4338ca", "bg": "#eef2ff", "dot": "●"},
            "Completed": {"fg": "#047857", "bg": "#ecfdf5", "dot": "●"},
            "Cancelled": {"fg": "#be123c", "bg": "#fff1f2", "dot": "●"}
        }

        priority_colors = {
            "Urgent": {"fg": "#be123c", "bg": "#ffe4e6"},
            "High": {"fg": "#c2410c", "bg": "#ffedd5"},
            "Normal": {"fg": "#0e7490", "bg": "#e0f2fe"},
            "Low": {"fg": "#64748b", "bg": "#f1f5f9"}
        }

        for idx, task in enumerate(self.filtered_tasks):
            bg_row = "#ffffff" if idx % 2 == 0 else "#fbfcfd"
            row = tk.Frame(self.task_rows_frame, bg=bg_row, height=58, highlightbackground="#f1f5f9", highlightthickness=1)
            row.pack(fill=tk.X)
            row.pack_propagate(False)

            # Col 1: Title + Priority + ID
            c1 = tk.Frame(row, bg=bg_row, width=self.task_col_widths["title"])
            c1.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c1.pack_propagate(False)

            info_b = tk.Frame(c1, bg=bg_row)
            info_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=6)

            title_row = tk.Frame(info_b, bg=bg_row)
            title_row.pack(fill=tk.X)

            pr_val = task.get("priority", "Normal")
            pr_style = priority_colors.get(pr_val, priority_colors["Normal"])
            tk.Label(title_row, text=pr_val, font=("Segoe UI Bold", 7), fg=pr_style["fg"], bg=pr_style["bg"], padx=4, pady=1).pack(side=tk.LEFT, padx=(0, 6))

            t_title = task.get("title", "Task")
            if len(t_title) > 32:
                t_title = t_title[:30] + "..."
            tk.Label(title_row, text=t_title, font=FONT_NAME, fg=C_TEXT_HERO, bg=bg_row, anchor=tk.W).pack(side=tk.LEFT)

            sub_txt = f"{task.get('id', '-')}  •  Assigned: {task.get('assigned_to', 'Unassigned')}"
            tk.Label(info_b, text=sub_txt, font=("Segoe UI", 8), fg="#94a3b8", bg=bg_row, anchor=tk.W).pack(anchor=tk.W, pady=(2, 0))

            # Col 2: Client & Phone
            c2 = tk.Frame(row, bg=bg_row, width=self.task_col_widths["client"])
            c2.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c2.pack_propagate(False)
            cl_info = tk.Frame(c2, bg=bg_row)
            cl_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
            tk.Label(cl_info, text=task.get("client_name", "-"), font=("Segoe UI Semibold", 9), fg=C_TEXT_HERO, bg=bg_row, anchor=tk.W).pack(anchor=tk.W)
            tk.Label(cl_info, text=task.get("phone", "-"), font=("Segoe UI", 8), fg="#0e7490", bg=bg_row, anchor=tk.W).pack(anchor=tk.W)

            # Col 3: Task Type
            c3 = tk.Frame(row, bg=bg_row, width=self.task_col_widths["type"])
            c3.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c3.pack_propagate(False)
            tk.Label(c3, text=task.get("type", "General"), font=FONT_DATA, fg="#475569", bg=bg_row, anchor=tk.W).pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

            # Col 4: Due Date
            c4 = tk.Frame(row, bg=bg_row, width=self.task_col_widths["due"])
            c4.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c4.pack_propagate(False)
            due_d = task.get("due_date", "-")
            today_str = datetime.now().strftime("%Y-%m-%d")
            due_fg = "#e11d48" if due_d == today_str else C_TEXT_BODY
            tk.Label(c4, text=due_d, font=("Segoe UI Semibold", 9), fg=due_fg, bg=bg_row, anchor=tk.W).pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

            # Col 5: Status Badge
            c5 = tk.Frame(row, bg=bg_row, width=self.task_col_widths["status"])
            c5.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c5.pack_propagate(False)
            st_val = task.get("status", "Pending")
            st_style = status_colors.get(st_val, {"fg": "#475569", "bg": "#f1f5f9", "dot": "●"})
            badge = tk.Label(c5, text=f"{st_style['dot']} {st_val}", font=FONT_BADGE, fg=st_style["fg"], bg=st_style["bg"], padx=8, pady=3)
            badge.pack(side=tk.LEFT, padx=6)

            # Col 6: Follow-up Actions (Call, WhatsApp, Edit, Delete)
            c6 = tk.Frame(row, bg=bg_row, width=self.task_col_widths["action"])
            c6.pack(side=tk.RIGHT, fill=tk.Y, padx=4)
            c6.pack_propagate(False)

            # Quick Call Button
            call_btn = tk.Button(
                c6,
                text="Call",
                font=("Segoe UI Semibold", 8),
                bg="#e0f2fe",
                fg="#0369a1",
                activebackground="#bae6fd",
                activeforeground="#0284c7",
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda t=task: self.execute_task_call(t)
            )
            call_btn.pack(side=tk.LEFT, padx=(4, 3), pady=12)

            # Quick WhatsApp Button
            wa_btn = tk.Button(
                c6,
                text="WhatsApp",
                font=("Segoe UI Semibold", 8),
                bg="#ecfdf5",
                fg="#047857",
                activebackground="#d1fae5",
                activeforeground="#059669",
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda t=task: self.execute_task_whatsapp(t)
            )
            wa_btn.pack(side=tk.LEFT, padx=3, pady=12)

            # Edit Button
            edit_btn = tk.Button(
                c6,
                text="Edit",
                font=("Segoe UI Semibold", 8),
                bg=C_TEAL_LIGHT,
                fg=C_TEAL_DARK,
                activebackground=C_TEAL_PRIMARY,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda t=task: self.open_edit_task_modal(t)
            )
            edit_btn.pack(side=tk.LEFT, padx=3, pady=12)

            # Delete Button
            del_btn = tk.Button(
                c6,
                text="Delete",
                font=("Segoe UI Semibold", 8),
                bg="#fff1f2",
                fg="#e11d48",
                activebackground="#ffe4e6",
                activeforeground="#be123c",
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda t=task: self.delete_task(t)
            )
            del_btn.pack(side=tk.LEFT, padx=(3, 6), pady=12)

            def _on_e(e, r=row):
                r.config(bg=C_ROW_HOVER)
            def _on_l(e, r=row, ob=bg_row):
                r.config(bg=ob)

            row.bind("<Enter>", _on_e)
            row.bind("<Leave>", _on_l)
            self.bind_smooth_wheel_recursive(row, self.task_canvas)

    def execute_task_call(self, task):
        phone = task.get("phone", "").strip()
        name = task.get("client_name", "Client")
        clean_digits = "".join(filter(str.isdigit, phone))
        if not clean_digits:
            messagebox.showwarning("Invalid Phone", f"Task '{task.get('title')}' me phone number available nahi hai.")
            return

        # Trigger native tel protocol or show call modal
        tel_url = f"tel:{clean_digits}"
        try:
            webbrowser.open(tel_url)
        except Exception:
            pass

        # Also provide prompt for status update after calling
        confirm = messagebox.askyesno(
            "Calling Follow-up",
            f"Calling {name} ({phone})\n\nKya aapka call ho gaya? Kya aap is task ka status 'In Progress' ya 'Completed' update karna chahte hain?"
        )
        if confirm:
            task["status"] = "Completed"
            self.save_tasks_data()
            self.apply_task_filters()

    def execute_task_whatsapp(self, task):
        # Dispatch WhatsApp using Chrome profile picker
        client_proxy = {
            "name": task.get("client_name", "Client"),
            "phone": task.get("phone", "")
        }
        self.send_whatsapp_to_client(client_proxy)

    def open_add_task_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Add New Task & Follow-up")
        modal.geometry("560x580")
        modal.minsize(480, 520)
        modal.config(bg="#ffffff")
        modal.transient(self)
        modal.grab_set()

        head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=22, pady=18)
        head.pack(fill=tk.X)
        tk.Label(head, text="Create New Task & Follow-up", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(head, text="Assign task, set follow-up channel (Call/WhatsApp) and schedule due date", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(modal, bg="#ffffff", padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        # Title & ID
        r1 = tk.Frame(body, bg="#ffffff")
        r1.pack(fill=tk.X, pady=(0, 10))
        c_title = tk.Frame(r1, bg="#ffffff")
        c_title.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_title, text="Task Title *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        title_ent = tk.Entry(c_title, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        title_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)

        c_id = tk.Frame(r1, bg="#ffffff")
        c_id.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_id, text="Task ID", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        auto_id = f"TSK-{len(self.all_tasks) + 201}"
        id_ent = tk.Entry(c_id, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        id_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        id_ent.insert(0, auto_id)

        # Client Name & Phone
        r2 = tk.Frame(body, bg="#ffffff")
        r2.pack(fill=tk.X, pady=(0, 10))
        c_cl = tk.Frame(r2, bg="#ffffff")
        c_cl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_cl, text="Client / Contact Name *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        cl_ent = tk.Entry(c_cl, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        cl_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)

        c_ph = tk.Frame(r2, bg="#ffffff")
        c_ph.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_ph, text="Phone Number *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        ph_ent = tk.Entry(c_ph, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        ph_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)

        # Task Type & Priority
        r3 = tk.Frame(body, bg="#ffffff")
        r3.pack(fill=tk.X, pady=(0, 10))
        c_tp = tk.Frame(r3, bg="#ffffff")
        c_tp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_tp, text="Task Type / Channel", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        type_cb = ttk.Combobox(c_tp, values=["Calling Follow-up", "WhatsApp Follow-up", "Payment Collection", "Client Demo", "General Task"], font=FONT_DATA)
        type_cb.set("Calling Follow-up")
        type_cb.pack(fill=tk.X, pady=(4, 0))

        c_pr = tk.Frame(r3, bg="#ffffff")
        c_pr.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_pr, text="Priority", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        pr_cb = ttk.Combobox(c_pr, values=["Normal", "High", "Urgent", "Low"], font=FONT_DATA, state="readonly")
        pr_cb.set("Normal")
        pr_cb.pack(fill=tk.X, pady=(4, 0))

        # Status & Due Date & Assigned To
        r4 = tk.Frame(body, bg="#ffffff")
        r4.pack(fill=tk.X, pady=(0, 10))
        c_st = tk.Frame(r4, bg="#ffffff")
        c_st.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Label(c_st, text="Status", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        st_cb = ttk.Combobox(c_st, values=["Pending", "In Progress", "Completed", "Cancelled"], font=FONT_DATA, state="readonly")
        st_cb.set("Pending")
        st_cb.pack(fill=tk.X, pady=(4, 0))

        c_dd = tk.Frame(r4, bg="#ffffff")
        c_dd.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Label(c_dd, text="Due Date", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        dd_ent = tk.Entry(c_dd, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        dd_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        dd_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))

        c_as = tk.Frame(r4, bg="#ffffff")
        c_as.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
        tk.Label(c_as, text="Assign To", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        emp_names = [e.get("name") for e in self.all_employees] if self.all_employees else ["Self"]
        as_cb = ttk.Combobox(c_as, values=emp_names, font=FONT_DATA)
        as_cb.set(emp_names[0] if emp_names else "Self")
        as_cb.pack(fill=tk.X, pady=(4, 0))

        # Notes / Discussion
        tk.Label(body, text="Task Instructions & Follow-up Notes:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        notes_box = tk.Text(body, font=FONT_DATA, bg="#f8fafc", fg=C_TEXT_HERO, relief=tk.SOLID, bd=1, height=4, padx=10, pady=8)
        notes_box.pack(fill=tk.BOTH, expand=True, pady=(4, 16))

        def _save_task():
            t_title = title_ent.get().strip()
            c_name = cl_ent.get().strip()
            c_phone = ph_ent.get().strip()
            if not t_title or not c_name or not c_phone:
                messagebox.showwarning("Missing Fields", "Task Title, Client Name aur Phone Number bharna zaroori hai.")
                return

            new_task = {
                "id": id_ent.get().strip() or f"TSK-{len(self.all_tasks)+201}",
                "title": t_title,
                "client_name": c_name,
                "phone": c_phone,
                "type": type_cb.get().strip() or "General Task",
                "priority": pr_cb.get().strip() or "Normal",
                "due_date": dd_ent.get().strip() or datetime.now().strftime("%Y-%m-%d"),
                "status": st_cb.get().strip() or "Pending",
                "assigned_to": as_cb.get().strip() or "Self",
                "notes": notes_box.get("1.0", tk.END).strip() or "-"
            }

            self.all_tasks.insert(0, new_task)
            self.save_tasks_data()
            self.apply_task_filters()
            modal.destroy()
            messagebox.showinfo("Success", f"Task '{t_title}' successfully create ho gaya!")

        # Action Buttons
        btn_bar = tk.Frame(body, bg="#ffffff")
        btn_bar.pack(fill=tk.X)

        create_btn = tk.Button(btn_bar, text="Create Task", font=FONT_HEAD, bg=C_TEAL_PRIMARY, fg="#ffffff", activebackground=C_TEAL_DARK, relief=tk.FLAT, padx=20, pady=7, cursor="hand2", command=_save_task)
        create_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(btn_bar, text="Cancel", font=FONT_DATA, bg="#f1f5f9", fg=C_TEXT_BODY, relief=tk.FLAT, padx=14, pady=7, cursor="hand2", command=modal.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=8)

    def open_edit_task_modal(self, task):
        modal = tk.Toplevel(self)
        modal.title(f"Edit Task — {task.get('title')}")
        modal.geometry("560x580")
        modal.minsize(480, 520)
        modal.config(bg="#ffffff")
        modal.transient(self)
        modal.grab_set()

        head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=22, pady=18)
        head.pack(fill=tk.X)
        tk.Label(head, text=f"Edit Task — {task.get('id')}", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(head, text="Update task status, due date, follow-up channel or assignees", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(modal, bg="#ffffff", padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        # Title & ID
        r1 = tk.Frame(body, bg="#ffffff")
        r1.pack(fill=tk.X, pady=(0, 10))
        c_title = tk.Frame(r1, bg="#ffffff")
        c_title.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_title, text="Task Title *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        title_ent = tk.Entry(c_title, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        title_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        title_ent.insert(0, task.get("title", ""))

        c_id = tk.Frame(r1, bg="#ffffff")
        c_id.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_id, text="Task ID", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        id_ent = tk.Entry(c_id, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        id_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        id_ent.insert(0, task.get("id", ""))

        # Client Name & Phone
        r2 = tk.Frame(body, bg="#ffffff")
        r2.pack(fill=tk.X, pady=(0, 10))
        c_cl = tk.Frame(r2, bg="#ffffff")
        c_cl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_cl, text="Client / Contact Name *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        cl_ent = tk.Entry(c_cl, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        cl_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        cl_ent.insert(0, task.get("client_name", ""))

        c_ph = tk.Frame(r2, bg="#ffffff")
        c_ph.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_ph, text="Phone Number *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        ph_ent = tk.Entry(c_ph, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        ph_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        ph_ent.insert(0, task.get("phone", ""))

        # Task Type & Priority
        r3 = tk.Frame(body, bg="#ffffff")
        r3.pack(fill=tk.X, pady=(0, 10))
        c_tp = tk.Frame(r3, bg="#ffffff")
        c_tp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_tp, text="Task Type / Channel", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        type_cb = ttk.Combobox(c_tp, values=["Calling Follow-up", "WhatsApp Follow-up", "Payment Collection", "Client Demo", "General Task"], font=FONT_DATA)
        type_cb.set(task.get("type", "Calling Follow-up"))
        type_cb.pack(fill=tk.X, pady=(4, 0))

        c_pr = tk.Frame(r3, bg="#ffffff")
        c_pr.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_pr, text="Priority", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        pr_cb = ttk.Combobox(c_pr, values=["Normal", "High", "Urgent", "Low"], font=FONT_DATA, state="readonly")
        pr_cb.set(task.get("priority", "Normal"))
        pr_cb.pack(fill=tk.X, pady=(4, 0))

        # Status & Due Date & Assigned To
        r4 = tk.Frame(body, bg="#ffffff")
        r4.pack(fill=tk.X, pady=(0, 10))
        c_st = tk.Frame(r4, bg="#ffffff")
        c_st.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Label(c_st, text="Status", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        st_cb = ttk.Combobox(c_st, values=["Pending", "In Progress", "Completed", "Cancelled"], font=FONT_DATA, state="readonly")
        st_cb.set(task.get("status", "Pending"))
        st_cb.pack(fill=tk.X, pady=(4, 0))

        c_dd = tk.Frame(r4, bg="#ffffff")
        c_dd.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Label(c_dd, text="Due Date", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        dd_ent = tk.Entry(c_dd, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        dd_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        dd_ent.insert(0, task.get("due_date", datetime.now().strftime("%Y-%m-%d")))

        c_as = tk.Frame(r4, bg="#ffffff")
        c_as.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
        tk.Label(c_as, text="Assign To", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        emp_names = [e.get("name") for e in self.all_employees] if self.all_employees else ["Self"]
        as_cb = ttk.Combobox(c_as, values=emp_names, font=FONT_DATA)
        as_cb.set(task.get("assigned_to", emp_names[0] if emp_names else "Self"))
        as_cb.pack(fill=tk.X, pady=(4, 0))

        # Notes / Discussion
        tk.Label(body, text="Task Instructions & Follow-up Notes:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        notes_box = tk.Text(body, font=FONT_DATA, bg="#f8fafc", fg=C_TEXT_HERO, relief=tk.SOLID, bd=1, height=4, padx=10, pady=8)
        notes_box.pack(fill=tk.BOTH, expand=True, pady=(4, 16))
        notes_box.insert(tk.END, task.get("notes", ""))

        def _save_changes():
            t_title = title_ent.get().strip()
            c_name = cl_ent.get().strip()
            c_phone = ph_ent.get().strip()
            if not t_title or not c_name or not c_phone:
                messagebox.showwarning("Missing Fields", "Task Title, Client Name aur Phone Number bharna zaroori hai.")
                return

            task["id"] = id_ent.get().strip() or task.get("id", "TSK-000")
            task["title"] = t_title
            task["client_name"] = c_name
            task["phone"] = c_phone
            task["type"] = type_cb.get().strip() or "General Task"
            task["priority"] = pr_cb.get().strip() or "Normal"
            task["due_date"] = dd_ent.get().strip()
            task["status"] = st_cb.get().strip() or "Pending"
            task["assigned_to"] = as_cb.get().strip() or "Self"
            task["notes"] = notes_box.get("1.0", tk.END).strip() or "-"

            self.save_tasks_data()
            self.apply_task_filters()
            modal.destroy()
            messagebox.showinfo("Saved", f"Task '{t_title}' updated successfully!")

        # Action Buttons
        btn_bar = tk.Frame(body, bg="#ffffff")
        btn_bar.pack(fill=tk.X)

        del_b = tk.Button(
            btn_bar,
            text="Delete Task",
            font=FONT_DATA,
            bg="#fff1f2",
            fg="#e11d48",
            activebackground="#ffe4e6",
            activeforeground="#be123c",
            relief=tk.FLAT,
            padx=14,
            pady=7,
            cursor="hand2",
            command=lambda: [modal.destroy(), self.delete_task(task)]
        )
        del_b.pack(side=tk.LEFT)

        save_btn = tk.Button(btn_bar, text="Save Changes", font=FONT_HEAD, bg=C_TEAL_PRIMARY, fg="#ffffff", activebackground=C_TEAL_DARK, relief=tk.FLAT, padx=20, pady=7, cursor="hand2", command=_save_changes)
        save_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(btn_bar, text="Cancel", font=FONT_DATA, bg="#f1f5f9", fg=C_TEXT_BODY, relief=tk.FLAT, padx=14, pady=7, cursor="hand2", command=modal.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=8)

    def delete_task(self, task):
        t_title = task.get("title", "Task")
        confirm = messagebox.askyesno("Confirm Delete", f"Kya aap sach me task '{t_title}' ko delete karna chahte hain?")
        if confirm:
            if task in self.all_tasks:
                self.all_tasks.remove(task)
            if task in self.filtered_tasks:
                self.filtered_tasks.remove(task)
            self.save_tasks_data()
            self.apply_task_filters()
            messagebox.showinfo("Deleted", f"Task '{t_title}' delete ho chuka hai.")

    # =========================================================================
    # ACCOUNTS & FINANCIAL MANAGEMENT: INCOME, EXPENSES, SALARIES (ADD, EDIT, DELETE, SEARCH, FILTER)
    # =========================================================================
    def load_accounts_data(self):
        if os.path.exists(TRANSACTIONS_FILE):
            try:
                with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
                    self.all_transactions = json.load(f)
            except Exception as e:
                print("Error loading accounts vault:", e)
                self.all_transactions = []
        else:
            # Starter comprehensive financial ledger
            self.all_transactions = [
                {
                    "id": "TXN-501",
                    "title": "Client Retainer Fee - Kavya Traders",
                    "type": "Income",
                    "category": "Client Payments",
                    "amount": 45000.0,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "payment_mode": "Bank Transfer / NEFT",
                    "party": "Kavya Traders",
                    "status": "Received",
                    "notes": "Monthly retainership for AI agent integration."
                },
                {
                    "id": "TXN-502",
                    "title": "Staff Monthly Salary - Rohit Sharma",
                    "type": "Salary",
                    "category": "Employee Salaries",
                    "amount": 35000.0,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "payment_mode": "UPI / IMPS",
                    "party": "Rohit Sharma (EMP-101)",
                    "status": "Paid",
                    "notes": "Salary for Sales Lead position."
                },
                {
                    "id": "TXN-503",
                    "title": "Staff Monthly Salary - Punit Verma",
                    "type": "Salary",
                    "category": "Employee Salaries",
                    "amount": 32000.0,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "payment_mode": "UPI / IMPS",
                    "party": "Punit Verma (EMP-102)",
                    "status": "Paid",
                    "notes": "Salary for Operations Manager."
                },
                {
                    "id": "TXN-504",
                    "title": "Cloud Server & Database Hosting",
                    "type": "Expense",
                    "category": "Infrastructure & Software",
                    "amount": 6800.0,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "payment_mode": "Credit Card",
                    "party": "Google Cloud & AWS",
                    "status": "Paid",
                    "notes": "Server hosting and API quota recharge."
                },
                {
                    "id": "TXN-505",
                    "title": "Office High-Speed Internet & Utilities",
                    "type": "Expense",
                    "category": "Office Utilities",
                    "amount": 2400.0,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "payment_mode": "UPI",
                    "party": "Airtel Broadband",
                    "status": "Paid",
                    "notes": "Office internet and electricity bill."
                },
                {
                    "id": "TXN-506",
                    "title": "New CRM Setup Milestone Payment",
                    "type": "Income",
                    "category": "Software Implementation",
                    "amount": 25000.0,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "payment_mode": "Cheque",
                    "party": "Webspool Private Limited",
                    "status": "Pending",
                    "notes": "Milestone 1 payment pending clearance."
                }
            ]
            self.save_accounts_data()

        self.filtered_transactions = list(self.all_transactions)

    def save_accounts_data(self):
        try:
            with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.all_transactions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Error saving accounts vault:", e)

    def build_accounts_page(self, parent):
        # 1. STUDIO HEADER ROW: SEARCH BAR + ACTION TOOLBAR (+ Record Entry)
        top_bar = tk.Frame(parent, bg=C_CANVAS, height=56)
        top_bar.pack(fill=tk.X, padx=20, pady=(16, 12))
        top_bar.pack_propagate(False)

        search_card = tk.Frame(top_bar, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        search_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        search_wrap = tk.Frame(search_card, bg="#ffffff")
        search_wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        tk.Label(search_wrap, image=self.icons["search"], bg="#ffffff").pack(side=tk.LEFT, padx=(6, 8))

        self.acc_search_entry = tk.Entry(
            search_wrap,
            font=FONT_SEARCH,
            bg="#ffffff",
            fg=C_TEXT_HERO,
            insertbackground=C_TEAL_PRIMARY,
            relief=tk.FLAT,
            bd=0
        )
        self.acc_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, ipady=4)
        self.acc_search_entry.insert(0, "Search ledger by title, party/employee, category, mode or notes...")
        self.acc_search_entry.config(fg=C_TEXT_MUTED)

        def _acc_s_in(e):
            if self.acc_search_entry.get() == "Search ledger by title, party/employee, category, mode or notes...":
                self.acc_search_entry.delete(0, tk.END)
                self.acc_search_entry.config(fg=C_TEXT_HERO)

        def _acc_s_out(e):
            if not self.acc_search_entry.get().strip():
                self.acc_search_entry.insert(0, "Search ledger by title, party/employee, category, mode or notes...")
                self.acc_search_entry.config(fg=C_TEXT_MUTED)

        self.acc_search_entry.bind("<FocusIn>", _acc_s_in)
        self.acc_search_entry.bind("<FocusOut>", _acc_s_out)
        self.acc_search_entry.bind("<KeyRelease>", lambda e: self.apply_account_filters())

        # Action Buttons on Right (Floating Mor Pankh Copilot Button + Add Transaction)
        ai_logo_kw = {"image": self.mor_pankh_btn_photo} if self.mor_pankh_btn_photo else {"image": self.icons["ai"]}
        self.copilot_trigger_acc = tk.Button(
            top_bar,
            **ai_logo_kw,
            bg=C_CANVAS,
            activebackground=C_CANVAS,
            relief=tk.FLAT,
            bd=0,
            padx=0,
            pady=0,
            cursor="hand2",
            command=self.toggle_copilot_side_panel
        )
        if self.mor_pankh_btn_hover:
            self.copilot_trigger_acc.bind("<Enter>", lambda e: self.copilot_trigger_acc.config(image=self.mor_pankh_btn_hover))
            self.copilot_trigger_acc.bind("<Leave>", lambda e: self.copilot_trigger_acc.config(image=self.mor_pankh_btn_photo))
        self.copilot_trigger_acc.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 4))

        # + Add Transaction Button
        add_entry_btn = tk.Button(
            top_bar,
            text="+ Add Income / Expense / Salary",
            font=("Segoe UI Semibold", 10),
            bg=C_TEAL_PRIMARY,
            fg="#ffffff",
            activebackground=C_TEAL_DARK,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
            command=self.open_add_transaction_modal
        )
        add_entry_btn.pack(side=tk.RIGHT, fill=tk.Y)

        # 2. FINANCIAL STATS OVERVIEW & CATEGORY PILLS (Income, Expenses, Salaries, Net Balance)
        self.acc_filter_cards_bar = tk.Frame(parent, bg=C_CANVAS, height=72)
        self.acc_filter_cards_bar.pack(fill=tk.X, padx=20, pady=(0, 14))
        self.acc_filter_cards_bar.pack_propagate(False)

        self.acc_categories = [
            ("All", "All Transactions", "#0e7490", "#e0f2fe"),
            ("Income", "Total Income", "#059669", "#ecfdf5"),
            ("Expense", "Business Expenses", "#e11d48", "#fff1f2"),
            ("Salary", "Employee Salaries", "#d97706", "#fef3c7"),
            ("Net", "Net Balance", "#004d40", "#e0f2f1")
        ]

        self.acc_card_widgets = {}
        for s_key, s_title, s_color, s_bg in self.acc_categories:
            card = tk.Frame(
                self.acc_filter_cards_bar,
                bg=C_CARD,
                highlightbackground="#e2e8f0",
                highlightthickness=1,
                padx=14,
                pady=8,
                cursor="hand2"
            )
            card.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)

            top_line = tk.Frame(card, bg=C_CARD)
            top_line.pack(fill=tk.X)

            dot = tk.Label(top_line, text="●", font=("Segoe UI", 9), fg=s_color, bg=C_CARD)
            dot.pack(side=tk.LEFT, padx=(0, 5))

            title_lbl = tk.Label(top_line, text=s_title, font=("Segoe UI Semibold", 9), fg="#64748b", bg=C_CARD)
            title_lbl.pack(side=tk.LEFT)

            amount_lbl = tk.Label(card, text="₹0", font=("Segoe UI", 15, "bold"), fg=C_TEXT_HERO, bg=C_CARD, anchor=tk.W)
            amount_lbl.pack(anchor=tk.W, pady=(3, 0))

            self.acc_card_widgets[s_key] = {
                "frame": card,
                "top_line": top_line,
                "dot": dot,
                "title": title_lbl,
                "amount": amount_lbl,
                "color": s_color,
                "bg_accent": s_bg
            }

            def _bind_acc_filter(key=s_key, widgets=[card, top_line, dot, title_lbl, amount_lbl]):
                for w in widgets:
                    w.bind("<Button-1>", lambda e, k=key: self.select_acc_filter(k))

            _bind_acc_filter()

        # 3. MODERN TRANSACTIONS LEDGER TABLE CONTAINER
        self.acc_table_card = tk.Frame(parent, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        self.acc_table_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

        # Column Layout Widths
        self.acc_col_widths = {
            "title": 260,
            "party": 180,
            "type": 110,
            "category": 150,
            "amount": 130,
            "date_mode": 150,
            "status": 100,
            "action": 130
        }

        # Table Header
        acc_hdr = tk.Frame(self.acc_table_card, bg="#f8fafc", height=42, highlightbackground=C_BORDER, highlightthickness=1)
        acc_hdr.pack(fill=tk.X)
        acc_hdr.pack_propagate(False)

        h_title = tk.Frame(acc_hdr, bg="#f8fafc", width=self.acc_col_widths["title"])
        h_title.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_title.pack_propagate(False)
        tk.Label(h_title, text="TRANSACTION TITLE", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=12)

        h_party = tk.Frame(acc_hdr, bg="#f8fafc", width=self.acc_col_widths["party"])
        h_party.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_party.pack_propagate(False)
        tk.Label(h_party, text="PARTY / RECIPIENT", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_type = tk.Frame(acc_hdr, bg="#f8fafc", width=self.acc_col_widths["type"])
        h_type.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_type.pack_propagate(False)
        tk.Label(h_type, text="TYPE", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_cat = tk.Frame(acc_hdr, bg="#f8fafc", width=self.acc_col_widths["category"])
        h_cat.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_cat.pack_propagate(False)
        tk.Label(h_cat, text="CATEGORY", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_amt = tk.Frame(acc_hdr, bg="#f8fafc", width=self.acc_col_widths["amount"])
        h_amt.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_amt.pack_propagate(False)
        tk.Label(h_amt, text="AMOUNT (INR)", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_dt = tk.Frame(acc_hdr, bg="#f8fafc", width=self.acc_col_widths["date_mode"])
        h_dt.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_dt.pack_propagate(False)
        tk.Label(h_dt, text="DATE & PAYMENT MODE", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_st = tk.Frame(acc_hdr, bg="#f8fafc", width=self.acc_col_widths["status"])
        h_st.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        h_st.pack_propagate(False)
        tk.Label(h_st, text="STATUS", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        h_act = tk.Frame(acc_hdr, bg="#f8fafc", width=self.acc_col_widths["action"])
        h_act.pack(side=tk.RIGHT, fill=tk.Y, padx=4)
        h_act.pack_propagate(False)
        tk.Label(h_act, text="ACTIONS", font=("Segoe UI Bold", 9), fg="#64748b", bg="#f8fafc", anchor=tk.W).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Scrollable rows stage (Zero-Smear Architecture)
        acc_canvas_wrap = tk.Frame(self.acc_table_card, bg="#ffffff")
        acc_canvas_wrap.pack(fill=tk.BOTH, expand=True)

        self.acc_canvas = tk.Canvas(acc_canvas_wrap, bg="#ffffff", bd=0, highlightthickness=0)
        self.acc_rows_frame = tk.Frame(self.acc_canvas, bg="#ffffff")
        self.acc_canvas_window = self.acc_canvas.create_window((0, 0), window=self.acc_rows_frame, anchor="nw")

        self.acc_vsb = ttk.Scrollbar(acc_canvas_wrap, orient="vertical")
        self.acc_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.acc_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.setup_zero_smear_scroll(self.acc_canvas, self.acc_canvas_window, self.acc_rows_frame, self.acc_vsb)

        self.refresh_accounts_page()

    def select_acc_filter(self, key):
        self.active_acc_type_filter = key
        self.apply_account_filters()

    def apply_account_filters(self):
        q = self.acc_search_entry.get().strip().lower()
        has_query = q and q != "search ledger by title, party/employee, category, mode or notes..."

        filtered = []
        for t in self.all_transactions:
            if has_query:
                matches = (
                    q in t.get("title", "").lower() or
                    q in t.get("party", "").lower() or
                    q in t.get("type", "").lower() or
                    q in t.get("category", "").lower() or
                    q in t.get("payment_mode", "").lower() or
                    q in t.get("id", "").lower() or
                    q in str(t.get("amount", "")) or
                    q in t.get("notes", "").lower()
                )
                if not matches:
                    continue

            # Type filter
            if self.active_acc_type_filter not in ["All", "Net"]:
                if t.get("type", "").strip().lower() != self.active_acc_type_filter.lower():
                    continue

            filtered.append(t)

        self.filtered_transactions = filtered
        self.render_accounts_table()
        self.update_accounts_stats_ui()

    def update_accounts_stats_ui(self):
        total_income = sum(float(t.get("amount", 0)) for t in self.all_transactions if t.get("type") == "Income")
        total_expense = sum(float(t.get("amount", 0)) for t in self.all_transactions if t.get("type") == "Expense")
        total_salary = sum(float(t.get("amount", 0)) for t in self.all_transactions if t.get("type") == "Salary")
        net_balance = total_income - (total_expense + total_salary)

        amounts_map = {
            "All": total_income,
            "Income": total_income,
            "Expense": total_expense,
            "Salary": total_salary,
            "Net": net_balance
        }

        for s_key, widgets in self.acc_card_widgets.items():
            val = amounts_map.get(s_key, 0.0)
            sign = "₹" if val >= 0 else "-₹"
            abs_val = abs(val)
            formatted = f"{sign}{abs_val:,.0f}"

            widgets["amount"].config(text=formatted)

            # Highlighting active card
            if s_key == self.active_acc_type_filter:
                widgets["frame"].config(bg=widgets["bg_accent"], highlightbackground=widgets["color"], highlightthickness=2)
                widgets["title"].config(bg=widgets["bg_accent"], fg=widgets["color"], font=("Segoe UI Bold", 9))
                widgets["dot"].config(bg=widgets["bg_accent"])
                widgets["amount"].config(bg=widgets["bg_accent"], fg=widgets["color"])
            else:
                widgets["frame"].config(bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
                widgets["title"].config(bg=C_CARD, fg=C_TEXT_BODY, font=("Segoe UI Semibold", 9))
                widgets["dot"].config(bg=C_CARD)
                widgets["amount"].config(bg=C_CARD, fg=C_TEXT_HERO)

    def refresh_accounts_page(self):
        self.apply_account_filters()

    def render_accounts_table(self):
        for w in self.acc_rows_frame.winfo_children():
            w.destroy()

        if not self.filtered_transactions:
            empty_box = tk.Frame(self.acc_rows_frame, bg="#ffffff", pady=60)
            empty_box.pack(fill=tk.BOTH, expand=True)
            tk.Label(empty_box, text="🔍 No transactions found in ledger", font=("Segoe UI Semibold", 12), fg=C_TEXT_MUTED, bg="#ffffff").pack()
            tk.Label(empty_box, text="Record income, expense or staff salary using '+ Add Income / Expense / Salary'.", font=FONT_DATA, fg="#94a3b8", bg="#ffffff").pack(pady=(4, 0))
            return

        type_styles = {
            "Income": {"fg": "#047857", "bg": "#ecfdf5", "prefix": "+₹"},
            "Expense": {"fg": "#be123c", "bg": "#fff1f2", "prefix": "-₹"},
            "Salary": {"fg": "#b45309", "bg": "#fef3c7", "prefix": "-₹"}
        }

        status_styles = {
            "Received": {"fg": "#047857", "bg": "#ecfdf5", "dot": "●"},
            "Paid": {"fg": "#047857", "bg": "#ecfdf5", "dot": "●"},
            "Pending": {"fg": "#b45309", "bg": "#fef3c7", "dot": "●"},
            "Cancelled": {"fg": "#be123c", "bg": "#fff1f2", "dot": "●"}
        }

        for idx, txn in enumerate(self.filtered_transactions):
            bg_row = "#ffffff" if idx % 2 == 0 else "#fbfcfd"
            row = tk.Frame(self.acc_rows_frame, bg=bg_row, height=56, highlightbackground="#f1f5f9", highlightthickness=1)
            row.pack(fill=tk.X)
            row.pack_propagate(False)

            # Col 1: Title & ID
            c1 = tk.Frame(row, bg=bg_row, width=self.acc_col_widths["title"])
            c1.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c1.pack_propagate(False)

            info_b = tk.Frame(c1, bg=bg_row)
            info_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=6)
            t_title = txn.get("title", "Transaction")
            if len(t_title) > 34:
                t_title = t_title[:32] + "..."
            tk.Label(info_b, text=t_title, font=FONT_NAME, fg=C_TEXT_HERO, bg=bg_row, anchor=tk.W).pack(anchor=tk.W)
            tk.Label(info_b, text=f"ID: {txn.get('id', '-')}", font=("Segoe UI", 8), fg="#94a3b8", bg=bg_row, anchor=tk.W).pack(anchor=tk.W)

            # Col 2: Party / Recipient
            c2 = tk.Frame(row, bg=bg_row, width=self.acc_col_widths["party"])
            c2.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c2.pack_propagate(False)
            tk.Label(c2, text=txn.get("party", "-"), font=("Segoe UI Semibold", 9), fg=C_TEXT_HERO, bg=bg_row, anchor=tk.W).pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

            # Col 3: Type Pill
            c3 = tk.Frame(row, bg=bg_row, width=self.acc_col_widths["type"])
            c3.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c3.pack_propagate(False)
            t_type = txn.get("type", "Expense")
            t_style = type_styles.get(t_type, type_styles["Expense"])
            tk.Label(c3, text=t_type, font=FONT_BADGE, fg=t_style["fg"], bg=t_style["bg"], padx=8, pady=3).pack(side=tk.LEFT, padx=6)

            # Col 4: Category
            c4 = tk.Frame(row, bg=bg_row, width=self.acc_col_widths["category"])
            c4.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c4.pack_propagate(False)
            tk.Label(c4, text=txn.get("category", "-"), font=FONT_DATA, fg="#475569", bg=bg_row, anchor=tk.W).pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

            # Col 5: Amount
            c5 = tk.Frame(row, bg=bg_row, width=self.acc_col_widths["amount"])
            c5.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c5.pack_propagate(False)
            amt = float(txn.get("amount", 0.0))
            amt_str = f"{t_style['prefix']}{amt:,.0f}"
            tk.Label(c5, text=amt_str, font=("Segoe UI Bold", 10), fg=t_style["fg"], bg=bg_row, anchor=tk.W).pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

            # Col 6: Date & Payment Mode
            c6 = tk.Frame(row, bg=bg_row, width=self.acc_col_widths["date_mode"])
            c6.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c6.pack_propagate(False)
            dt_box = tk.Frame(c6, bg=bg_row)
            dt_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=6)
            tk.Label(dt_box, text=txn.get("date", "-"), font=("Segoe UI Semibold", 8), fg=C_TEXT_HERO, bg=bg_row, anchor=tk.W).pack(anchor=tk.W)
            tk.Label(dt_box, text=txn.get("payment_mode", "-"), font=("Segoe UI", 8), fg="#64748b", bg=bg_row, anchor=tk.W).pack(anchor=tk.W)

            # Col 7: Status Pill
            c7 = tk.Frame(row, bg=bg_row, width=self.acc_col_widths["status"])
            c7.pack(side=tk.LEFT, fill=tk.Y, padx=4)
            c7.pack_propagate(False)
            st_val = txn.get("status", "Paid")
            st_style = status_styles.get(st_val, {"fg": "#475569", "bg": "#f1f5f9", "dot": "●"})
            tk.Label(c7, text=f"{st_style['dot']} {st_val}", font=FONT_BADGE, fg=st_style["fg"], bg=st_style["bg"], padx=8, pady=3).pack(side=tk.LEFT, padx=6)

            # Col 8: Action Buttons (Edit & Delete)
            c8 = tk.Frame(row, bg=bg_row, width=self.acc_col_widths["action"])
            c8.pack(side=tk.RIGHT, fill=tk.Y, padx=4)
            c8.pack_propagate(False)

            del_b = tk.Button(
                c8,
                text="Delete",
                font=("Segoe UI Semibold", 8),
                bg="#fff1f2",
                fg="#e11d48",
                activebackground="#ffe4e6",
                activeforeground="#be123c",
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda t=txn: self.delete_transaction(t)
            )
            del_b.pack(side=tk.RIGHT, padx=(4, 8), pady=12)

            edit_b = tk.Button(
                c8,
                text="Edit",
                font=("Segoe UI Semibold", 8),
                bg=C_TEAL_LIGHT,
                fg=C_TEAL_DARK,
                activebackground=C_TEAL_PRIMARY,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda t=txn: self.open_edit_transaction_modal(t)
            )
            edit_b.pack(side=tk.RIGHT, padx=(0, 4), pady=12)

            def _on_e(e, r=row):
                r.config(bg=C_ROW_HOVER)
            def _on_l(e, r=row, ob=bg_row):
                r.config(bg=ob)

            row.bind("<Enter>", _on_e)
            row.bind("<Leave>", _on_l)
            self.bind_smooth_wheel_recursive(row, self.acc_canvas)

    def open_add_transaction_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Record Transaction (Income / Expense / Salary)")
        modal.geometry("560x600")
        modal.minsize(480, 520)
        modal.config(bg="#ffffff")
        modal.transient(self)
        modal.grab_set()

        head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=22, pady=18)
        head.pack(fill=tk.X)
        tk.Label(head, text="Record New Financial Entry", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(head, text="Record client revenue, business operating expenses or employee salaries", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(modal, bg="#ffffff", padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        # Title & ID
        r1 = tk.Frame(body, bg="#ffffff")
        r1.pack(fill=tk.X, pady=(0, 10))
        c_title = tk.Frame(r1, bg="#ffffff")
        c_title.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_title, text="Transaction Title *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        title_ent = tk.Entry(c_title, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        title_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)

        c_id = tk.Frame(r1, bg="#ffffff")
        c_id.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_id, text="Transaction ID", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        auto_id = f"TXN-{len(self.all_transactions) + 501}"
        id_ent = tk.Entry(c_id, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        id_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        id_ent.insert(0, auto_id)

        # Type & Amount
        r2 = tk.Frame(body, bg="#ffffff")
        r2.pack(fill=tk.X, pady=(0, 10))
        c_tp = tk.Frame(r2, bg="#ffffff")
        c_tp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_tp, text="Transaction Type *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        type_cb = ttk.Combobox(c_tp, values=["Income", "Expense", "Salary"], font=FONT_DATA, state="readonly")
        type_cb.set("Income")
        type_cb.pack(fill=tk.X, pady=(4, 0))

        c_amt = tk.Frame(r2, bg="#ffffff")
        c_amt.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_amt, text="Amount (in INR ₹) *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        amt_ent = tk.Entry(c_amt, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        amt_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)

        # Party / Recipient & Category
        r3 = tk.Frame(body, bg="#ffffff")
        r3.pack(fill=tk.X, pady=(0, 10))
        c_prty = tk.Frame(r3, bg="#ffffff")
        c_prty.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_prty, text="Party / Employee / Vendor *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        party_ent = tk.Entry(c_prty, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        party_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)

        c_cat = tk.Frame(r3, bg="#ffffff")
        c_cat.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_cat, text="Accounting Category", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        cat_cb = ttk.Combobox(c_cat, values=["Client Payments", "Employee Salaries", "Office Utilities", "Infrastructure & Software", "Marketing & Ads", "Travel & Fuel", "Miscellaneous"], font=FONT_DATA)
        cat_cb.set("Client Payments")
        cat_cb.pack(fill=tk.X, pady=(4, 0))

        # Dynamic category sync on type change
        def _on_type_select(e):
            sel = type_cb.get()
            if sel == "Salary":
                cat_cb.set("Employee Salaries")
                if self.all_employees and not party_ent.get().strip():
                    party_ent.delete(0, tk.END)
                    party_ent.insert(0, self.all_employees[0].get("name"))
            elif sel == "Income":
                cat_cb.set("Client Payments")
            elif sel == "Expense":
                cat_cb.set("Infrastructure & Software")

        type_cb.bind("<<ComboboxSelected>>", _on_type_select)

        # Date, Mode & Status
        r4 = tk.Frame(body, bg="#ffffff")
        r4.pack(fill=tk.X, pady=(0, 10))
        c_dt = tk.Frame(r4, bg="#ffffff")
        c_dt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Label(c_dt, text="Date", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        dt_ent = tk.Entry(c_dt, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        dt_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        dt_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))

        c_mod = tk.Frame(r4, bg="#ffffff")
        c_mod.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Label(c_mod, text="Payment Mode", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        mod_cb = ttk.Combobox(c_mod, values=["UPI", "Bank Transfer / NEFT", "IMPS", "Credit Card", "Cash", "Cheque"], font=FONT_DATA)
        mod_cb.set("UPI")
        mod_cb.pack(fill=tk.X, pady=(4, 0))

        c_st = tk.Frame(r4, bg="#ffffff")
        c_st.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
        tk.Label(c_st, text="Status", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        st_cb = ttk.Combobox(c_st, values=["Received", "Paid", "Pending", "Cancelled"], font=FONT_DATA, state="readonly")
        st_cb.set("Paid")
        st_cb.pack(fill=tk.X, pady=(4, 0))

        # Notes / Remarks
        tk.Label(body, text="Payment Description & Reference Notes:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        notes_box = tk.Text(body, font=FONT_DATA, bg="#f8fafc", fg=C_TEXT_HERO, relief=tk.SOLID, bd=1, height=4, padx=10, pady=8)
        notes_box.pack(fill=tk.BOTH, expand=True, pady=(4, 16))

        def _save_txn():
            t_title = title_ent.get().strip()
            amt_raw = amt_ent.get().strip()
            t_party = party_ent.get().strip()

            if not t_title or not amt_raw or not t_party:
                messagebox.showwarning("Missing Fields", "Transaction Title, Amount aur Party Name daalna zaroori hai.")
                return

            try:
                amt_val = float(amt_raw.replace(",", "").replace("₹", ""))
            except ValueError:
                messagebox.showerror("Invalid Amount", "Kripya sahi number amount enter karein (e.g. 15000).")
                return

            new_txn = {
                "id": id_ent.get().strip() or f"TXN-{len(self.all_transactions)+501}",
                "title": t_title,
                "type": type_cb.get().strip() or "Expense",
                "category": cat_cb.get().strip() or "General",
                "amount": amt_val,
                "date": dt_ent.get().strip() or datetime.now().strftime("%Y-%m-%d"),
                "payment_mode": mod_cb.get().strip() or "UPI",
                "party": t_party,
                "status": st_cb.get().strip() or "Paid",
                "notes": notes_box.get("1.0", tk.END).strip() or "-"
            }

            self.all_transactions.insert(0, new_txn)
            self.save_accounts_data()
            self.apply_account_filters()
            modal.destroy()
            messagebox.showinfo("Success", f"Transaction '{t_title}' successfully save ho gaya!")

        # Action Buttons
        btn_bar = tk.Frame(body, bg="#ffffff")
        btn_bar.pack(fill=tk.X)

        create_btn = tk.Button(btn_bar, text="Record Transaction", font=FONT_HEAD, bg=C_TEAL_PRIMARY, fg="#ffffff", activebackground=C_TEAL_DARK, relief=tk.FLAT, padx=20, pady=7, cursor="hand2", command=_save_txn)
        create_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(btn_bar, text="Cancel", font=FONT_DATA, bg="#f1f5f9", fg=C_TEXT_BODY, relief=tk.FLAT, padx=14, pady=7, cursor="hand2", command=modal.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=8)

    def open_edit_transaction_modal(self, txn):
        modal = tk.Toplevel(self)
        modal.title(f"Edit Transaction — {txn.get('id')}")
        modal.geometry("560x600")
        modal.minsize(480, 520)
        modal.config(bg="#ffffff")
        modal.transient(self)
        modal.grab_set()

        head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=22, pady=18)
        head.pack(fill=tk.X)
        tk.Label(head, text=f"Edit Transaction — {txn.get('id')}", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(head, text="Update amount, payment status, category or reference notes", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(modal, bg="#ffffff", padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        # Title & ID
        r1 = tk.Frame(body, bg="#ffffff")
        r1.pack(fill=tk.X, pady=(0, 10))
        c_title = tk.Frame(r1, bg="#ffffff")
        c_title.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_title, text="Transaction Title *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        title_ent = tk.Entry(c_title, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        title_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        title_ent.insert(0, txn.get("title", ""))

        c_id = tk.Frame(r1, bg="#ffffff")
        c_id.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_id, text="Transaction ID", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        id_ent = tk.Entry(c_id, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        id_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        id_ent.insert(0, txn.get("id", ""))

        # Type & Amount
        r2 = tk.Frame(body, bg="#ffffff")
        r2.pack(fill=tk.X, pady=(0, 10))
        c_tp = tk.Frame(r2, bg="#ffffff")
        c_tp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_tp, text="Transaction Type *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        type_cb = ttk.Combobox(c_tp, values=["Income", "Expense", "Salary"], font=FONT_DATA, state="readonly")
        type_cb.set(txn.get("type", "Expense"))
        type_cb.pack(fill=tk.X, pady=(4, 0))

        c_amt = tk.Frame(r2, bg="#ffffff")
        c_amt.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_amt, text="Amount (in INR ₹) *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        amt_ent = tk.Entry(c_amt, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        amt_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        amt_ent.insert(0, str(txn.get("amount", "")))

        # Party & Category
        r3 = tk.Frame(body, bg="#ffffff")
        r3.pack(fill=tk.X, pady=(0, 10))
        c_prty = tk.Frame(r3, bg="#ffffff")
        c_prty.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(c_prty, text="Party / Employee / Vendor *", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        party_ent = tk.Entry(c_prty, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        party_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        party_ent.insert(0, txn.get("party", ""))

        c_cat = tk.Frame(r3, bg="#ffffff")
        c_cat.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(c_cat, text="Accounting Category", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        cat_cb = ttk.Combobox(c_cat, values=["Client Payments", "Employee Salaries", "Office Utilities", "Infrastructure & Software", "Marketing & Ads", "Travel & Fuel", "Miscellaneous"], font=FONT_DATA)
        cat_cb.set(txn.get("category", "General"))
        cat_cb.pack(fill=tk.X, pady=(4, 0))

        # Date, Mode & Status
        r4 = tk.Frame(body, bg="#ffffff")
        r4.pack(fill=tk.X, pady=(0, 10))
        c_dt = tk.Frame(r4, bg="#ffffff")
        c_dt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Label(c_dt, text="Date", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        dt_ent = tk.Entry(c_dt, font=FONT_DATA, relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        dt_ent.pack(fill=tk.X, pady=(4, 0), ipady=3)
        dt_ent.insert(0, txn.get("date", datetime.now().strftime("%Y-%m-%d")))

        c_mod = tk.Frame(r4, bg="#ffffff")
        c_mod.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Label(c_mod, text="Payment Mode", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        mod_cb = ttk.Combobox(c_mod, values=["UPI", "Bank Transfer / NEFT", "IMPS", "Credit Card", "Cash", "Cheque"], font=FONT_DATA)
        mod_cb.set(txn.get("payment_mode", "UPI"))
        mod_cb.pack(fill=tk.X, pady=(4, 0))

        c_st = tk.Frame(r4, bg="#ffffff")
        c_st.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
        tk.Label(c_st, text="Status", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        st_cb = ttk.Combobox(c_st, values=["Received", "Paid", "Pending", "Cancelled"], font=FONT_DATA, state="readonly")
        st_cb.set(txn.get("status", "Paid"))
        st_cb.pack(fill=tk.X, pady=(4, 0))

        # Notes / Remarks
        tk.Label(body, text="Payment Description & Reference Notes:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        notes_box = tk.Text(body, font=FONT_DATA, bg="#f8fafc", fg=C_TEXT_HERO, relief=tk.SOLID, bd=1, height=4, padx=10, pady=8)
        notes_box.pack(fill=tk.BOTH, expand=True, pady=(4, 16))
        notes_box.insert(tk.END, txn.get("notes", ""))

        def _save_changes():
            t_title = title_ent.get().strip()
            amt_raw = amt_ent.get().strip()
            t_party = party_ent.get().strip()

            if not t_title or not amt_raw or not t_party:
                messagebox.showwarning("Missing Fields", "Transaction Title, Amount aur Party Name daalna zaroori hai.")
                return

            try:
                amt_val = float(amt_raw.replace(",", "").replace("₹", ""))
            except ValueError:
                messagebox.showerror("Invalid Amount", "Kripya sahi number amount enter karein.")
                return

            txn["id"] = id_ent.get().strip() or txn.get("id", "TXN-000")
            txn["title"] = t_title
            txn["type"] = type_cb.get().strip() or "Expense"
            txn["category"] = cat_cb.get().strip() or "General"
            txn["amount"] = amt_val
            txn["date"] = dt_ent.get().strip()
            txn["payment_mode"] = mod_cb.get().strip()
            txn["party"] = t_party
            txn["status"] = st_cb.get().strip()
            txn["notes"] = notes_box.get("1.0", tk.END).strip() or "-"

            self.save_accounts_data()
            self.apply_account_filters()
            modal.destroy()
            messagebox.showinfo("Saved", f"Transaction '{t_title}' updated successfully!")

        # Action Buttons
        btn_bar = tk.Frame(body, bg="#ffffff")
        btn_bar.pack(fill=tk.X)

        del_b = tk.Button(
            btn_bar,
            text="Delete Entry",
            font=FONT_DATA,
            bg="#fff1f2",
            fg="#e11d48",
            activebackground="#ffe4e6",
            activeforeground="#be123c",
            relief=tk.FLAT,
            padx=14,
            pady=7,
            cursor="hand2",
            command=lambda: [modal.destroy(), self.delete_transaction(txn)]
        )
        del_b.pack(side=tk.LEFT)

        save_btn = tk.Button(btn_bar, text="Save Changes", font=FONT_HEAD, bg=C_TEAL_PRIMARY, fg="#ffffff", activebackground=C_TEAL_DARK, relief=tk.FLAT, padx=20, pady=7, cursor="hand2", command=_save_changes)
        save_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(btn_bar, text="Cancel", font=FONT_DATA, bg="#f1f5f9", fg=C_TEXT_BODY, relief=tk.FLAT, padx=14, pady=7, cursor="hand2", command=modal.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=8)

    def delete_transaction(self, txn):
        t_title = txn.get("title", "Transaction")
        confirm = messagebox.askyesno("Confirm Delete", f"Kya aap sach me transaction '{t_title}' ko delete karna chahte hain?")
        if confirm:
            if txn in self.all_transactions:
                self.all_transactions.remove(txn)
            if txn in self.filtered_transactions:
                self.filtered_transactions.remove(txn)
            self.save_accounts_data()
            self.apply_account_filters()
            messagebox.showinfo("Deleted", f"Transaction '{t_title}' delete ho chuka hai.")

    # =========================================================================
    # WHATSAPP CAMPAIGN MANAGER & DISPATCH LOGIC
    # =========================================================================
    def get_client_key(self, client):
        phone_clean = "".join(filter(str.isdigit, client.get("phone", "")))
        if phone_clean:
            return phone_clean[-10:] if len(phone_clean) >= 10 else phone_clean
        return client.get("name", "").strip().lower()

    def is_whatsapp_sent_today(self, client):
        key = self.get_client_key(client)
        if not key or key not in self.whatsapp_logs:
            return False
        today_str = datetime.now().strftime("%Y-%m-%d")
        return self.whatsapp_logs[key].get("date") == today_str

    def load_whatsapp_data(self):
        # 1. Load default message template
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.default_whatsapp_text = data.get("default_text", "")
            except Exception:
                self.default_whatsapp_text = ""
        else:
            self.default_whatsapp_text = "Namaste {name}, Achyuta team ki taraf se pranam. Hum aapse follow-up ke regarding connect karna chahte the. Kya hum baat kar sakte hain?"
            self.save_whatsapp_settings(self.default_whatsapp_text)

        # 2. Load sent logs
        if os.path.exists(CAMPAIGN_LOG_FILE):
            try:
                with open(CAMPAIGN_LOG_FILE, "r", encoding="utf-8") as f:
                    self.whatsapp_logs = json.load(f)
            except Exception:
                self.whatsapp_logs = {}
        else:
            self.whatsapp_logs = {}

    def save_whatsapp_settings(self, text):
        self.default_whatsapp_text = text
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump({"default_text": text}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Error saving whatsapp settings:", e)

    def save_whatsapp_logs(self):
        try:
            with open(CAMPAIGN_LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.whatsapp_logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Error saving campaign logs:", e)

    def get_chrome_executable(self):
        paths = [
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return None

    def get_chrome_profiles(self):
        profiles = []
        user_data_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        local_state_path = os.path.join(user_data_path, "Local State")
        temp_dir = tempfile.gettempdir()
        now = time.time()

        if os.path.exists(local_state_path):
            try:
                with open(local_state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                info_cache = data.get("profile", {}).get("info_cache", {})
                
                for dir_name, p_info in info_cache.items():
                    display_name = p_info.get("name", dir_name)
                    email = p_info.get("user_name", "")
                    label = f"{display_name} ({email})" if email else display_name
                    p_path = os.path.join(user_data_path, dir_name)

                    # Calculate activity time from directory or session/history files
                    mtime = 0
                    for fn in ["", "Sessions", "History", "Preferences"]:
                        chk = os.path.join(p_path, fn) if fn else p_path
                        if os.path.exists(chk):
                            try:
                                mtime = max(mtime, os.path.getmtime(chk))
                            except Exception:
                                pass

                    # Extract recent tab/page title from History safely
                    recent_tabs = []
                    hist_file = os.path.join(p_path, "History")
                    if os.path.exists(hist_file):
                        safe_name = dir_name.replace(" ", "_")
                        temp_copy = os.path.join(temp_dir, f"chr_tmp_{safe_name}.db")
                        try:
                            shutil.copy2(hist_file, temp_copy)
                            conn = sqlite3.connect(temp_copy)
                            c = conn.cursor()
                            c.execute("SELECT title, url FROM urls WHERE title != '' ORDER BY last_visit_time DESC LIMIT 2")
                            rows = c.fetchall()
                            recent_tabs = [r[0] for r in rows if r[0]]
                            conn.close()
                            if os.path.exists(temp_copy):
                                os.remove(temp_copy)
                        except Exception:
                            pass

                    # Format human friendly activity time
                    diff = int(now - mtime) if mtime > 0 else 9999999
                    if mtime == 0:
                        activity_text = "Never used"
                    elif diff < 60:
                        activity_text = "Active just now"
                    elif diff < 3600:
                        activity_text = f"Active {diff // 60}m ago"
                    elif diff < 86400:
                        activity_text = f"Active {diff // 3600}h ago"
                    elif diff < 604800:
                        activity_text = f"Active {diff // 86400}d ago"
                    else:
                        activity_text = time.strftime("%d %b", time.localtime(mtime))

                    profiles.append({
                        "dir": dir_name,
                        "name": display_name,
                        "email": email,
                        "label": label,
                        "mtime": mtime,
                        "activity_text": activity_text,
                        "recent_tabs": recent_tabs,
                        "is_recent": (diff < 86400 * 2) # Active in last 48 hours
                    })
            except Exception as e:
                print("Error reading Chrome profiles:", e)

        # Fallback if none parsed
        if not profiles:
            profiles = [{"dir": "Default", "name": "Default Profile", "email": "", "label": "Default Profile", "mtime": 0, "activity_text": "Default", "recent_tabs": [], "is_recent": True}]

        # Sort strictly by last active time descending so recently used Chrome profiles are at the top
        profiles.sort(key=lambda x: x.get("mtime", 0), reverse=True)
        return profiles

    def send_whatsapp_to_client(self, client):
        raw_phone = client.get("phone", "").strip()
        digits = "".join(filter(str.isdigit, raw_phone))
        if not digits:
            messagebox.showwarning("Invalid Phone", f"Client '{client.get('name')}' ka phone number available nahi hai.")
            return

        # Prompt profile selection popup first
        self.open_chrome_profile_picker(client)

    def open_chrome_profile_picker(self, client):
        profiles = self.get_chrome_profiles()

        modal = tk.Toplevel(self)
        modal.title("Select Chrome Profile for WhatsApp")
        modal.geometry("540x580")
        modal.minsize(460, 480)
        modal.config(bg="#ffffff")
        modal.transient(self)
        modal.grab_set()

        head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=20, pady=16)
        head.pack(fill=tk.X)
        tk.Label(head, text="Select Chrome Profile", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(head, text=f"Choose which profile to open WhatsApp Web for {client.get('name')}", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        # Search / Filter Box for Profiles
        search_frame = tk.Frame(modal, bg="#f8fafc", padx=14, pady=8, highlightbackground="#e2e8f0", highlightthickness=1)
        search_frame.pack(fill=tk.X)

        p_search = tk.Entry(search_frame, font=("Segoe UI", 10), bg="#ffffff", fg=C_TEXT_HERO, bd=1, relief=tk.SOLID)
        p_search.pack(fill=tk.X, ipady=4, padx=2)
        p_search.insert(0, "Filter profile by name, tab or email...")
        p_search.config(fg="#94a3b8")

        # Scrollable Profiles List Container
        list_container = tk.Frame(modal, bg="#ffffff")
        list_container.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        p_canvas = tk.Canvas(list_container, bg="#ffffff", bd=0, highlightthickness=0)
        p_vsb = ttk.Scrollbar(list_container, orient="vertical", command=p_canvas.yview)
        p_rows = tk.Frame(p_canvas, bg="#ffffff")

        p_win = p_canvas.create_window((0, 0), window=p_rows, anchor="nw")
        p_canvas.configure(yscrollcommand=p_vsb.set)

        p_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        p_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        p_rows.bind("<Configure>", lambda e: p_canvas.configure(scrollregion=p_canvas.bbox("all")))
        p_canvas.bind("<Configure>", lambda e: p_canvas.itemconfig(p_win, width=e.width))

        def _launch_with_profile(profile_dir):
            modal.destroy()
            self._execute_whatsapp_open(client, profile_dir)

        def _render_profiles(filter_text=""):
            for w in p_rows.winfo_children():
                w.destroy()

            f_lower = filter_text.strip().lower()
            matching = []
            for p in profiles:
                tabs_text = " ".join(p.get("recent_tabs", [])).lower()
                if (not f_lower or 
                    f_lower in p["name"].lower() or 
                    f_lower in p["email"].lower() or 
                    f_lower in p["dir"].lower() or 
                    f_lower in tabs_text):
                    matching.append(p)

            if not matching:
                tk.Label(p_rows, text="No matching profiles found", font=("Segoe UI", 10), fg=C_TEXT_MUTED, bg="#ffffff", pady=20).pack()
                return

            # Group into Recent and Other if no specific search query
            recents = [p for p in matching if p.get("is_recent")]
            others = [p for p in matching if not p.get("is_recent")]

            # If user is searching or only a few profiles exist, display direct list
            sections = []
            if not f_lower and recents:
                sections.append(("Recent Active Chrome Profiles", recents))
                if others:
                    sections.append(("Other Profiles", others))
            else:
                sections.append(("", matching))

            for section_title, p_list in sections:
                if section_title:
                    sec_hdr = tk.Frame(p_rows, bg="#f1f5f9", padx=10, pady=4)
                    sec_hdr.pack(fill=tk.X, pady=(8, 4))
                    tk.Label(sec_hdr, text=section_title.upper(), font=("Segoe UI Semibold", 8), fg=C_TEAL_PRIMARY, bg="#f1f5f9").pack(anchor=tk.W)

                for idx, p in enumerate(p_list):
                    bg_item = "#ffffff" if idx % 2 == 0 else "#f8fafc"
                    item_card = tk.Frame(p_rows, bg=bg_item, highlightbackground="#cbd5e1" if p.get("is_recent") else "#e2e8f0", highlightthickness=1, pady=8, padx=12, cursor="hand2")
                    item_card.pack(fill=tk.X, pady=3)

                    # Left Info Box
                    info_box = tk.Frame(item_card, bg=bg_item)
                    info_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                    # Title row: Name + Activity status badge
                    title_row = tk.Frame(info_box, bg=bg_item)
                    title_row.pack(fill=tk.X, anchor=tk.W)

                    p_name_lbl = tk.Label(title_row, text=p["name"], font=("Segoe UI Semibold", 10), fg=C_TEXT_HERO, bg=bg_item, anchor=tk.W)
                    p_name_lbl.pack(side=tk.LEFT)

                    badge_bg = "#ecfdf5" if p.get("is_recent") else "#f1f5f9"
                    badge_fg = "#059669" if p.get("is_recent") else "#64748b"
                    p_act_lbl = tk.Label(title_row, text=f" {p.get('activity_text', '')} ", font=("Segoe UI Semibold", 7), fg=badge_fg, bg=badge_bg, relief=tk.FLAT, padx=4, pady=1)
                    p_act_lbl.pack(side=tk.LEFT, padx=(8, 0))

                    # Recent Tab Preview row
                    tabs = p.get("recent_tabs", [])
                    if tabs:
                        tab_str = tabs[0]
                        if len(tab_str) > 55:
                            tab_str = tab_str[:52] + "..."
                        p_tab_lbl = tk.Label(info_box, text=f"Recent Tab: {tab_str}", font=("Segoe UI", 8), fg="#0284c7", bg=bg_item, anchor=tk.W)
                        p_tab_lbl.pack(anchor=tk.W, pady=(2, 0))

                    # Sub row: Email / Dir
                    sub_txt = p["email"] if p["email"] else f"Profile: {p['dir']}"
                    p_sub_lbl = tk.Label(info_box, text=sub_txt, font=("Segoe UI", 7), fg="#94a3b8", bg=bg_item, anchor=tk.W)
                    p_sub_lbl.pack(anchor=tk.W, pady=(1, 0))

                    # Open Button
                    open_btn = tk.Button(
                        item_card,
                        text="Open WhatsApp",
                        font=("Segoe UI Semibold", 8),
                        bg=C_TEAL_PRIMARY,
                        fg="#ffffff",
                        activebackground=C_TEAL_DARK,
                        relief=tk.FLAT,
                        bd=0,
                        padx=12,
                        pady=6,
                        cursor="hand2",
                        command=lambda pd=p["dir"]: _launch_with_profile(pd)
                    )
                    open_btn.pack(side=tk.RIGHT, padx=(6, 0))

                    # Card click also launches
                    hover_targets = [item_card, info_box, title_row, p_name_lbl, p_sub_lbl]
                    if tabs:
                        hover_targets.append(p_tab_lbl)

                    for w in hover_targets:
                        w.bind("<Button-1>", lambda e, pd=p["dir"]: _launch_with_profile(pd))
                        w.bind("<Enter>", lambda e, c=item_card, ib=info_box, tr=title_row, nl=p_name_lbl, sl=p_sub_lbl: [
                            c.config(bg="#f0fdfa"), ib.config(bg="#f0fdfa"), tr.config(bg="#f0fdfa"), nl.config(bg="#f0fdfa"), sl.config(bg="#f0fdfa")
                        ])
                        w.bind("<Leave>", lambda e, c=item_card, ib=info_box, tr=title_row, nl=p_name_lbl, sl=p_sub_lbl, ob=bg_item: [
                            c.config(bg=ob), ib.config(bg=ob), tr.config(bg=ob), nl.config(bg=ob), sl.config(bg=ob)
                        ])

        _render_profiles()

        def _on_p_focus_in(e):
            if p_search.get() == "Filter profile by name, tab or email...":
                p_search.delete(0, tk.END)
                p_search.config(fg=C_TEXT_HERO)

        def _on_p_focus_out(e):
            if not p_search.get().strip():
                p_search.insert(0, "Filter profile by name, tab or email...")
                p_search.config(fg="#94a3b8")

        p_search.bind("<FocusIn>", _on_p_focus_in)
        p_search.bind("<FocusOut>", _on_p_focus_out)
        p_search.bind("<KeyRelease>", lambda e: _render_profiles(p_search.get() if p_search.get() != "Filter profile by name, tab or email..." else ""))

    def _execute_whatsapp_open(self, client, profile_dir="Default"):
        raw_phone = client.get("phone", "").strip()
        digits = "".join(filter(str.isdigit, raw_phone))
        if len(digits) == 10:
            formatted_phone = f"91{digits}"
        elif len(digits) > 10 and not digits.startswith("91") and len(digits) == 11 and digits.startswith("0"):
            formatted_phone = f"91{digits[1:]}"
        else:
            formatted_phone = digits

        client_name = client.get("name", "Client")
        msg_template = self.default_whatsapp_text if self.default_whatsapp_text else "Namaste {name}, Achyuta se pranam."
        personalized_msg = msg_template.replace("{name}", client_name).replace("{phone}", raw_phone)

        encoded_text = urllib.parse.quote(personalized_msg)
        wa_url = f"https://web.whatsapp.com/send?phone={formatted_phone}&text={encoded_text}"

        chrome_exe = self.get_chrome_executable()
        if chrome_exe and os.path.exists(chrome_exe):
            try:
                import subprocess
                subprocess.Popen([chrome_exe, f"--profile-directory={profile_dir}", wa_url])
            except Exception as e:
                print("Failed to launch Chrome with profile, fallback to default browser:", e)
                webbrowser.open(wa_url)
        else:
            webbrowser.open(wa_url)

        # Mark as sent today
        now = datetime.now()
        client_key = self.get_client_key(client)
        self.whatsapp_logs[client_key] = {
            "name": client_name,
            "phone": raw_phone,
            "profile": profile_dir,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%I:%M %p"),
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_whatsapp_logs()

        # Update UI in both Clients table and WhatsApp section
        self.render_clients_table()
        if hasattr(self, "refresh_whatsapp_page"):
            self.refresh_whatsapp_page()

    def open_whatsapp_settings_modal(self):
        modal = tk.Toplevel(self)
        modal.title("WhatsApp Message Settings")
        modal.geometry("560x420")
        modal.minsize(500, 360)
        modal.config(bg="#ffffff")
        modal.transient(self)
        modal.grab_set()

        head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=22, pady=18)
        head.pack(fill=tk.X)
        tk.Label(head, text="WhatsApp Message Settings", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(head, text="Configure default message template sent to clients via WhatsApp Web", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(modal, bg="#ffffff", padx=24, pady=18)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text="Default Message Template:", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        tk.Label(body, text="Tip: Use {name} for client name and {phone} for phone number.", font=("Segoe UI", 9), fg=C_TEXT_MUTED, bg="#ffffff").pack(anchor=tk.W, pady=(2, 6))

        text_box = tk.Text(body, font=FONT_DATA, bg="#f8fafc", fg=C_TEXT_HERO, relief=tk.SOLID, bd=1, height=7, padx=10, pady=10)
        text_box.pack(fill=tk.BOTH, expand=True, pady=(4, 16))
        text_box.insert(tk.END, self.default_whatsapp_text)

        def _save():
            new_text = text_box.get("1.0", tk.END).strip()
            self.save_whatsapp_settings(new_text)
            modal.destroy()
            messagebox.showinfo("Saved", "WhatsApp default message template updated successfully!")

        btn_bar = tk.Frame(body, bg="#ffffff")
        btn_bar.pack(fill=tk.X)

        save_btn = tk.Button(btn_bar, text="Save Template", font=FONT_HEAD, bg=C_TEAL_PRIMARY, fg="#ffffff", activebackground=C_TEAL_DARK, activeforeground="#ffffff", relief=tk.FLAT, padx=18, pady=7, cursor="hand2", command=_save)
        save_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(btn_bar, text="Cancel", font=FONT_DATA, bg="#f1f5f9", fg=C_TEXT_BODY, relief=tk.FLAT, padx=14, pady=7, cursor="hand2", command=modal.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=8)

    # =========================================================================
    # WHATSAPP SECTION UI (Campaign & Sent Overview)
    # =========================================================================
    def build_whatsapp_page(self, parent):
        # 1. Top Header with Stats and Minimalist Settings Button
        top_card = tk.Frame(parent, bg=C_CARD, height=74, highlightbackground=C_BORDER, highlightthickness=1)
        top_card.pack(fill=tk.X, padx=20, pady=(18, 12))
        top_card.pack_propagate(False)

        left_info = tk.Frame(top_card, bg=C_CARD)
        left_info.pack(side=tk.LEFT, fill=tk.Y, padx=18, pady=12)

        self.wa_title_lbl = tk.Label(left_info, text="WhatsApp Campaign Hub", font=FONT_BRAND, fg=C_TEXT_HERO, bg=C_CARD)
        self.wa_title_lbl.pack(anchor=tk.W)

        self.wa_subtitle_lbl = tk.Label(left_info, text="Direct 1-click dispatch to WhatsApp Web with automatic tracking", font=("Segoe UI", 9), fg=C_TEXT_MUTED, bg=C_CARD)
        self.wa_subtitle_lbl.pack(anchor=tk.W)

        right_bar = tk.Frame(top_card, bg=C_CARD)
        right_bar.pack(side=tk.RIGHT, fill=tk.Y, padx=18, pady=16)

        # Counter Badge
        self.wa_counter_badge = tk.Label(
            right_bar,
            text="Today Sent: 0",
            font=FONT_HEAD,
            bg=C_TEAL_LIGHT,
            fg=C_TEAL_DARK,
            padx=14,
            pady=6
        )
        self.wa_counter_badge.pack(side=tk.LEFT, padx=(0, 10))

        # Minimalist Settings Text Button
        settings_btn = tk.Button(
            right_bar,
            text="Settings",
            font=FONT_HEAD,
            bg="#f1f5f9",
            fg=C_TEXT_BODY,
            activebackground=C_BORDER,
            activeforeground=C_TEXT_HERO,
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.open_whatsapp_settings_modal
        )
        settings_btn.pack(side=tk.LEFT)

        # Action Button: Floating Mor Pankh Copilot Button
        ai_logo_kw = {"image": self.mor_pankh_btn_photo} if self.mor_pankh_btn_photo else {"image": self.icons["ai"]}
        self.copilot_trigger_wa = tk.Button(
            right_bar,
            **ai_logo_kw,
            bg=C_CARD,
            activebackground=C_CARD,
            relief=tk.FLAT,
            bd=0,
            padx=0,
            pady=0,
            cursor="hand2",
            command=self.toggle_copilot_side_panel
        )
        if self.mor_pankh_btn_hover:
            self.copilot_trigger_wa.bind("<Enter>", lambda e: self.copilot_trigger_wa.config(image=self.mor_pankh_btn_hover))
            self.copilot_trigger_wa.bind("<Leave>", lambda e: self.copilot_trigger_wa.config(image=self.mor_pankh_btn_photo))
        self.copilot_trigger_wa.pack(side=tk.LEFT, padx=(10, 0))

        # 2. Main Two-Column or Tabbed Body: (A) Today's Sent Log (B) All Clients Direct Dispatch
        main_body = tk.Frame(parent, bg=C_CANVAS)
        main_body.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 18))

        # Left Column: Today's Sent Activity Log
        sent_card = tk.Frame(main_body, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        sent_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        sent_head = tk.Frame(sent_card, bg="#f8fafc", height=42, highlightbackground=C_BORDER, highlightthickness=1)
        sent_head.pack(fill=tk.X)
        sent_head.pack_propagate(False)
        tk.Label(sent_head, text="TODAY'S SENT DISPATCH LIST", font=FONT_HEAD, fg="#475569", bg="#f8fafc").pack(side=tk.LEFT, padx=14, pady=10)

        # Sent Log Stage (Zero-Smear Architecture)
        sent_canvas_wrap = tk.Frame(sent_card, bg="#ffffff")
        sent_canvas_wrap.pack(fill=tk.BOTH, expand=True)

        self.sent_canvas = tk.Canvas(sent_canvas_wrap, bg="#ffffff", bd=0, highlightthickness=0)
        self.sent_rows_frame = tk.Frame(self.sent_canvas, bg="#ffffff")
        self.sent_canvas_window = self.sent_canvas.create_window((0, 0), window=self.sent_rows_frame, anchor="nw")

        self.sent_vsb = ttk.Scrollbar(sent_canvas_wrap, orient="vertical")
        self.sent_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sent_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.setup_zero_smear_scroll(self.sent_canvas, self.sent_canvas_window, self.sent_rows_frame, self.sent_vsb)

        # Right Column: Direct Dispatch from Full Clients List
        all_card = tk.Frame(main_body, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        all_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        all_head = tk.Frame(all_card, bg="#f8fafc", height=42, highlightbackground=C_BORDER, highlightthickness=1)
        all_head.pack(fill=tk.X)
        all_head.pack_propagate(False)
        tk.Label(all_head, text="ALL CLIENTS (ONE-CLICK DISPATCH)", font=FONT_HEAD, fg="#475569", bg="#f8fafc").pack(side=tk.LEFT, padx=14, pady=10)

        # Search Bar for WhatsApp Clients list
        wa_search_wrap = tk.Frame(all_card, bg="#f8fafc", height=38, highlightbackground=C_BORDER, highlightthickness=1)
        wa_search_wrap.pack(fill=tk.X)
        wa_search_wrap.pack_propagate(False)

        self.wa_search_placeholder = "Filter clients to message..."
        self.wa_search_entry = tk.Entry(wa_search_wrap, font=("Segoe UI", 9), bg="#ffffff", fg=C_TEXT_HERO, bd=0)
        self.wa_search_entry.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self.wa_search_entry.insert(0, self.wa_search_placeholder)
        self.wa_search_entry.config(fg=C_TEXT_MUTED)

        def _wa_s_in(e):
            val = self.wa_search_entry.get().strip().lower()
            if "filter clients" in val or val == self.wa_search_placeholder.lower():
                self.wa_search_entry.delete(0, tk.END)
                self.wa_search_entry.config(fg=C_TEXT_HERO)

        def _wa_s_out(e):
            if not self.wa_search_entry.get().strip():
                self.wa_search_entry.delete(0, tk.END)
                self.wa_search_entry.insert(0, self.wa_search_placeholder)
                self.wa_search_entry.config(fg=C_TEXT_MUTED)

        self.wa_search_entry.bind("<FocusIn>", _wa_s_in)
        self.wa_search_entry.bind("<FocusOut>", _wa_s_out)
        self.wa_search_entry.bind("<KeyRelease>", lambda e: self.render_wa_all_clients())

        # All Clients Stage (Zero-Smear Architecture)
        all_canvas_wrap = tk.Frame(all_card, bg="#ffffff")
        all_canvas_wrap.pack(fill=tk.BOTH, expand=True)

        self.wa_all_canvas = tk.Canvas(all_canvas_wrap, bg="#ffffff", bd=0, highlightthickness=0)
        self.wa_all_rows_frame = tk.Frame(self.wa_all_canvas, bg="#ffffff")
        self.wa_all_canvas_window = self.wa_all_canvas.create_window((0, 0), window=self.wa_all_rows_frame, anchor="nw")

        self.wa_all_vsb = ttk.Scrollbar(all_canvas_wrap, orient="vertical")
        self.wa_all_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.wa_all_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.setup_zero_smear_scroll(self.wa_all_canvas, self.wa_all_canvas_window, self.wa_all_rows_frame, self.wa_all_vsb)

    def refresh_whatsapp_page(self):
        self.render_wa_sent_list()
        self.render_wa_all_clients()

    def render_wa_sent_list(self):
        for w in self.sent_rows_frame.winfo_children():
            w.destroy()

        today_str = datetime.now().strftime("%Y-%m-%d")
        today_sent = [v for v in self.whatsapp_logs.values() if v.get("date") == today_str]
        today_sent.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        self.wa_counter_badge.config(text=f"Today Sent: {len(today_sent)}")

        if not today_sent:
            empty = tk.Frame(self.sent_rows_frame, bg="#ffffff", pady=40)
            empty.pack(fill=tk.BOTH, expand=True)
            tk.Label(empty, text="No messages sent yet today", font=("Segoe UI Semibold", 11), fg=C_TEXT_MUTED, bg="#ffffff").pack()
            tk.Label(empty, text="Click 'WhatsApp' on any client to send a message via WhatsApp Web.", font=FONT_DATA, fg="#94a3b8", bg="#ffffff").pack(pady=(4, 0))
            return

        for idx, item in enumerate(today_sent):
            bg_c = "#ffffff" if idx % 2 == 0 else "#f8fafc"
            rf = tk.Frame(self.sent_rows_frame, bg=bg_c, height=48, highlightbackground="#f1f5f9", highlightthickness=1)
            rf.pack(fill=tk.X)
            rf.pack_propagate(False)

            # Name and Phone
            c_info = tk.Frame(rf, bg=bg_c)
            c_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=6)

            tk.Label(c_info, text=item.get("name", "Client"), font=("Segoe UI Semibold", 9), fg=C_TEXT_HERO, bg=bg_c, anchor=tk.W).pack(anchor=tk.W)
            tk.Label(c_info, text=item.get("phone", "-"), font=("Segoe UI", 8), fg=C_TEXT_MUTED, bg=bg_c, anchor=tk.W).pack(anchor=tk.W)

            # Time Sent
            t_lbl = tk.Label(rf, text=item.get("time", ""), font=("Segoe UI", 9), fg="#059669", bg=bg_c)
            t_lbl.pack(side=tk.RIGHT, padx=12)

            badge = tk.Label(rf, text="Sent", font=("Segoe UI Bold", 8), bg="#d1fae5", fg="#047857", padx=8, pady=2)
            badge.pack(side=tk.RIGHT, padx=6)

    def render_wa_all_clients(self):
        for w in self.wa_all_rows_frame.winfo_children():
            w.destroy()

        raw_query = self.wa_search_entry.get().strip().lower()
        # Robust placeholder check (catches variations like 2 dots or case differences)
        if not raw_query or "filter clients" in raw_query or raw_query == getattr(self, "wa_search_placeholder", "").lower():
            display_list = self.all_clients[:100]
        else:
            display_list = [
                c for c in self.all_clients
                if raw_query in c.get("name", "").lower() or 
                   raw_query in c.get("phone", "").lower() or 
                   raw_query in c.get("phone", "").replace(" ", "").replace("-", "")
            ][:100]

        if not display_list:
            empty = tk.Frame(self.wa_all_rows_frame, bg="#ffffff", pady=40)
            empty.pack(fill=tk.BOTH, expand=True)
            if not self.all_clients:
                tk.Label(empty, text="Loading client vault...", font=("Segoe UI Semibold", 10), fg=C_TEXT_MUTED, bg="#ffffff").pack()
            else:
                tk.Label(empty, text="No clients match your search", font=("Segoe UI Semibold", 10), fg=C_TEXT_MUTED, bg="#ffffff").pack()
            return

        for idx, client in enumerate(display_list):
            bg_c = "#ffffff" if idx % 2 == 0 else "#f8fafc"
            rf = tk.Frame(self.wa_all_rows_frame, bg=bg_c, height=48, highlightbackground="#f1f5f9", highlightthickness=1)
            rf.pack(fill=tk.X)
            rf.pack_propagate(False)

            c_info = tk.Frame(rf, bg=bg_c)
            c_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=6)

            tk.Label(c_info, text=client.get("name", "Client"), font=("Segoe UI Semibold", 9), fg=C_TEXT_HERO, bg=bg_c, anchor=tk.W).pack(anchor=tk.W)
            tk.Label(c_info, text=client.get("phone", "-"), font=("Segoe UI", 8), fg=C_TEXT_MUTED, bg=bg_c, anchor=tk.W).pack(anchor=tk.W)

            is_sent = self.is_whatsapp_sent_today(client)
            btn_txt = "Sent Today" if is_sent else "Send WhatsApp"
            btn_bg = "#ecfdf5" if is_sent else C_TEAL_PRIMARY
            btn_fg = "#047857" if is_sent else "#ffffff"

            send_b = tk.Button(
                rf,
                text=btn_txt,
                font=("Segoe UI Semibold", 8),
                bg=btn_bg,
                fg=btn_fg,
                activebackground=C_TEAL_DARK,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda c=client: self.send_whatsapp_to_client(c)
            )
            send_b.pack(side=tk.RIGHT, padx=10, pady=10)

    def build_assistant_page(self, parent):
        container = tk.Frame(parent, bg=C_CARD, padx=22, pady=20, highlightbackground=C_BORDER, highlightthickness=1)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(18, 18))

        head_row = tk.Frame(container, bg=C_CARD)
        head_row.pack(fill=tk.X, pady=(0, 12))

        # Title with Mor Pankh icon
        h_left = tk.Frame(head_row, bg=C_CARD)
        h_left.pack(side=tk.LEFT)

        if self.mor_pankh_chat_icon:
            tk.Label(h_left, image=self.mor_pankh_chat_icon, bg=C_CARD).pack(side=tk.LEFT, padx=(0, 8))
        elif self.mor_pankh_btn_photo:
            tk.Label(h_left, image=self.mor_pankh_btn_photo, bg=C_CARD).pack(side=tk.LEFT, padx=(0, 8))

        header_lbl = tk.Label(
            h_left,
            text="Achyuta Agent",
            font=FONT_BRAND,
            fg=C_TEXT_HERO,
            bg=C_CARD
        )
        header_lbl.pack(side=tk.LEFT)

        status_pill = tk.Label(
            head_row,
            text="Universal Omni-Access Active ⚡",
            font=FONT_HEAD,
            bg=C_TEAL_LIGHT,
            fg=C_TEAL_DARK,
            padx=12,
            pady=4
        )
        status_pill.pack(side=tk.RIGHT)

        chat_frame = tk.Frame(container, bg=C_CANVAS, highlightbackground=C_BORDER, highlightthickness=1)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 14))

        self.chat_box = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            font=FONT_CHAT,
            bg=C_CANVAS,
            fg=C_TEXT_HERO,
            insertbackground=C_TEAL_PRIMARY,
            bd=0,
            padx=18,
            pady=18
        )
        self.chat_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sc = ttk.Scrollbar(chat_frame, command=self.chat_box.yview)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_box.config(yscrollcommand=sc.set)

        welcome_text = (
            "Achyuta: Hello! I am your executive agent with full omni-control across Clients, Tasks, Accounts, Employees, WhatsApp, and Focus Timer.\n"
            "You can ask questions, assign any task, record transactions, manage team members, or control timer sessions directly.\n\n"
        )
        self.chat_box.insert(tk.END, welcome_text)
        self.chat_box.config(state=tk.DISABLED)

        input_frame = tk.Frame(container, bg="#ffffff", highlightbackground=C_TEAL_PRIMARY, highlightthickness=1)
        input_frame.pack(fill=tk.X)

        self.entry = tk.Entry(
            input_frame,
            font=FONT_CHAT,
            bg="#ffffff",
            fg=C_TEXT_HERO,
            insertbackground=C_TEAL_PRIMARY,
            bd=0
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(14, 8), ipady=10)
        self.entry.bind("<Return>", self.send_message)

        send_btn = tk.Button(
            input_frame,
            text="Send Message 🦚",
            font=FONT_HEAD,
            bg=C_TEAL_PRIMARY,
            fg="#ffffff",
            activebackground=C_TEAL_DARK,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.send_message
        )
        send_btn.pack(side=tk.RIGHT, padx=4, pady=4)

    # =========================================================================
    # FOCUS TIMER PAGE & WINDOWS PUSH NOTIFICATIONS
    # =========================================================================
    def build_timer_page(self, parent):
        top_card = tk.Frame(parent, bg=C_CARD, height=74, highlightbackground=C_BORDER, highlightthickness=1)
        top_card.pack(fill=tk.X, padx=20, pady=(18, 12))
        top_card.pack_propagate(False)

        left_info = tk.Frame(top_card, bg=C_CARD)
        left_info.pack(side=tk.LEFT, fill=tk.Y, padx=18, pady=12)

        tk.Label(left_info, text="Executive Focus Timer", font=FONT_BRAND, fg=C_TEXT_HERO, bg=C_CARD).pack(anchor=tk.W)
        tk.Label(left_info, text="Deep work & client calling countdown with push alarm alert", font=("Segoe UI", 9), fg=C_TEXT_MUTED, bg=C_CARD).pack(anchor=tk.W)

        # Action Button: Floating Mor Pankh Copilot Button
        ai_logo_kw = {"image": self.mor_pankh_btn_photo} if self.mor_pankh_btn_photo else {"image": self.icons["ai"]}
        self.copilot_trigger_timer = tk.Button(
            top_card,
            **ai_logo_kw,
            bg=C_CARD,
            activebackground=C_CARD,
            relief=tk.FLAT,
            bd=0,
            padx=0,
            pady=0,
            cursor="hand2",
            command=self.toggle_copilot_side_panel
        )
        if self.mor_pankh_btn_hover:
            self.copilot_trigger_timer.bind("<Enter>", lambda e: self.copilot_trigger_timer.config(image=self.mor_pankh_btn_hover))
            self.copilot_trigger_timer.bind("<Leave>", lambda e: self.copilot_trigger_timer.config(image=self.mor_pankh_btn_photo))
        self.copilot_trigger_timer.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 18), pady=16)

        # Main timer presentation card
        timer_card = tk.Frame(parent, bg=C_CARD, highlightbackground=C_BORDER, highlightthickness=1)
        timer_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 18))

        center_box = tk.Frame(timer_card, bg=C_CARD, pady=40)
        center_box.pack(anchor=tk.CENTER, expand=True)

        # Huge Digit Display
        self.timer_digits_lbl = tk.Label(
            center_box,
            text="25:00",
            font=("Segoe UI", 68, "bold"),
            fg=C_TEAL_DARK,
            bg=C_CARD
        )
        self.timer_digits_lbl.pack(pady=(0, 8))

        self.timer_status_lbl = tk.Label(
            center_box,
            text="Ready to Start Session",
            font=("Segoe UI Semibold", 12),
            fg=C_TEXT_MUTED,
            bg=C_CARD
        )
        self.timer_status_lbl.pack(pady=(0, 24))

        # Quick Preset Buttons
        presets_frame = tk.Frame(center_box, bg=C_CARD)
        presets_frame.pack(pady=(0, 24))

        tk.Label(presets_frame, text="Quick Presets: ", font=FONT_HEAD, fg=C_TEXT_BODY, bg=C_CARD).pack(side=tk.LEFT, padx=(0, 8))

        preset_mins = [("5 Mins", 5), ("10 Mins", 10), ("15 Mins", 15), ("25 Mins (Pomodoro)", 25), ("45 Mins", 45)]
        for label, mins in preset_mins:
            btn = tk.Button(
                presets_frame,
                text=label,
                font=("Segoe UI Semibold", 9),
                bg="#f1f5f9",
                fg=C_TEXT_BODY,
                activebackground=C_TEAL_LIGHT,
                activeforeground=C_TEAL_DARK,
                relief=tk.FLAT,
                bd=0,
                padx=12,
                pady=6,
                cursor="hand2",
                command=lambda m=mins: self.set_timer_minutes(m)
            )
            btn.pack(side=tk.LEFT, padx=4)

        # Custom Duration Input Row
        custom_frame = tk.Frame(center_box, bg=C_CARD)
        custom_frame.pack(pady=(0, 30))

        tk.Label(custom_frame, text="Or Set Custom Minutes:", font=FONT_HEAD, fg=C_TEXT_BODY, bg=C_CARD).pack(side=tk.LEFT, padx=(0, 8))
        self.custom_timer_entry = tk.Entry(custom_frame, font=("Segoe UI", 11), width=6, justify="center", relief=tk.SOLID, bd=1, bg="#f8fafc", fg=C_TEXT_HERO)
        self.custom_timer_entry.pack(side=tk.LEFT, padx=(0, 8), ipady=3)
        self.custom_timer_entry.insert(0, "25")

        set_btn = tk.Button(
            custom_frame,
            text="Set",
            font=FONT_HEAD,
            bg="#f1f5f9",
            fg=C_TEXT_BODY,
            activebackground=C_BORDER,
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=4,
            cursor="hand2",
            command=self.apply_custom_timer
        )
        set_btn.pack(side=tk.LEFT)

        # Primary Control Buttons (Start / Pause / Reset)
        ctrl_frame = tk.Frame(center_box, bg=C_CARD)
        ctrl_frame.pack()

        self.timer_start_btn = tk.Button(
            ctrl_frame,
            text="Start Timer",
            font=("Segoe UI", 12, "bold"),
            bg=C_TEAL_PRIMARY,
            fg="#ffffff",
            activebackground=C_TEAL_DARK,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=32,
            pady=10,
            cursor="hand2",
            command=self.toggle_timer
        )
        self.timer_start_btn.pack(side=tk.LEFT, padx=8)

        reset_btn = tk.Button(
            ctrl_frame,
            text="Reset",
            font=("Segoe UI", 12),
            bg="#f1f5f9",
            fg=C_TEXT_BODY,
            activebackground=C_BORDER,
            activeforeground=C_TEXT_HERO,
            relief=tk.FLAT,
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
            command=self.reset_timer
        )
        reset_btn.pack(side=tk.LEFT, padx=8)

        # Default initial set to 25 mins
        self.set_timer_minutes(25)

    def set_timer_minutes(self, minutes):
        if self.timer_is_running:
            self.stop_timer()
        self.timer_initial_seconds = minutes * 60
        self.timer_seconds_left = self.timer_initial_seconds
        self.update_timer_display()
        self.timer_status_lbl.config(text=f"Session set for {minutes} minutes")

    def apply_custom_timer(self):
        val = self.custom_timer_entry.get().strip()
        try:
            mins = int(val)
            if mins <= 0:
                mins = 1
            self.set_timer_minutes(mins)
        except ValueError:
            messagebox.showwarning("Invalid Duration", "Kripya valid numbers me minutes enter karein.")

    def update_timer_display(self):
        mins = self.timer_seconds_left // 60
        secs = self.timer_seconds_left % 60
        self.timer_digits_lbl.config(text=f"{mins:02d}:{secs:02d}")

    def toggle_timer(self):
        if self.timer_is_running:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if self.timer_seconds_left <= 0:
            self.timer_seconds_left = self.timer_initial_seconds or 25 * 60
        self.timer_is_running = True
        self.timer_start_btn.config(text="Pause Timer", bg="#d97706")
        self.timer_status_lbl.config(text="Focus Session in Progress...", fg="#059669")
        self._timer_tick()

    def stop_timer(self):
        self.timer_is_running = False
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        self.timer_start_btn.config(text="Resume Timer", bg=C_TEAL_PRIMARY)
        self.timer_status_lbl.config(text="Session Paused", fg=C_TEXT_MUTED)

    def reset_timer(self):
        self.stop_timer()
        self.timer_seconds_left = self.timer_initial_seconds
        self.update_timer_display()
        self.timer_start_btn.config(text="Start Timer", bg=C_TEAL_PRIMARY)
        self.timer_status_lbl.config(text="Ready to Start Session", fg=C_TEXT_MUTED)

    def _timer_tick(self):
        if not self.timer_is_running:
            return
        if self.timer_seconds_left > 0:
            self.timer_seconds_left -= 1
            self.update_timer_display()
            self.timer_after_id = self.after(1000, self._timer_tick)
        else:
            self.timer_is_running = False
            self.timer_start_btn.config(text="Start Timer", bg=C_TEAL_PRIMARY)
            self.timer_status_lbl.config(text="Time Up! Session Completed", fg="#dc2626")
            self.trigger_time_up_notification()

    def trigger_time_up_notification(self):
        # 1. Beep audio tone
        def _play_sound():
            try:
                import winsound
                # Play alert chime
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                for freq in [800, 1000, 1200]:
                    winsound.Beep(freq, 200)
            except Exception:
                pass

        threading.Thread(target=_play_sound, daemon=True).start()

        # 2. Windows Native PowerShell Toast Notification
        def _show_windows_toast():
            try:
                ps_script = (
                    "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null; "
                    "$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
                    "$textNodes = $template.GetElementsByTagName('text'); "
                    "$textNodes.Item(0).AppendChild($template.CreateTextNode('Achyuta: Time Up! ⏱')) > $null; "
                    "$textNodes.Item(1).AppendChild($template.CreateTextNode('Aapka set kiya hua timer complete ho gaya hai.')) > $null; "
                    "$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Achyuta'); "
                    "$notification = [Windows.UI.Notifications.ToastNotification]::new($template); "
                    "$notifier.Show($notification);"
                )
                import subprocess
                subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_script], creationflags=0x08000000)
            except Exception:
                pass

        threading.Thread(target=_show_windows_toast, daemon=True).start()

        # 3. Bring Window to front with High-Priority Pop Alert
        self.deiconify()
        self.lift()
        self.focus_force()
        self.show_floating_timeup_banner()

    def show_floating_timeup_banner(self):
        banner = tk.Toplevel(self)
        banner.title("Time Up!")
        banner.geometry("420x220")
        banner.config(bg="#ffffff")
        banner.transient(self)
        banner.attributes("-topmost", True)

        # Center banner
        self.update_idletasks()
        bx = self.winfo_x() + (self.winfo_width() // 2) - 210
        by = self.winfo_y() + (self.winfo_height() // 2) - 110
        banner.geometry(f"+{max(0, bx)}+{max(0, by)}")

        b_head = tk.Frame(banner, bg="#dc2626", padx=20, pady=14)
        b_head.pack(fill=tk.X)
        tk.Label(b_head, text="TIME UP!", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg="#dc2626").pack(anchor=tk.W)

        b_body = tk.Frame(banner, bg="#ffffff", padx=20, pady=18)
        b_body.pack(fill=tk.BOTH, expand=True)

        tk.Label(b_body, text="Aapka Focus Timer session complete ho chuka hai.", font=FONT_HEAD, fg=C_TEXT_HERO, bg="#ffffff").pack(anchor=tk.W)
        tk.Label(b_body, text="Aap agla task start kar sakte hain ya break le sakte hain.", font=FONT_DATA, fg=C_TEXT_MUTED, bg="#ffffff").pack(anchor=tk.W, pady=(4, 16))

        ok_btn = tk.Button(
            b_body,
            text="Got it",
            font=FONT_HEAD,
            bg=C_TEAL_PRIMARY,
            fg="#ffffff",
            activebackground=C_TEAL_DARK,
            relief=tk.FLAT,
            bd=0,
            padx=24,
            pady=8,
            cursor="hand2",
            command=banner.destroy
        )
        ok_btn.pack(side=tk.RIGHT)

    def load_clients_data(self):
        if os.path.exists(CLIENTS_FILE):
            try:
                with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
                    self.all_clients = json.load(f)
            except Exception as e:
                print("Error loading clients vault JSON:", e)
                self.all_clients = []
        else:
            self.all_clients = []

    def save_clients_data(self):
        try:
            with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.all_clients, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Error saving clients vault JSON:", e)

    def init_data_vault(self):
        # 1. First, instantly display from local JSON cache if already available
        if self.all_clients:
            self.apply_combined_filters()
            if hasattr(self, "refresh_whatsapp_page"):
                self.refresh_whatsapp_page()
            self.hide_skeleton()
        else:
            self.show_skeleton()

        if not DATA_SERVICE_AVAILABLE or not os.path.exists(CREDENTIALS_FILE):
            self.hide_skeleton()
            return

        def _auth():
            try:
                scopes = ["https://www.googleapis.com/auth/spreadsheets"]
                creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
                self.gc = gspread.authorize(creds)
                self.after(200, self.fetch_data_vault)
            except Exception:
                self.after(0, self.hide_skeleton)

        threading.Thread(target=_auth, daemon=True).start()

    def fetch_data_vault(self):
        if not self.gc:
            self.init_data_vault()
            return

        def _load():
            for attempt in range(3):
                try:
                    sh = self.gc.open_by_key(DATA_VAULT_ID)
                    self.current_spreadsheet = sh
                    ws = sh.sheet1
                    raw_rows = ws.get_all_values()

                    cleaned_list = []
                    for i, r in enumerate(raw_rows[1:], start=2):
                        if not any(c.strip() for c in r):
                            continue
                        
                        name = r[0].strip() or (r[14].strip() if len(r)>14 else '') or (r[4].strip() if len(r)>4 else '') or (r[35].strip() if len(r)>35 else '') or (r[36].strip() if len(r)>36 else '') or 'Client'
                        phone = r[1].strip() or (r[7].strip() if len(r)>7 else '') or (r[15].strip() if len(r)>15 else '') or (r[38].strip() if len(r)>38 else '') or (r[42].strip() if len(r)>42 else '') or '-'
                        status = r[8].strip() or (r[9].strip() if len(r)>9 else '') or (r[39].strip() if len(r)>39 else '') or 'New'
                        last_follow = r[10].strip() or (r[16].strip() if len(r)>16 else '') or '-'
                        next_follow = r[11].strip() if len(r)>11 and r[11].strip() else '-'
                        notes = r[6].strip() or (r[40].strip() if len(r)>40 else '') or '-'

                        cid = f"lead_{i}_{phone}"

                        cleaned_list.append({
                            "id": cid,
                            "sheet_row": i,
                            "name": name,
                            "phone": phone,
                            "status": status,
                            "last_followup": last_follow,
                            "next_followup": next_follow,
                            "notes": notes
                        })

                    # Save newly synced list to JSON cache
                    self.all_clients = cleaned_list
                    self.save_clients_data()

                    def _update_ui():
                        self.apply_combined_filters()
                        if hasattr(self, "refresh_whatsapp_page"):
                            self.refresh_whatsapp_page()
                        self.hide_skeleton()

                    self.after(0, _update_ui)
                    return

                except Exception as ex:
                    print(f"Sync attempt {attempt+1} failed:", ex)
                    try:
                        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
                        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
                        self.gc = gspread.authorize(creds)
                    except Exception:
                        pass
                    import time
                    time.sleep(1)

            def _err():
                self.hide_skeleton()
            self.after(0, _err)

        threading.Thread(target=_load, daemon=True).start()

    def sync_client_to_sheet_async(self, action_type, client_data):
        def _bg_sync():
            try:
                if not self.gc:
                    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
                    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
                    self.gc = gspread.authorize(creds)
                
                sh = self.current_spreadsheet or self.gc.open_by_key(DATA_VAULT_ID)
                self.current_spreadsheet = sh
                ws = sh.sheet1

                if action_type == "add":
                    row_idx = len(ws.get_all_values()) + 1
                    client_data["sheet_row"] = row_idx
                    self.save_clients_data()
                    
                    row_values = [
                        client_data.get("name", "Client"),
                        client_data.get("phone", "-"),
                        "", "", "", "",
                        client_data.get("notes", "-"),
                        client_data.get("phone", "-"),
                        client_data.get("status", "New"),
                        "",
                        client_data.get("last_followup", datetime.now().strftime("%Y-%m-%d")),
                        client_data.get("next_followup", "-"),
                        "", "Manual",
                        client_data.get("name", "Client")
                    ]
                    ws.update(range_name=f"A{row_idx}:O{row_idx}", values=[row_values])
                    print(f"Sheet sync: added new client at row {row_idx}")

                elif action_type == "update":
                    row_idx = client_data.get("sheet_row")
                    if not row_idx:
                        # find by matching phone or name
                        c_phone = (client_data.get("phone") or "").replace(" ", "").replace("-", "")
                        c_name = (client_data.get("name") or "").lower()
                        all_vals = ws.get_all_values()
                        for i, r in enumerate(all_vals[1:], start=2):
                            r_phone = "".join(filter(str.isdigit, str(r)))
                            if (c_phone and c_phone in r_phone) or (c_name and c_name in str(r).lower()):
                                row_idx = i
                                client_data["sheet_row"] = row_idx
                                self.save_clients_data()
                                break

                    if row_idx:
                        # Check whether this row is in Meta Ads format (>25 columns) or Standard table
                        row_vals = ws.row_values(row_idx)
                        if len(row_vals) > 20:
                            # Update Meta columns AN (lead_status, col 40) and AO (notes, col 41)
                            # along with Standard columns A (Name), B (Phone), G (Notes), I (Status)
                            ws.update(
                                range_name=f"AN{row_idx}:AO{row_idx}",
                                values=[[client_data.get("status", "New"), client_data.get("notes", "-")]]
                            )
                        # Standard header updates
                        ws.update(
                            range_name=f"A{row_idx}:B{row_idx}",
                            values=[[client_data.get("name", "Client"), client_data.get("phone", "-")]]
                        )
                        ws.update(
                            range_name=f"G{row_idx}:I{row_idx}",
                            values=[[
                                client_data.get("notes", "-"),
                                client_data.get("phone", "-"),
                                client_data.get("status", "New")
                            ]]
                        )
                        ws.update(
                            range_name=f"K{row_idx}:L{row_idx}",
                            values=[[
                                client_data.get("last_followup", "-"),
                                client_data.get("next_followup", "-")
                            ]]
                        )
                        print(f"Sheet sync: updated client at row {row_idx}")

                elif action_type == "delete":
                    row_idx = client_data.get("sheet_row")
                    if not row_idx:
                        c_phone = (client_data.get("phone") or "").replace(" ", "").replace("-", "")
                        c_name = (client_data.get("name") or "").lower()
                        all_vals = ws.get_all_values()
                        for i, r in enumerate(all_vals[1:], start=2):
                            r_phone = "".join(filter(str.isdigit, str(r)))
                            if (c_phone and c_phone in r_phone) or (c_name and c_name in str(r).lower()):
                                row_idx = i
                                break
                    if row_idx:
                        # Clear row cells so index doesn't shift existing rows
                        ws.update(range_name=f"A{row_idx}:O{row_idx}", values=[[""] * 15])
                        print(f"Sheet sync: cleared deleted client at row {row_idx}")

            except Exception as e:
                print("Background Google Sheet live sync error:", e)

        threading.Thread(target=_bg_sync, daemon=True).start()

    # ==========================================
    # ASSISTANT DIALOGUE
    # ==========================================
    def append_chat(self, sender, message):
        self.chat_box.config(state=tk.NORMAL)
        if sender == "You":
            self.chat_box.insert(tk.END, f"👤 {sender}:\n{message}\n\n")
        else:
            self.chat_box.insert(tk.END, f"🦚 {sender}:\n{message}\n\n")
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def speak(self, text):
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception as e:
                print("TTS error:", e)

    def send_message(self, event=None):
        msg = self.entry.get().strip()
        if not msg:
            return
        self.entry.delete(0, tk.END)
        self.append_chat("You", msg)
        
        self.append_chat("Achyuta", "Thinking... 💭")

        def _fetch_ai_reply():
            response, _ = self.process_ai_leads_intent(msg)
            def _update():
                self.chat_box.config(state=tk.NORMAL)
                content = self.chat_box.get("1.0", tk.END)
                target = "🦚 Achyuta:\nThinking... 💭\n\n"
                if target in content:
                    idx = content.rfind(target)
                    self.chat_box.delete(f"1.0 + {idx} chars", tk.END)
                self.chat_box.config(state=tk.DISABLED)

                self.append_chat("Achyuta", response)
                threading.Thread(target=self.speak, args=(response,), daemon=True).start()

            self.after(0, _update)

        threading.Thread(target=_fetch_ai_reply, daemon=True).start()

    def get_achyuta_response(self, query):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{AI_MODEL}:generateContent?key={AI_API_KEY}"
            sheet_info = f"Current active clients database has {len(self.all_clients)} verified client records."
            
            system_instruction = (
                "You are 'Achyuta AI', a modern, highly capable, and polite Business & Life Assistant inspired by Bhagwan Vishnu's infallible essence. "
                "You help users manage clients, follow-ups, sales strategies, calling scripts, and tasks. "
                "Respond in natural, clean Hinglish or English/Hindi as preferred. "
                "Keep answers simple, clear, actionable, and friendly. "
                f"{sheet_info}"
            )

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"Instruction: {system_instruction}\nUser Query: {query}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 800
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=12) as response:
                result = json.loads(response.read().decode("utf-8"))
                reply = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                return reply

        except Exception as e:
            return f"Achyuta AI: Offline network notice ({str(e)[:45]}). Kripya internet connection check karein."


    # =========================================================================
    # ACHYUTA AI EXECUTIVE ASSISTANT SIDE PANEL
    # =========================================================================
    def build_copilot_side_panel(self):
        # 1. Header (Minimalist, Sober & Clean)
        header = tk.Frame(self.copilot_side_frame, bg="#ffffff", padx=20, pady=16, highlightbackground="#f1f5f9", highlightthickness=1)
        header.pack(fill=tk.X)

        h_left = tk.Frame(header, bg="#ffffff")
        h_left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        title_row = tk.Frame(h_left, bg="#ffffff")
        title_row.pack(anchor=tk.W)

        # Achyuta Logo Icon
        if self.mor_pankh_chat_icon:
            tk.Label(title_row, image=self.mor_pankh_chat_icon, bg="#ffffff").pack(side=tk.LEFT, padx=(0, 8))
        elif self.mor_pankh_btn_photo:
            tk.Label(title_row, image=self.mor_pankh_btn_photo, bg="#ffffff").pack(side=tk.LEFT, padx=(0, 8))
        else:
            tk.Label(title_row, image=self.icons["ai"], bg="#ffffff").pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(title_row, text="Achyuta", font=("Segoe UI", 13, "bold"), fg="#0f172a", bg="#ffffff").pack(side=tk.LEFT)

        # Close Drawer Button
        close_drawer_btn = tk.Button(
            header,
            text="✕",
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#94a3b8",
            activebackground="#f8fafc",
            activeforeground="#0f172a",
            bd=0,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.toggle_copilot_side_panel
        )
        close_drawer_btn.pack(side=tk.RIGHT)

        # 2. Main Stage (Holds Chat Feed + Centered Suggestions Overlay)
        self.copilot_chat_stage = tk.Frame(self.copilot_side_frame, bg="#ffffff")
        self.copilot_chat_stage.pack(fill=tk.BOTH, expand=True, padx=16, pady=(8, 0))

        self.copilot_chat = tk.Text(
            self.copilot_chat_stage,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#1e293b",
            bd=0,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            selectbackground="#e2e8f0",
            cursor="xterm"
        )
        self.copilot_chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        chat_sc = ttk.Scrollbar(self.copilot_chat_stage, orient="vertical", command=self.copilot_chat.yview)
        chat_sc.pack(side=tk.RIGHT, fill=tk.Y)
        self.copilot_chat.config(yscrollcommand=chat_sc.set)

        # Typography tags for readable communication
        self.copilot_chat.tag_configure("center_align", justify="center")
        self.copilot_chat.tag_configure("user_label", font=("Segoe UI Semibold", 9), foreground="#64748b", spacing1=14, spacing3=2, lmargin1=4, lmargin2=4)
        self.copilot_chat.tag_configure("user_text", font=("Segoe UI", 10), foreground="#0f172a", spacing1=2, spacing3=10, lmargin1=4, lmargin2=4)
        
        self.copilot_chat.tag_configure("ai_label", font=("Segoe UI Semibold", 9), foreground="#0f766e", spacing1=14, spacing3=2, lmargin1=4, lmargin2=4)
        self.copilot_chat.tag_configure("ai_text", font=("Segoe UI", 10), foreground="#1e293b", spacing1=2, spacing3=10, lmargin1=4, lmargin2=4)
        self.copilot_chat.tag_configure("thinking_text", font=("Segoe UI Italic", 9), foreground="#94a3b8", spacing1=2, spacing3=6, lmargin1=4, lmargin2=4)
        self.copilot_chat.config(state="disabled")

        # 3. Suggestions Centered Exactly in the Middle of Chat Area
        self.copilot_center_box = tk.Frame(self.copilot_chat_stage, bg="#ffffff")
        self.copilot_center_box.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92)

        # Central Avatar & Welcoming Heading
        center_head = tk.Frame(self.copilot_center_box, bg="#ffffff")
        center_head.pack(pady=(0, 6))

        if self.mor_pankh_btn_photo:
            tk.Label(center_head, image=self.mor_pankh_btn_photo, bg="#ffffff").pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(center_head, text="Achyuta", font=("Segoe UI", 16, "bold"), fg="#0f172a", bg="#ffffff").pack(side=tk.LEFT)

        total_cnt = len(self.all_clients)
        tk.Label(
            self.copilot_center_box,
            text=f"Ready to assist with your {total_cnt} client leads.",
            font=("Segoe UI", 9),
            fg="#64748b",
            bg="#ffffff"
        ).pack(pady=(0, 16))

        # Centered Sober Action Prompts
        suggestions = [
            ("⚡  Who needs a follow-up today?", "Who needs a follow-up today?"),
            ("📋  What are the urgent pending tasks?", "What are the urgent pending tasks?"),
            ("💰  Show current total income and expense balance", "Show current total income and expense balance"),
            ("⏱️  Start a 15 minute focus timer", "Start a 15 minute focus timer")
        ]

        def _apply_centered_prompt(txt):
            self.copilot_input.delete(0, tk.END)
            self.copilot_input.insert(0, txt)
            self.dispatch_copilot_panel_query()

        for chip_lbl, p_text in suggestions:
            btn = tk.Button(
                self.copilot_center_box,
                text=chip_lbl,
                font=("Segoe UI", 9),
                bg="#f8fafc",
                fg="#334155",
                activebackground="#f1f5f9",
                activeforeground="#0f172a",
                highlightbackground="#e2e8f0",
                highlightthickness=1,
                relief=tk.SOLID,
                bd=0,
                padx=14,
                pady=7,
                anchor="w",
                cursor="hand2",
                command=lambda pt=p_text: _apply_centered_prompt(pt)
            )
            btn.pack(fill=tk.X, pady=4)

        # 4. Refined Rounded Pill Prompt Window at Bottom with Gray Border & Circular Send Button
        input_container = tk.Frame(self.copilot_side_frame, bg="#ffffff", padx=16, pady=16)
        input_container.pack(fill=tk.X, side=tk.BOTTOM)

        # Canvas-based smooth rounded pill (gray border, perfect curved corners)
        self.input_canvas = tk.Canvas(input_container, bg="#ffffff", bd=0, highlightthickness=0, height=48)
        self.input_canvas.pack(fill=tk.X)

        self.copilot_input_placeholder = "Ask anything or assign tasks..."

        # Generate custom circular send button icons (ChatGPT / Claude upward arrow style)
        def _render_circle_send_icon(size=30, bg_color="#0f766e", fg_color="#ffffff"):
            scale = 4
            s = size * scale
            im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.ellipse([0, 0, s - 1, s - 1], fill=bg_color)
            cx, cy = s / 2, s / 2
            shaft_len = s * 0.22
            head_size = s * 0.16
            lw = max(2, int(2.2 * scale))
            d.line([(cx, cy + shaft_len * 0.8), (cx, cy - shaft_len)], fill=fg_color, width=lw)
            top_y = cy - shaft_len
            d.line([(cx - head_size, top_y + head_size), (cx, top_y)], fill=fg_color, width=lw)
            d.line([(cx + head_size, top_y + head_size), (cx, top_y)], fill=fg_color, width=lw)
            return ImageTk.PhotoImage(im.resize((size, size), Image.Resampling.LANCZOS))

        self.send_icon_normal = _render_circle_send_icon(size=30, bg_color="#0f766e", fg_color="#ffffff")
        self.send_icon_hover = _render_circle_send_icon(size=30, bg_color="#115e59", fg_color="#ffffff")
        self.send_icon_disabled = _render_circle_send_icon(size=30, bg_color="#cbd5e1", fg_color="#ffffff")

        self.copilot_send_btn = tk.Button(
            self.input_canvas,
            image=self.send_icon_normal,
            bg="#f8fafc",
            activebackground="#f8fafc",
            bd=0,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.dispatch_copilot_panel_query
        )
        self.copilot_send_btn.bind("<Enter>", lambda e: self.copilot_send_btn.config(image=self.send_icon_hover))
        self.copilot_send_btn.bind("<Leave>", lambda e: self.copilot_send_btn.config(image=self.send_icon_normal))

        self.copilot_input = tk.Entry(
            self.input_canvas,
            font=("Segoe UI", 10),
            bg="#f8fafc",
            fg="#94a3b8",
            bd=0,
            relief=tk.FLAT,
            insertbackground="#0f766e"
        )
        self.copilot_input.insert(0, self.copilot_input_placeholder)

        self.input_entry_win = self.input_canvas.create_window(20, 24, window=self.copilot_input, anchor="w")
        self.input_btn_win = self.input_canvas.create_window(360, 24, window=self.copilot_send_btn, anchor="center")

        def _draw_pill_bg(border_color="#cbd5e1"):
            self.input_canvas.delete("pill_bg")
            w = self.input_canvas.winfo_width()
            h = 48
            if w <= 10:
                return
            r = (h - 4) // 2
            x1, y1, x2, y2 = 2, 2, w - 2, h - 2
            pts = [
                x1+r, y1, x1+r, y1,
                x2-r, y1, x2-r, y1,
                x2, y1, x2, y1+r,
                x2, y1+r, x2, y2-r,
                x2, y2-r, x2, y2,
                x2-r, y2, x2-r, y2,
                x1+r, y2, x1+r, y2,
                x1, y2, x1, y2-r,
                x1, y2-r, x1, y1+r,
                x1, y1+r, x1, y1
            ]
            self.input_canvas.create_polygon(pts, fill="#f8fafc", outline=border_color, width=1, smooth=True, tags="pill_bg")
            self.input_canvas.tag_lower("pill_bg")

        def _on_canvas_resize(event):
            w = event.width
            if w <= 10:
                return
            _draw_pill_bg(border_color="#cbd5e1")
            self.input_canvas.coords(self.input_entry_win, 20, 24)
            self.input_canvas.itemconfigure(self.input_entry_win, width=max(10, w - 74))
            self.input_canvas.coords(self.input_btn_win, w - 24, 24)

        self.input_canvas.bind("<Configure>", _on_canvas_resize)

        def _on_input_focus_in(event):
            if self.copilot_input.get().strip() == self.copilot_input_placeholder:
                self.copilot_input.delete(0, tk.END)
                self.copilot_input.config(fg="#0f172a")
            _draw_pill_bg(border_color="#0f766e")

        def _on_input_focus_out(event):
            if not self.copilot_input.get().strip():
                self.copilot_input.insert(0, self.copilot_input_placeholder)
                self.copilot_input.config(fg="#94a3b8")
            _draw_pill_bg(border_color="#cbd5e1")

        self.copilot_input.bind("<FocusIn>", _on_input_focus_in)
        self.copilot_input.bind("<FocusOut>", _on_input_focus_out)
        self.copilot_input.bind("<Return>", lambda e: self.dispatch_copilot_panel_query())

    def toggle_copilot_side_panel(self):
        # Prevent glitchy overlapping triggers while sliding
        if getattr(self, "copilot_is_animating", False):
            return

        if self.copilot_anim_id:
            self.after_cancel(self.copilot_anim_id)
            self.copilot_anim_id = None

        self.update_idletasks()
        total_w = self.winfo_width()
        w = self.copilot_panel_width
        self.copilot_is_animating = True

        if not self.copilot_is_open:
            self.copilot_side_frame.lift()
            self._run_drawer_slide(
                start_x=total_w,
                target_x=total_w - w,
                step_idx=0,
                total_steps=8,
                on_complete=lambda: self._finish_drawer_transition(True)
            )
        else:
            curr_x = self.copilot_side_frame.winfo_x()
            if curr_x < 0 or curr_x > total_w:
                curr_x = total_w - w
            self._run_drawer_slide(
                start_x=curr_x,
                target_x=total_w,
                step_idx=0,
                total_steps=7,
                on_complete=lambda: self._finish_drawer_transition(False)
            )

    def _finish_drawer_transition(self, opened):
        self.copilot_is_open = opened
        self.copilot_is_animating = False
        if opened:
            self.copilot_input.focus_set()
        else:
            self.copilot_side_frame.place_forget()

    def _run_drawer_slide(self, start_x, target_x, step_idx, total_steps, on_complete=None):
        step_idx += 1
        t = step_idx / total_steps
        ease = 1 - (1 - t) * (1 - t)
        curr_x = int(start_x + (target_x - start_x) * ease)
        
        self.copilot_side_frame.place(x=curr_x, y=0, width=self.copilot_panel_width, relheight=1.0)
        
        if step_idx < total_steps:
            self.copilot_anim_id = self.after(16, lambda: self._run_drawer_slide(start_x, target_x, step_idx, total_steps, on_complete))
        else:
            self.copilot_side_frame.place(x=target_x, y=0, width=self.copilot_panel_width, relheight=1.0)
            self.copilot_anim_id = None
            if on_complete:
                on_complete()

    def dispatch_copilot_panel_query(self):
        q = self.copilot_input.get().strip()
        if not q or q == getattr(self, "copilot_input_placeholder", ""):
            return "break"
        
        # Hide centered suggestions once conversation starts
        if hasattr(self, "copilot_center_box") and self.copilot_center_box.winfo_ismapped():
            self.copilot_center_box.place_forget()

        self.copilot_input.delete(0, tk.END)

        # Show user message
        self.copilot_chat.config(state="normal")
        self.copilot_chat.insert(tk.END, "You\n", "user_label")
        self.copilot_chat.insert(tk.END, f"{q}\n", "user_text")
        
        # Thinking indicator with inline icon
        thinking_tag = f"thinking_{int(time.time()*1000)}"
        if self.mor_pankh_chat_icon:
            self.copilot_chat.image_create(tk.END, image=self.mor_pankh_chat_icon)
            self.copilot_chat.insert(tk.END, " Achyuta\n", "ai_label")
        else:
            self.copilot_chat.insert(tk.END, "Achyuta\n", "ai_label")

        self.copilot_chat.insert(tk.END, "Working on it...\n", (thinking_tag, "thinking_text"))
        self.copilot_chat.see(tk.END)
        self.copilot_chat.config(state="disabled")

        if hasattr(self, "send_icon_disabled"):
            self.copilot_send_btn.config(state="disabled", image=self.send_icon_disabled)
        else:
            self.copilot_send_btn.config(state="disabled")

        def _worker():
            reply, action_data = self.process_ai_leads_intent(q)

            def _update_panel():
                if hasattr(self, "send_icon_normal"):
                    self.copilot_send_btn.config(state="normal", image=self.send_icon_normal)
                else:
                    self.copilot_send_btn.config(state="normal")
                self.copilot_chat.config(state="normal")

                # Remove thinking tag line cleanly
                ranges = self.copilot_chat.tag_ranges(thinking_tag)
                if ranges:
                    self.copilot_chat.delete(ranges[0], ranges[1])

                self.copilot_chat.insert(tk.END, f"{reply}\n", "ai_text")
                self.copilot_chat.see(tk.END)
                self.copilot_chat.config(state="disabled")

                if hasattr(self, "speak"):
                    threading.Thread(target=self.speak, args=(reply,), daemon=True).start()

            self.after(0, _update_panel)

        threading.Thread(target=_worker, daemon=True).start()
        return "break"

    def open_gemini_copilot_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Achyuta Leads AI Copilot")
        modal.geometry("640x700")
        modal.minsize(560, 600)
        modal.config(bg="#ffffff")
        modal.transient(self)

        # Center modal gracefully over parent window
        try:
            self.update_idletasks()
            mx = self.winfo_x() + (self.winfo_width() // 2) - 320
            my = self.winfo_y() + (self.winfo_height() // 2) - 350
            modal.geometry(f"+{max(0, mx)}+{max(0, my)}")
        except Exception:
            pass

        # 1. Google Gemini Header Banner (Minimalist Clean Luxury)
        header = tk.Frame(modal, bg="#ffffff", padx=24, pady=18, highlightbackground="#f1f5f9", highlightthickness=1)
        header.pack(fill=tk.X)

        h_left = tk.Frame(header, bg="#ffffff")
        h_left.pack(side=tk.LEFT)

        title_row = tk.Frame(h_left, bg="#ffffff")
        title_row.pack(anchor=tk.W)

        # AI Sparkle Icon
        tk.Label(title_row, image=self.icons["ai"], bg="#ffffff").pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(title_row, text="Achyuta Leads Intelligence", font=("Segoe UI", 13, "bold"), fg=C_TEXT_HERO, bg="#ffffff").pack(side=tk.LEFT)

        # Gemini-style active status pill
        status_pill = tk.Label(title_row, text=" Live Gemini 2.5 ", font=("Segoe UI Semibold", 8), bg="#ecfdf5", fg="#047857", relief=tk.FLAT, padx=6, pady=2)
        status_pill.pack(side=tk.LEFT, padx=(10, 0))

        sub_lbl = tk.Label(h_left, text="Autonomous CRM agent — query context, modify leads, update funnel & search", font=("Segoe UI", 9), fg="#64748b", bg="#ffffff")
        sub_lbl.pack(anchor=tk.W, pady=(2, 0))

        # Close X icon button
        close_x = tk.Button(header, text="✕", font=("Segoe UI", 11), bg="#ffffff", fg="#94a3b8", activebackground="#f8fafc", activeforeground=C_TEXT_HERO, bd=0, relief=tk.FLAT, cursor="hand2", command=modal.destroy)
        close_x.pack(side=tk.RIGHT)

        # 2. Suggested Prompt Pills (Claude / Gemini Style Quick Action Chips)
        chips_frame = tk.Frame(modal, bg="#f8fafc", padx=20, pady=10, highlightbackground="#e2e8f0", highlightthickness=1)
        chips_frame.pack(fill=tk.X)

        tk.Label(chips_frame, text="Quick Prompts:", font=("Segoe UI Semibold", 8), fg="#64748b", bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 8))

        suggestions = [
            "Follow-up me kaun hai?",
            "Total leads & status",
            "Top lead ne kya bola?",
            "Add Ramesh 9891075410",
            "Show Closed deals"
        ]

        def _apply_chip(prompt_text):
            input_box.delete("1.0", tk.END)
            input_box.insert("1.0", prompt_text)
            _send_query()

        for s_txt in suggestions:
            chip_btn = tk.Button(
                chips_frame,
                text=s_txt,
                font=("Segoe UI", 8),
                bg="#ffffff",
                fg=C_TEXT_BODY,
                activebackground="#f0fdfa",
                activeforeground=C_TEAL_DARK,
                bd=1,
                relief=tk.SOLID,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda st=s_txt: _apply_chip(st)
            )
            chip_btn.pack(side=tk.LEFT, padx=3)

        # 3. Conversational Message Stage (Clean Glassmorphism-style feed)
        chat_stage = tk.Frame(modal, bg="#ffffff", padx=20, pady=14)
        chat_stage.pack(fill=tk.BOTH, expand=True)

        chat_feed = tk.Text(
            chat_stage,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg=C_TEXT_HERO,
            bd=0,
            relief=tk.FLAT,
            padx=12,
            pady=12,
            spacing1=3,
            spacing3=6
        )
        chat_feed.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sc = ttk.Scrollbar(chat_stage, orient="vertical", command=chat_feed.yview)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        chat_feed.config(yscrollcommand=sc.set)

        welcome_msg = (
            "🦚 Achyuta AI:\n"
            f"Pranam! Main aapka autonomous Leads Copilot hoon. "
            f"Aapke paas current database me total {len(self.all_clients)} leads hain.\n\n"
            "Aap mujhse kisi bhi lead ke baare me pooch sakte hain, status update karwa sakte hain, "
            "nayi lead add ya delete karwa sakte hain. Mai turant execute kar dunga.\n"
            "─────────────────────────────────────────\n\n"
        )
        chat_feed.insert(tk.END, welcome_msg)
        chat_feed.config(state="disabled")

        # 4. Premium Gemini-style Rounded Floating Input Pill Box
        input_wrap = tk.Frame(modal, bg="#ffffff", padx=20, pady=12)
        input_wrap.pack(fill=tk.X)

        pill_card = tk.Frame(input_wrap, bg="#f8fafc", highlightbackground="#cbd5e1", highlightthickness=1, padx=12, pady=8)
        pill_card.pack(fill=tk.X)

        input_box = tk.Text(
            pill_card,
            font=("Segoe UI", 10),
            bg="#f8fafc",
            fg=C_TEXT_HERO,
            bd=0,
            relief=tk.FLAT,
            height=2,
            insertbackground=C_TEAL_PRIMARY
        )
        input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 8), pady=2)
        input_box.focus_set()

        send_action_btn = tk.Button(
            pill_card,
            text="Send ✨",
            font=("Segoe UI Semibold", 9),
            bg=C_TEAL_PRIMARY,
            fg="#ffffff",
            activebackground=C_TEAL_DARK,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2"
        )
        send_action_btn.pack(side=tk.RIGHT, pady=2)

        def _send_query(event=None):
            q = input_box.get("1.0", tk.END).strip()
            if not q:
                return "break"
            input_box.delete("1.0", tk.END)

            # Append User message
            chat_feed.config(state="normal")
            chat_feed.insert(tk.END, f"👤 Aap:\n{q}\n\n")
            chat_feed.insert(tk.END, "🦚 Achyuta AI:\nThinking & executing... 💭\n\n")
            chat_feed.see(tk.END)
            chat_feed.config(state="disabled")

            send_action_btn.config(state="disabled", text="Thinking...")

            def _thread_worker():
                reply, action_data = self.process_ai_leads_intent(q)

                def _update_ui():
                    send_action_btn.config(state="normal", text="Send ✨")
                    chat_feed.config(state="normal")
                    
                    content = chat_feed.get("1.0", tk.END)
                    target = "🦚 Achyuta AI:\nThinking & executing... 💭\n\n"
                    if target in content:
                        idx = content.rfind(target)
                        chat_feed.delete(f"1.0 + {idx} chars", tk.END)

                    action_name = action_data.get("action", "query").upper()
                    chat_feed.insert(tk.END, f"🦚 Achyuta AI [{action_name}]:\n{reply}\n\n")
                    chat_feed.see(tk.END)
                    chat_feed.config(state="disabled")

                    # Voice playback in background
                    if hasattr(self, "speak"):
                        threading.Thread(target=self.speak, args=(reply,), daemon=True).start()

                self.after(0, _update_ui)

            threading.Thread(target=_thread_worker, daemon=True).start()
            return "break"

        send_action_btn.config(command=_send_query)
        input_box.bind("<Return>", _send_query)

    def dispatch_ai_leads_command(self):
        # Open the full rich Gemini copilot modal
        self.open_gemini_copilot_modal()

    def process_ai_leads_intent(self, user_prompt):
        # 1. Compile live database snapshot across all modules
        total_leads = len(self.all_clients)
        status_counts = {}
        for c in self.all_clients:
            st = c.get("status", "New").strip()
            status_counts[st] = status_counts.get(st, 0) + 1

        leads_summary = []
        for i, c in enumerate(self.all_clients[:20]):
            leads_summary.append({
                "name": c.get("name", ""),
                "phone": c.get("phone", ""),
                "status": c.get("status", "New"),
                "notes": c.get("notes", "-")
            })

        tasks_summary = []
        for t in getattr(self, "all_tasks", [])[:15]:
            tasks_summary.append({
                "title": t.get("title", ""),
                "status": t.get("status", "Pending"),
                "priority": t.get("priority", "Medium"),
                "client": t.get("client_name", ""),
                "due": t.get("due_date", "")
            })

        acc_summary = []
        for a in getattr(self, "all_transactions", [])[:15]:
            acc_summary.append({
                "type": a.get("type", "Income"),
                "title": a.get("title", ""),
                "amount": a.get("amount", 0),
                "party": a.get("party", "")
            })

        total_income = sum(float(a.get("amount", 0)) for a in getattr(self, "all_transactions", []) if a.get("type") == "Income")
        total_expense = sum(float(a.get("amount", 0)) for a in getattr(self, "all_transactions", []) if a.get("type") in ["Expense", "Salary"])
        net_balance = total_income - total_expense

        emp_summary = []
        for e in getattr(self, "all_employees", [])[:15]:
            emp_summary.append({
                "name": e.get("name", ""),
                "role": e.get("role", ""),
                "status": e.get("status", "Active"),
                "phone": e.get("phone", "")
            })

        timer_mins = getattr(self, "timer_seconds_left", 0) // 60
        timer_secs = getattr(self, "timer_seconds_left", 0) % 60
        timer_running = getattr(self, "timer_is_running", False)

        wa_sent_today = len(getattr(self, "whatsapp_logs", []))

        system_instruction = (
            "You are 'Achyuta', a master autonomous executive agent with complete operational authority over the entire CRM business suite: "
            "Clients (Leads), Tasks, Accounts (Finances/Ledger), Employees (Staff), WhatsApp messaging, and Focus Timer.\n"
            "CRITICAL GUIDELINES:\n"
            "- Always communicate in clean, polite, highly professional English. Do not use Hindi or Hinglish.\n"
            "- Keep answers concise, direct, helpful, and natural.\n"
            "- You can execute actions across ANY module directly based on the user's instructions.\n\n"
            "LIVE CONTEXT SNAPSHOT:\n"
            f"- Clients ({total_leads} total): Statuses={json.dumps(status_counts)}, Sample={json.dumps(leads_summary)}\n"
            f"- Tasks ({len(getattr(self, 'all_tasks', []))} total): Sample={json.dumps(tasks_summary)}\n"
            f"- Accounts: Total Income={total_income}, Total Expense={total_expense}, Net Balance={net_balance}, Recent={json.dumps(acc_summary)}\n"
            f"- Employees ({len(getattr(self, 'all_employees', []))} total): Sample={json.dumps(emp_summary)}\n"
            f"- Focus Timer: Running={timer_running}, Remaining={timer_mins}m {timer_secs}s\n"
            f"- WhatsApp: Sent Today={wa_sent_today}\n\n"
            "POSSIBLE ACTIONS:\n"
            "1. 'add_client': add new client lead (name, phone, status, notes).\n"
            "2. 'delete_client': delete a client (match by name or phone).\n"
            "3. 'update_client_status': update status of a client (e.g. New, Follow-up, Interested, Closed, Called, Lost).\n"
            "4. 'search_clients': filter client list with search keyword.\n"
            "5. 'add_task': create task (title, priority: High/Medium/Low, due_date: YYYY-MM-DD, client_name, notes).\n"
            "6. 'complete_task': mark task completed (match title or client_name).\n"
            "7. 'search_tasks': filter task list with search keyword.\n"
            "8. 'add_transaction': record finance entry (type: Income/Expense/Salary, title, amount: number, party, category, mode: UPI/Cash/Bank).\n"
            "9. 'search_accounts': filter transactions ledger with search keyword.\n"
            "10. 'add_employee': add staff member (name, role, department, phone, email, salary: number, status: Active/On Leave/Probation).\n"
            "11. 'update_employee_status': update employee status (match by name).\n"
            "12. 'search_employees': filter employee directory with keyword.\n"
            "13. 'timer_start': start the focus timer.\n"
            "14. 'timer_pause': pause the focus timer.\n"
            "15. 'timer_reset': reset the focus timer.\n"
            "16. 'timer_set': set timer minutes (provide 'minutes' integer, e.g. 15, 25, 45) and start it.\n"
            "17. 'query': user asks any question about clients, tasks, accounts, employees, whatsapp, timer, or business strategy.\n\n"
            "CRITICAL: Output valid JSON ONLY matching this schema:\n"
            "{\n"
            "  \"action\": \"add_client\" | \"delete_client\" | \"update_client_status\" | \"search_clients\" | \"add_task\" | \"complete_task\" | \"search_tasks\" | \"add_transaction\" | \"search_accounts\" | \"add_employee\" | \"update_employee_status\" | \"search_employees\" | \"timer_start\" | \"timer_pause\" | \"timer_reset\" | \"timer_set\" | \"query\",\n"
            "  \"name\": string or null,\n"
            "  \"phone\": string or null,\n"
            "  \"status\": string or null,\n"
            "  \"notes\": string or null,\n"
            "  \"title\": string or null,\n"
            "  \"priority\": string or null,\n"
            "  \"due_date\": string or null,\n"
            "  \"client_name\": string or null,\n"
            "  \"type\": string or null,\n"
            "  \"amount\": number or null,\n"
            "  \"party\": string or null,\n"
            "  \"category\": string or null,\n"
            "  \"mode\": string or null,\n"
            "  \"role\": string or null,\n"
            "  \"department\": string or null,\n"
            "  \"salary\": number or null,\n"
            "  \"minutes\": number or null,\n"
            "  \"search_keyword\": string or null,\n"
            "  \"response_speech\": \"A concise, polite, natural response in professional English explaining what you found or what action you executed.\"\n"
            "}"
        )

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{AI_MODEL}:generateContent?key={AI_API_KEY}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"Instruction: {system_instruction}\nUser Command: {user_prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 600
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                result = json.loads(response.read().decode("utf-8"))
                raw_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

                if "```json" in raw_text:
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()

                data = json.loads(raw_text)
                action = data.get("action", "query")
                resp_speech = data.get("response_speech", "Command completed successfully.")

                self.after(0, lambda: self._execute_ai_action_on_leads(action, data))
                return resp_speech, data

        except Exception as e:
            # Smart Universal Fallback Logic in Professional English
            low_p = user_prompt.lower()
            
            # Timer commands
            if "timer" in low_p:
                if "start" in low_p or "begin" in low_p:
                    # check for minutes
                    nums = [int(s) for s in low_p.split() if s.isdigit()]
                    if nums:
                        m = nums[0]
                        self.after(0, lambda: self._set_and_start_timer(m))
                        return f"Focus timer set to {m} minutes and started.", {"action": "timer_set", "minutes": m}
                    self.after(0, self.start_timer)
                    return "Focus timer session started.", {"action": "timer_start"}
                elif "stop" in low_p or "pause" in low_p:
                    self.after(0, self.stop_timer)
                    return "Focus timer paused.", {"action": "timer_pause"}
                elif "reset" in low_p:
                    self.after(0, self.reset_timer)
                    return "Focus timer reset to default.", {"action": "timer_reset"}
                else:
                    nums = [int(s) for s in low_p.split() if s.isdigit()]
                    if nums:
                        m = nums[0]
                        self.after(0, lambda: self._set_and_start_timer(m))
                        return f"Focus timer set to {m} minutes and started.", {"action": "timer_set", "minutes": m}

            # Account & Finance queries
            if "income" in low_p or "expense" in low_p or "balance" in low_p or "finance" in low_p:
                speech = f"Financial Summary: Total Income is ₹{total_income:,.2f}, Total Expenses are ₹{total_expense:,.2f}, with a Net Balance of ₹{net_balance:,.2f}."
                return speech, {"action": "query"}

            # Task queries
            if "task" in low_p:
                pending_cnt = sum(1 for t in getattr(self, "all_tasks", []) if t.get("status") == "Pending")
                urgent_cnt = sum(1 for t in getattr(self, "all_tasks", []) if t.get("priority") == "High")
                speech = f"You have {len(getattr(self, 'all_tasks', []))} total tasks recorded, with {pending_cnt} currently pending and {urgent_cnt} flagged as high priority."
                return speech, {"action": "query"}

            # Employee queries
            if "employee" in low_p or "staff" in low_p or "team" in low_p:
                active_emps = sum(1 for e in getattr(self, "all_employees", []) if e.get("status") == "Active")
                speech = f"There are {len(getattr(self, 'all_employees', []))} employees in your team directory, with {active_emps} currently active on duty."
                return speech, {"action": "query"}

            # WhatsApp queries
            if "whatsapp" in low_p or "message" in low_p:
                speech = f"{wa_sent_today} client messages have been dispatched via WhatsApp Web today."
                return speech, {"action": "query"}

            # Leads / Clients queries
            if "how many" in low_p or "total" in low_p or "count" in low_p:
                fu_count = sum(1 for c in self.all_clients if "follow" in c.get("status", "").lower())
                closed_cnt = sum(1 for c in self.all_clients if "close" in c.get("status", "").lower())
                speech = f"There are currently {len(self.all_clients)} leads in total, including {fu_count} in follow-up and {closed_cnt} closed deals."
                return speech, {"action": "query"}

            elif "top" in low_p or "first" in low_p or "who" in low_p:
                fus = [c for c in self.all_clients if "follow" in c.get("status", "").lower()]
                target = fus[0] if fus else (self.all_clients[0] if self.all_clients else None)
                if target:
                    speech = f"The top active lead is '{target.get('name')}' (Phone: {target.get('phone')}). Note: \"{target.get('notes', '-')}\""
                else:
                    speech = "There are currently no active follow-up leads in the pipeline."
                return speech, {"action": "query"}

            return f"Processed query: {user_prompt}. Status updated across all modules.", {"action": "query"}

    def _set_and_start_timer(self, mins):
        if hasattr(self, "set_timer_minutes"):
            self.set_timer_minutes(mins)
        if hasattr(self, "start_timer"):
            self.start_timer()

    def _execute_ai_action_on_leads(self, action, data):
        # --- CLIENTS / LEADS ACTIONS ---
        if action in ["add", "add_client"]:
            name = data.get("name") or "New Client"
            phone = data.get("phone") or "-"
            status = data.get("status") or "New"
            notes = data.get("notes") or "Added via Achyuta Agent"
            new_lead = {
                "id": f"lead_{int(time.time()*1000)}_{phone}",
                "sheet_row": None,
                "name": name,
                "phone": phone,
                "status": status,
                "last_followup": datetime.now().strftime("%Y-%m-%d"),
                "next_followup": "-",
                "notes": notes
            }
            self.all_clients.insert(0, new_lead)
            self.save_clients_data()
            self.apply_combined_filters()
            self.sync_client_to_sheet_async("add", new_lead)

        elif action in ["delete", "delete_client"]:
            name_kw = (data.get("name") or "").lower()
            phone_kw = (data.get("phone") or "").replace(" ", "").replace("-", "")
            target_lead = None
            for c in list(self.all_clients):
                if (name_kw and name_kw in c.get("name", "").lower()) or (phone_kw and phone_kw in c.get("phone", "")):
                    target_lead = c
                    self.all_clients.remove(c)
                    break
            if target_lead:
                self.save_clients_data()
                self.sync_client_to_sheet_async("delete", target_lead)
            self.apply_combined_filters()

        elif action in ["update_status", "update_client_status"]:
            name_kw = (data.get("name") or "").lower()
            new_status = data.get("status") or "Follow-up"
            target_lead = None
            for c in self.all_clients:
                if name_kw and name_kw in c.get("name", "").lower():
                    c["status"] = new_status
                    target_lead = c
                    break
            if target_lead:
                self.save_clients_data()
                self.sync_client_to_sheet_async("update", target_lead)
            self.apply_combined_filters()

        elif action in ["update_notes", "update_client_notes"]:
            name_kw = (data.get("name") or "").lower()
            new_notes = data.get("notes") or ""
            target_lead = None
            for c in self.all_clients:
                if name_kw and name_kw in c.get("name", "").lower():
                    c["notes"] = new_notes
                    target_lead = c
                    break
            if target_lead:
                self.save_clients_data()
                self.sync_client_to_sheet_async("update", target_lead)
            self.apply_combined_filters()

        elif action in ["search", "search_clients"]:
            kw = data.get("search_keyword") or data.get("name") or ""
            if kw and hasattr(self, "search_entry"):
                self.search_entry.delete(0, tk.END)
                self.search_entry.insert(0, kw)
                self.search_entry.config(fg=C_TEXT_HERO)
                self.apply_combined_filters()

        # --- TASKS ACTIONS ---
        elif action == "add_task":
            title = data.get("title") or "New Task"
            priority = data.get("priority") or "Medium"
            due_date = data.get("due_date") or datetime.now().strftime("%Y-%m-%d")
            client_name = data.get("client_name") or "-"
            notes = data.get("notes") or "Created via Achyuta Agent"
            new_t = {
                "id": int(time.time() * 1000),
                "title": title,
                "priority": priority,
                "due_date": due_date,
                "status": "Pending",
                "client_name": client_name,
                "client_phone": "-",
                "assignee": "Achyuta Agent",
                "notes": notes,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            if hasattr(self, "all_tasks"):
                self.all_tasks.insert(0, new_t)
                self.save_tasks()
                self.apply_task_filters()

        elif action == "complete_task":
            t_kw = (data.get("title") or data.get("client_name") or "").lower()
            if hasattr(self, "all_tasks"):
                for t in self.all_tasks:
                    if t_kw and (t_kw in t.get("title", "").lower() or t_kw in t.get("client_name", "").lower()):
                        t["status"] = "Completed"
                        break
                self.save_tasks()
                self.apply_task_filters()

        elif action == "search_tasks":
            kw = data.get("search_keyword") or data.get("title") or ""
            if kw and hasattr(self, "task_search_entry"):
                self.task_search_entry.delete(0, tk.END)
                self.task_search_entry.insert(0, kw)
                self.task_search_entry.config(fg=C_TEXT_HERO)
                self.apply_task_filters()

        # --- ACCOUNTS ACTIONS ---
        elif action == "add_transaction":
            t_type = data.get("type") or "Income"
            title = data.get("title") or "Transaction"
            amt = float(data.get("amount") or 0.0)
            party = data.get("party") or "-"
            cat = data.get("category") or "Operations"
            mode = data.get("mode") or "UPI"
            new_tx = {
                "id": int(time.time() * 1000),
                "type": t_type,
                "title": title,
                "amount": amt,
                "party": party,
                "category": cat,
                "mode": mode,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "notes": "Logged via Achyuta Agent"
            }
            if hasattr(self, "all_transactions"):
                self.all_transactions.insert(0, new_tx)
                self.save_transactions()
                self.apply_account_filters()

        elif action == "search_accounts":
            kw = data.get("search_keyword") or data.get("title") or ""
            if kw and hasattr(self, "acc_search_entry"):
                self.acc_search_entry.delete(0, tk.END)
                self.acc_search_entry.insert(0, kw)
                self.acc_search_entry.config(fg=C_TEXT_HERO)
                self.apply_account_filters()

        # --- EMPLOYEES ACTIONS ---
        elif action == "add_employee":
            name = data.get("name") or "New Employee"
            role = data.get("role") or "Executive"
            dept = data.get("department") or "Operations"
            phone = data.get("phone") or "-"
            email = data.get("email") or "-"
            sal = float(data.get("salary") or 25000.0)
            status = data.get("status") or "Active"
            new_emp = {
                "id": int(time.time() * 1000),
                "name": name,
                "role": role,
                "department": dept,
                "phone": phone,
                "email": email,
                "salary": sal,
                "joining_date": datetime.now().strftime("%Y-%m-%d"),
                "status": status,
                "notes": "Added via Achyuta Agent"
            }
            if hasattr(self, "all_employees"):
                self.all_employees.insert(0, new_emp)
                self.save_employees()
                self.apply_employee_filters()

        elif action == "update_employee_status":
            name_kw = (data.get("name") or "").lower()
            new_status = data.get("status") or "Active"
            if hasattr(self, "all_employees"):
                for e in self.all_employees:
                    if name_kw and name_kw in e.get("name", "").lower():
                        e["status"] = new_status
                        break
                self.save_employees()
                self.apply_employee_filters()

        elif action == "search_employees":
            kw = data.get("search_keyword") or data.get("name") or ""
            if kw and hasattr(self, "emp_search_entry"):
                self.emp_search_entry.delete(0, tk.END)
                self.emp_search_entry.insert(0, kw)
                self.emp_search_entry.config(fg=C_TEXT_HERO)
                self.apply_employee_filters()

        # --- FOCUS TIMER ACTIONS ---
        elif action == "timer_start":
            if hasattr(self, "start_timer"):
                self.start_timer()

        elif action == "timer_pause":
            if hasattr(self, "stop_timer"):
                self.stop_timer()

        elif action == "timer_reset":
            if hasattr(self, "reset_timer"):
                self.reset_timer()

        elif action == "timer_set":
            mins = int(data.get("minutes") or 25)
            self._set_and_start_timer(mins)

    def show_ai_leads_response_modal(self, query, reply, action_data):
        modal = tk.Toplevel(self)
        modal.title("Achyuta Leads AI Executive Response")
        modal.geometry("540x360")
        modal.minsize(460, 300)
        modal.config(bg="#ffffff")
        modal.transient(self)

        head = tk.Frame(modal, bg=C_TEAL_PRIMARY, padx=20, pady=14)
        head.pack(fill=tk.X)
        tk.Label(head, text="Achyuta Leads AI Copilot 🦚", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg=C_TEAL_PRIMARY).pack(anchor=tk.W)
        tk.Label(head, text=f"Query: \"{query}\"", font=("Segoe UI", 9), fg="#e0f2f1", bg=C_TEAL_PRIMARY).pack(anchor=tk.W, pady=(2, 0))

        body = tk.Frame(modal, bg="#ffffff", padx=22, pady=18)
        body.pack(fill=tk.BOTH, expand=True)

        action_name = action_data.get("action", "query").upper()
        act_pill = tk.Label(body, text=f"Action: {action_name}", font=("Segoe UI Bold", 8), bg="#ecfdf5", fg="#047857", padx=8, pady=2)
        act_pill.pack(anchor=tk.W, pady=(0, 10))

        msg_box = tk.Text(body, font=("Segoe UI", 10), bg="#f8fafc", fg=C_TEXT_HERO, relief=tk.SOLID, bd=1, wrap=tk.WORD, padx=12, pady=12)
        msg_box.pack(fill=tk.BOTH, expand=True, pady=(0, 14))
        msg_box.insert(tk.END, reply)
        msg_box.config(state="disabled")

        btn_bar = tk.Frame(body, bg="#ffffff")
        btn_bar.pack(fill=tk.X)

        close_btn = tk.Button(btn_bar, text="Close", font=FONT_HEAD, bg=C_TEAL_PRIMARY, fg="#ffffff", activebackground=C_TEAL_DARK, relief=tk.FLAT, padx=20, pady=6, cursor="hand2", command=modal.destroy)
        close_btn.pack(side=tk.RIGHT)

    def show_ai_leads_quick_insights(self):
        total = len(self.all_clients)
        counts = {}
        for c in self.all_clients:
            st = c.get("status", "New").strip()
            counts[st] = counts.get(st, 0) + 1

        fus = [c for c in self.all_clients if "follow" in c.get("status", "").lower()]
        top_fu = fus[0] if fus else None

        summary = (
            f"📊 LIVE LEADS INSIGHTS:\n\n"
            f"• Total Leads: {total}\n"
            f"• Follow-ups: {counts.get('Follow-up', 0)}\n"
            f"• Called: {counts.get('Called', 0)}\n"
            f"• Interested: {counts.get('Interested', 0)}\n"
            f"• Closed Won: {counts.get('Closed', 0)}\n"
            f"• Lost: {counts.get('Lost', 0)}\n\n"
        )
        if top_fu:
            summary += f"🔥 TOP FOLLOW-UP LEAD:\n• Name: {top_fu.get('name')}\n• Phone: {top_fu.get('phone')}\n• Client Note: \"{top_fu.get('notes', '-')}\"\n• Next Scheduled: {top_fu.get('next_followup', '-')}"
        else:
            summary += "Sabhi leads updated hain!"

        self.show_ai_leads_response_modal("Live Leads Overview", summary, {"action": "query"})


def summon_window(app):
    app.deiconify()
    app.lift()
    app.focus_force()

def start_hotkey_listener(app):
    def on_activate():
        app.after(0, lambda: summon_window(app))
        
    def listen_loop():
        try:
            keyboard.add_hotkey('ctrl+shift+a', on_activate)
        except Exception as e:
            print("Hotkey listener add error:", e)
            
        while True:
            try:
                import time
                time.sleep(1)
            except Exception:
                time.sleep(1)

    t = threading.Thread(target=listen_loop, daemon=True)
    t.start()

if __name__ == "__main__":
    app = AchyutaAssistant()
    
    app.deiconify()
    app.lift()
    app.focus_force()
    
    start_hotkey_listener(app)
    
    app.mainloop()

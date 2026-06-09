import requests
import webbrowser
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal, QRect, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont

# Local imports
from config import save_config
from styles import mk_divider, mk_section, mk_field, mk_btn, mk_msgbox

# ─────────────────────────────────────────────────────────────
# 1. HEADER
# ─────────────────────────────────────────────────────────────
class Header(QWidget):
    nav = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setObjectName("AppHeader")
        self.setStyleSheet("""
            QWidget#AppHeader {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #140D28, stop:0.6 #1A1830, stop:1 #1E1E2E);
                border-bottom: 1px solid #2A2A3E;
            }
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0); lay.setSpacing(0)

        left_spacer = QWidget()
        left_spacer.setStyleSheet("background: transparent; border: none;")
        left_spacer.setFixedSize(32, 28)
        lay.addWidget(left_spacer); lay.addStretch()

        self.t = QLabel("Auto Clicker Pro")
        self.t.setStyleSheet("font-size:16px; font-weight:bold; color:#89B4FA; background:transparent; border:none;")
        self.t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.t); lay.addStretch()

        self.nav_btn = QPushButton("☰")
        self.nav_btn.setStyleSheet("""
            QPushButton { background-color: #313244; color: #CDD6F4; border: 1px solid #45475A; border-radius: 6px; font-size: 14px; font-weight: bold; padding: 4px; min-height: 10px; outline: none; }
            QPushButton:hover { background-color: #45475A; border: 1px solid #89B4FA; }
            QPushButton:pressed { background-color: #181825; border: 1px solid #89B4FA; padding-top: 6px; padding-bottom: 2px; }
        """)
        self.nav_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.nav_btn.setFixedSize(32, 28)
        self.nav_btn.clicked.connect(self.nav)
        lay.addWidget(self.nav_btn)

    def set_nav(self, icon): 
        self.nav_btn.setText(icon)

# ─────────────────────────────────────────────────────────────
# 2. MAIN PAGE
# ─────────────────────────────────────────────────────────────
class MainPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainPage") 
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12); lay.setSpacing(10)

        lay.addWidget(mk_section("TRIGGER SETTINGS", center=True))
        row = QHBoxLayout(); row.setSpacing(10)
        lc = QVBoxLayout(); lc.setSpacing(4)
        lc.addWidget(mk_field("Trigger value >", center=True))
        self.target = QLineEdit("0"); self.target.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lc.addWidget(self.target)
        
        rc = QVBoxLayout(); rc.setSpacing(4)
        rc.addWidget(mk_field("Scan interval (s)", center=True))
        self.interval = QLineEdit("0.5"); self.interval.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rc.addWidget(self.interval)
        row.addLayout(lc); row.addLayout(rc)
        lay.addLayout(row); lay.addWidget(mk_divider())

        lay.addWidget(mk_section("REGIONS", center=True))
        self.region_btn = mk_btn("Select Watch Region", "SecondaryBtn")
        lay.addWidget(self.region_btn)

        rr = QHBoxLayout(); rr.setSpacing(8)
        self.region_lbl = QLabel("Not set")
        self.region_lbl.setStyleSheet("color:#F38BA8; font-size:12px; background:transparent;")
        rr.addWidget(self.region_lbl); rr.addStretch()
        
        self.test_btn = mk_btn("Test Read", "PrimaryBtn"); self.test_btn.setMinimumWidth(80)
        rr.addWidget(self.test_btn); lay.addLayout(rr)

        self.click_btn = mk_btn("Set Click Position", "SecondaryBtn")
        lay.addWidget(self.click_btn)

        self.click_lbl = QLabel("Not set")
        self.click_lbl.setStyleSheet("color:#F38BA8; font-size:12px; background:transparent;")
        lay.addWidget(self.click_lbl); lay.addWidget(mk_divider())

        br = QHBoxLayout(); br.setSpacing(8)
        self.start_btn = mk_btn("START BOT", "SuccessBtn")
        self.stop_btn  = mk_btn("STOP BOT", "DangerBtn"); self.stop_btn.setEnabled(False)
        br.addWidget(self.start_btn); br.addWidget(self.stop_btn)
        lay.addLayout(br)

        self.status_lbl = QLabel("Status: Idle")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color:#6C7086; font-size:12px; background:transparent;")
        lay.addWidget(self.status_lbl); lay.addStretch()

# ─────────────────────────────────────────────────────────────
# 3. SETTINGS PAGE
# ─────────────────────────────────────────────────────────────
class SettingsPage(QWidget):
    saved = pyqtSignal(dict)

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPage") 
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12); lay.setSpacing(12)

        lay.addWidget(mk_field("Discord Webhook URL (For Alerts)", center=True))
        self.webhook_e = QLineEdit(cfg.get("webhook_url", ""))
        self.webhook_e.setPlaceholderText("https://discord.com/api/webhooks/...")
        self.webhook_e.setEchoMode(QLineEdit.EchoMode.Password)
        self.webhook_e.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.webhook_e)

        lay.addWidget(mk_field("Bot Token (For !stop Listener)", center=True))
        self.token_e = QLineEdit(cfg.get("bot_token", ""))
        self.token_e.setPlaceholderText("Paste your bot token here")
        self.token_e.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_e.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.token_e)

        lay.addWidget(mk_field("Command Channel ID (Optional)", center=True))
        self.channel_e = QLineEdit(cfg.get("channel_id", ""))
        self.channel_e.setPlaceholderText("Restrict !stop to this channel")
        self.channel_e.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.channel_e)

        lay.addWidget(mk_field("Your User ID (For Security)", center=True))
        self.uid_e = QLineEdit(cfg.get("user_id", ""))
        self.uid_e.setPlaceholderText("Your Discord user ID")
        self.uid_e.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.uid_e)

        self.test_btn = mk_btn("Send Test Message", "TestBtn")
        self.test_btn.clicked.connect(self._test)
        lay.addWidget(self.test_btn); lay.addStretch()
        
        self.save_btn = mk_btn("Save Settings", "PrimaryBtn")
        self.save_btn.clicked.connect(self._save)
        lay.addWidget(self.save_btn)

    def reload(self, cfg):
        self.webhook_e.setText(cfg.get("webhook_url", ""))
        self.token_e.setText(cfg.get("bot_token", ""))
        self.uid_e.setText(cfg.get("user_id", ""))
        self.channel_e.setText(cfg.get("channel_id", ""))

    def _collect(self):
        return { 
            "webhook_url": self.webhook_e.text().strip(), 
            "bot_token": self.token_e.text().strip(),
            "user_id": self.uid_e.text().strip(),
            "channel_id": self.channel_e.text().strip()
        }

    def _save(self):
        cfg = self._collect(); save_config(cfg); self.saved.emit(cfg)

    def _test(self):
        cfg = self._collect()
        if not cfg["webhook_url"]:
            mk_msgbox(self, "Missing", "Webhook URL is required.", "warning"); return
            
        m = f"<@{cfg['user_id']}>" if cfg["user_id"] else ""
        embed = {
            "title": "✅ Test Message Successful!", "description": "Your Webhook is configured perfectly! 🎉", "color": 5763719,
            "fields": [
                {"name": "Status", "value": "✅ **Ready**", "inline": True},
                {"name": "User ID", "value": f"✅ **{cfg.get('user_id', 'N/A')}**", "inline": True},
            ], "footer": {"text": "Auto-Clicker Pro"}
        }

        p = {"content": f"🔔 {m} **Test Alert!**".strip(), "embeds": [embed]}
        try:
            r = requests.post(cfg["webhook_url"], json=p, timeout=10)
            if r.status_code in (200, 204): mk_msgbox(self, "Success", "Test message sent!", "information")
            else: mk_msgbox(self, "Failed", f"Discord returned {r.status_code}:\n{r.text[:300]}", "warning")
        except Exception as e:
            mk_msgbox(self, "Error", str(e), "critical")

# ─────────────────────────────────────────────────────────────
# 4. SCREEN OVERLAY
# ─────────────────────────────────────────────────────────────
class ScreenOverlay(QWidget):
    region_selected = pyqtSignal(tuple)
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.showFullScreen()
        self.s = self.e = None

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(0,0,0,120))
        if self.s and self.e:
            r = QRect(self.s, self.e).normalized()
            p.fillRect(r, QColor(137,180,250,40))
            p.setPen(QPen(QColor(137,180,250), 2))
            p.drawRect(r)
            p.setBrush(QBrush(QColor(137,180,250)))
            p.setPen(Qt.PenStyle.NoPen)
            for c in [r.topLeft(), r.topRight(), r.bottomLeft(), r.bottomRight()]: 
                p.drawEllipse(c.x()-4, c.y()-4, 8, 8)
        p.setPen(QColor(255,255,255,200))
        p.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        p.drawText(24, 38, "Drag to select region   Esc to cancel")

    def mousePressEvent(self, e): 
        self.s = self.e = e.pos()
        self.update()
        
    def mouseMoveEvent(self, e):  
        self.e = e.pos()
        self.update()
        
    def mouseReleaseEvent(self, e):
        r = QRect(self.s, e.pos()).normalized()
        self.region_selected.emit((r.x(), r.y(), r.width(), r.height()))
        self.close()
        
    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape: 
            self.close()
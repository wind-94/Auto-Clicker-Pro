from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

STYLE = """
#MainWindow, #MainPage, #SettingsPage { background-color: #1E1E2E; }
QLabel { color: #CDD6F4; font-family: 'Segoe UI', sans-serif; }
QLineEdit {
    background-color: #181825; border: 2px solid #313244;
    border-radius: 6px; padding: 6px 10px; color: #A6E3A1;
    font-weight: bold; font-size: 13px; font-family: 'Segoe UI', sans-serif;
}
QLineEdit:hover { border: 2px solid #585B70; background-color: #2A2A3E; }
QLineEdit:focus { border: 2px solid #89B4FA; background-color: #2A2A3E; }
QMessageBox { background-color: #1E1E2E; }
QMessageBox QLabel { color: #CDD6F4; background: transparent; font-size: 13px; }
QMessageBox QPushButton {
    background-color: #89B4FA; color: #11111B;
    min-width: 60px; padding: 6px 12px; border-radius: 6px; 
    font-weight: bold; border: 1px solid #89B4FA; outline: none;
}
QMessageBox QPushButton:hover { background-color: #B4BEFE; border: 1px solid #B4BEFE; }
QMessageBox QPushButton:pressed {
    background-color: #7498D6; border: 1px solid #7498D6;
    padding-top: 8px; padding-bottom: 4px;
}
"""

BTN_COLORS = {
    "PrimaryBtn":   ("#89B4FA", "#B4BEFE", "#7498D6", "#11111B"), 
    "SecondaryBtn": ("#CBA6F7", "#E1C7FF", "#AB8BD2", "#11111B"),
    "TestBtn":      ("#F9E2AF", "#FDEBB3", "#D3BF94", "#11111B"),
    "SuccessBtn":   ("#A6E3A1", "#B5E8B0", "#8CC088", "#11111B"),
    "DangerBtn":    ("#F38BA8", "#F5A1B8", "#CD768E", "#11111B")
}

def mk_divider():
    d = QFrame(); d.setFrameShape(QFrame.Shape.HLine)
    d.setStyleSheet("background-color:#313244; border:none;"); d.setFixedHeight(1)
    return d

def mk_section(text, center=False):
    l = QLabel(text)
    l.setStyleSheet("color:#89B4FA; font-size:11px; font-weight:bold; letter-spacing:1px; background:transparent;")
    if center: l.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return l

def mk_field(text, center=False):
    l = QLabel(text)
    l.setStyleSheet("color:#CDD6F4; font-size:12px; background:transparent; margin-top:2px;")
    if center: l.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return l

def mk_btn(text, style_key):
    b = QPushButton(text)
    bg, hover, pressed, fg = BTN_COLORS.get(style_key, ("#313244", "#45475A", "#181825", "#CDD6F4"))
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg}; color: {fg}; border: 1px solid {bg}; border-radius: 6px;
            font-weight: bold; font-size: 13px; font-family: 'Segoe UI', sans-serif;
            padding: 8px 14px; min-height: 18px; outline: none;
        }}
        QPushButton:hover {{ background-color: {hover}; border: 1px solid {hover}; }}
        QPushButton:pressed {{ background-color: {pressed}; border: 1px solid {pressed}; padding-top: 10px; padding-bottom: 6px; }}
        QPushButton:disabled {{ background-color: #313244; border: 1px solid #313244; color: #585B70; }}
    """)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b

def mk_msgbox(parent, title, message, msg_type="information"):
    msgbox = QMessageBox(parent)
    msgbox.setWindowTitle(title)
    msgbox.setText(message)
    if msg_type == "warning": msgbox.setIcon(QMessageBox.Icon.Warning)
    elif msg_type == "critical": msgbox.setIcon(QMessageBox.Icon.Critical)
    else: msgbox.setIcon(QMessageBox.Icon.Information)
    msgbox.setStandardButtons(QMessageBox.StandardButton.Ok)
    msgbox.setStyleSheet("""
        QMessageBox { background-color: #1E1E2E !important; }
        QMessageBox QLabel { color: #CDD6F4 !important; background: transparent !important; font-size: 13px; }
        QMessageBox QPushButton {
            background-color: #89B4FA !important; color: #11111B !important;
            border: 1px solid #89B4FA !important; border-radius: 6px !important;
            padding: 6px 15px !important; min-width: 80px !important; font-weight: bold !important; font-size: 12px !important;
        }
        QMessageBox QPushButton:hover { background-color: #B4BEFE !important; border: 1px solid #B4BEFE !important; }
        QMessageBox QPushButton:pressed { background-color: #7498D6 !important; border: 1px solid #7498D6 !important; }
    """)
    msgbox.exec()
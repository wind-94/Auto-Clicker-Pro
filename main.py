# -*- coding: utf-8 -*-
import sys, re, time, threading, datetime, multiprocessing, ctypes, os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget, QSystemTrayIcon
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import pyautogui, pytesseract
from PIL import Image, ImageOps
import winsound

# --- Local Component Imports ---
from config import TESSERACT_PATH, OCR_CONFIG, load_config, save_config, ICON_PATH
from styles import STYLE, mk_msgbox
from discord_api import discord_send
from discord_remote import DiscordRemoteBot
from ui_components import Header, MainPage, SettingsPage, ScreenOverlay

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

class App(QWidget):
    # Signals for the background Discord Thread to communicate with the UI safely
    start_signal = pyqtSignal()
    stop_signal = pyqtSignal()
    update_channel_signal = pyqtSignal(str) # Listens for !setchannel
    notify_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow") 
        self.setWindowTitle("Auto Clicker Pro")
        import os
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.setFixedSize(320, 460)  
        self.watch_region = self.click_pos = None
        self.is_running   = False
        self.bot_start    = None
        self.remote_bot   = None
        self.cfg          = load_config()
        self._build()
        self._wire()
        self._boot_listener()
        self.notify_signal.connect(self._show_notification)
        self._setup_tray()

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        import os
        if os.path.exists(ICON_PATH):
            self.tray_icon.setIcon(QIcon(ICON_PATH))
        self.tray_icon.show()

    def _show_notification(self, title, message):
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        self.hdr  = Header(self)
        self.hdr.nav.connect(self._toggle)
        root.addWidget(self.hdr)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color:#1E1E2E;")
        self.main_pg = MainPage(self)
        self.set_pg  = SettingsPage(self.cfg, self)
        
        self.stack.addWidget(self.main_pg)   # 0
        self.stack.addWidget(self.set_pg)    # 1
        root.addWidget(self.stack)

    def _wire(self):
        mp = self.main_pg
        mp.region_btn.clicked.connect(self._sel_region)
        mp.test_btn.clicked.connect(self._test_vision)
        mp.click_btn.clicked.connect(self._set_click)
        mp.start_btn.clicked.connect(self._start)
        mp.stop_btn.clicked.connect(self._stop)
        self.set_pg.saved.connect(self._on_saved)
        
        # Connect Discord bot signals to App actions
        self.start_signal.connect(self._start)
        self.stop_signal.connect(self._stop)
        self.update_channel_signal.connect(self._update_channel_from_bot)

    def _update_channel_from_bot(self, new_channel_id):
        """Called automatically when you type !setchannel in Discord"""
        self.cfg["channel_id"] = new_channel_id
        save_config(self.cfg) # Saves to the encrypted config
        self.set_pg.reload(self.cfg) # Updates the UI text box in real time!

    def _boot_listener(self):
        tok = self.cfg.get("bot_token")
        uid = self.cfg.get("user_id")
        cid = self.cfg.get("channel_id")
        
        if tok and uid and not self.remote_bot:
            self.remote_bot = DiscordRemoteBot(tok, uid, cid, self)
            self.remote_bot.start()

    def _toggle(self):
        if self.stack.currentIndex() == 0:
            self.set_pg.reload(self.cfg)
            self.stack.setCurrentIndex(1)
            self.hdr.set_nav("⬅")
            self.hdr.t.setText("Settings") 
        else:
            self.stack.setCurrentIndex(0)
            self.hdr.set_nav("☰")
            self.hdr.t.setText("Auto-Clicker Pro") 

    def _on_saved(self, cfg):
        self.cfg = cfg
        self._boot_listener() 
        self._toggle()

    def _sel_region(self):
        self.hide()
        self.ov = ScreenOverlay()
        self.ov.region_selected.connect(self._on_region)

    def _on_region(self, r):
        self.watch_region = r
        mp = self.main_pg
        mp.region_lbl.setText("Region: Set")
        mp.region_lbl.setStyleSheet("color:#A6E3A1; font-size:12px; font-weight:bold; background:transparent;")
        self.show()

    def _test_vision(self):
        if not self.watch_region:
            mk_msgbox(self, "Warning", "Select a Watch Region first!", "warning"); return
        try:
            x,y,w,h = self._scaled()
            shot = pyautogui.screenshot(region=(x,y,w,h))
            bw   = self._proc(shot); bw.save("debug_eyes.png")
            nums = re.findall(r'\d+', pytesseract.image_to_string(bw, config=OCR_CONFIG))
            msg  = (f"Detected: <b style='color:#A6E3A1;font-size:16px;'>"
                    f"{max(int(n) for n in nums)}</b>") if nums else \
                   "<b style='color:#F38BA8;'>No number found.</b>"
            mk_msgbox(self, "Test Read", msg, "information")
        except Exception as ex:
            mk_msgbox(self, "Error", str(ex), "critical")

    def _set_click(self):
        mp = self.main_pg
        for i in (3,2,1):
            mp.click_lbl.setText(f"Move cursor to target... {i}")
            mp.click_lbl.setStyleSheet("color:#F9E2AF; font-size:12px; background:transparent;")
            QApplication.processEvents(); time.sleep(1)
        x,y = pyautogui.position()
        self.click_pos = (x,y)
        mp.click_lbl.setText("Click Pos: Set")
        mp.click_lbl.setStyleSheet("color:#A6E3A1; font-size:12px; font-weight:bold; background:transparent;")

    def _start(self):
        mp = self.main_pg
        if not self.watch_region or not self.click_pos:
            mk_msgbox(self,"Setup Incomplete", "Set the watch region and click position first.", "warning"); return
        try:
            self.tgt = int(mp.target.text())
            self.ivl = max(0.05, float(mp.interval.text()))
        except ValueError:
            mk_msgbox(self,"Invalid","Target and interval must be numbers.", "warning"); return

        self.is_running = True; self.bot_start = time.time()
        mp.start_btn.setEnabled(False); mp.stop_btn.setEnabled(True)
        mp.status_lbl.setText("Status:  Running")
        mp.status_lbl.setStyleSheet("color:#A6E3A1; font-size:12px; font-weight:bold; background:transparent;")
        threading.Thread(target=self._loop, daemon=True).start()

    def _stop(self):
        self.is_running = False
        mp = self.main_pg
        mp.start_btn.setEnabled(True); mp.stop_btn.setEnabled(False)
        mp.status_lbl.setText("Status: Idle")
        mp.status_lbl.setStyleSheet("color:#6C7086; font-size:12px; background:transparent;")

    def _scaled(self):
        r = self.devicePixelRatioF()
        x,y,w,h = self.watch_region
        return int(x*r),int(y*r),int(w*r),int(h*r)

    def _proc(self, img):
        img = img.resize((img.width*3, img.height*3), Image.Resampling.LANCZOS)
        g   = ImageOps.grayscale(img)
        return ImageOps.invert(g).point(lambda v: 0 if v<150 else 255, "1")

    def _loop(self):
        while self.is_running:
            try:
                x,y,w,h = self._scaled()
                bw   = self._proc(pyautogui.screenshot(region=(x,y,w,h)))
                nums = re.findall(r'\d+', pytesseract.image_to_string(bw, config=OCR_CONFIG))
                if nums:
                    val = max(int(n) for n in nums)
                    print(f"[BOT] {val}")
                    if val > self.tgt:
                        pyautogui.click(*self.click_pos)
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)

                        # --- 1. SEND NATIVE WINDOWS NOTIFICATION ---
                        # This safely tells the main UI to pop the message
                        self.notify_signal.emit("Auto-Clicker Triggered!", f"Value {val} > {self.tgt}")

                        # --- 2. SEND DISCORD MESSAGE ---
                        url = self.cfg.get("webhook_url","")
                        if url:
                            try:
                                dur = str(datetime.timedelta(seconds=int(time.time()-self.bot_start)))
                                ts  = int(time.time())
                                t12 = datetime.datetime.now().strftime("%I:%M %p")
                                discord_send(url, self.cfg.get("user_id",""), val, self.tgt, dur, t12, ts)
                            except Exception as ex:
                                print(f"[BOT] Discord error: {ex}")
                        time.sleep(3)
                time.sleep(self.ivl)
            except Exception as ex:
                print(f"[BOT] Error: {ex}"); time.sleep(self.ivl)

if __name__ == "__main__":
    # --- CRITICAL FIX: Stops PyInstaller from spawning infinite background loops ---
    multiprocessing.freeze_support() 
    
    # --- TASKBAR ICON FIX: Forces Windows to use your custom logo ---
    try:
        myappid = 'Auto Clicker Pro' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    app.setStyleSheet(STYLE)
    app.setFont(QFont("Segoe UI", 10))
    
    # Make sure the QApplication itself is loading the icon from your config
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))
        
    w = App(); w.show()
    sys.exit(app.exec())
#!/usr/bin/env python3
import sys
import socket
import os
import threading
import json
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QPalette

class LotusOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_socket()

    def init_ui(self):
        # Window flags: Frameless, Always on Top, Tool window (no taskbar icon), Click-through
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool | 
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Layout and Label
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Lotus Overlay")
        self.label.setAlignment(Qt.AlignCenter)
        
        # High contrast style
        self.label.setStyleSheet("""
            QLabel {
                color: #FFFFFF; /* White */
                background-color: rgba(0, 0, 0, 220); /* Solid black-ish */
                border-radius: 12px;
                padding: 15px;
            }
        """)
        self.font = QFont("Inter", 32) # Moderate font size
        self.label.setFont(self.font)
        
        self.layout.addWidget(self.label)
        
        # Animation for fading
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        
        # Timer to hide after inactivity
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)

        # Initial state
        self.setWindowOpacity(0)
        self.show()
        
        # Position: Top center
        screen = QApplication.primaryScreen().geometry()
        self.resize(screen.width() // 3, 100)
        self.move((screen.width() - self.width()) // 2, screen.height() - 150)

    def display_text(self, text):
        if not text:
            self.fade_out()
            return
            
        self.label.setText(text)
        self.adjustSize()
        # Recenter after resize
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, screen.height() - 150)
        
        self.fade_in()
        self.hide_timer.start(2500) # Show for 2.5 seconds

    def fade_in(self):
        self.anim.stop()
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(1.0)
        self.anim.start()

    def fade_out(self):
        self.anim.stop()
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(0.0)
        self.anim.start()

    def setup_socket(self):
        # For prototype, use a simple Unix socket in /tmp
        self.socket_path = "/tmp/lotus-overlay-proto.sock"
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.socket_path)
        self.server.listen(1)
        
        # Run socket listener in a separate thread
        self.thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.thread.start()

    def listen_loop(self):
        while True:
            conn, _ = self.server.accept()
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    msg = data.decode('utf-8').strip()
                    # Trigger UI update from main thread
                    QTimer.singleShot(0, lambda m=msg: self.display_text(m))
            except Exception as e:
                print(f"Socket error: {e}")
            finally:
                conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = LotusOverlay()
    
    # Simple test command:
    # echo "Hello Lotus" | socat - UNIX-CONNECT:/tmp/lotus-overlay-proto.sock
    
    sys.exit(app.exec())

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QTabWidget, QLabel, QStatusBar)
from PySide6.QtGui import QIcon

from ui.wifi_tab import WifiTab
from ui.network_tab import NetworkTab
from ui.test_tab import TestTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyWiFiman")
        self.resize(1000, 700)
        
        self.init_ui()
        self.apply_stylesheet()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(WifiTab(), "Wi-Fi Scanner")
        self.tabs.addTab(NetworkTab(), "Local Network")
        self.tabs.addTab(TestTab(), "Speed & Latency")
        
        layout.addWidget(self.tabs)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def closeEvent(self, event):
        """Handle application closure to stop all threads safely."""
        # Stop WifiTab worker
        if hasattr(self.tabs.widget(0), 'worker'):
            self.tabs.widget(0).worker.stop()
            self.tabs.widget(0).worker.wait(1000) # Wait up to 1s
        
        # Stop TestTab workers
        test_tab = self.tabs.widget(2)
        if hasattr(test_tab, 'ping_google'):
            test_tab.ping_google.stop()
            test_tab.ping_google.wait(1000)
        
        if hasattr(test_tab, 'speed_worker') and test_tab.speed_worker:
            test_tab.speed_worker.terminate() # Speedtest is blocking, terminate might be needed if it hangs
            test_tab.speed_worker.wait(1000)
        
        # Accept close event
        event.accept()

    def apply_stylesheet(self):
        # Modern Dark Theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #333;
            }
            QTabBar::tab {
                background: #444;
                color: #bbb;
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #007acc;
                color: white;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0062a3;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            QTableWidget {
                background-color: #333;
                gridline-color: #555;
                border: none;
            }
            QHeaderView::section {
                background-color: #444;
                color: white;
                padding: 6px;
                border: none;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 4px;
                text-align: center;
                background-color: #333;
            }
            QProgressBar::chunk {
                background-color: #007acc;
            }
        """)

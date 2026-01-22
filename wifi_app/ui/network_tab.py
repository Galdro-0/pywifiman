from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QLabel,
                               QHBoxLayout, QPushButton, QProgressBar)
from PySide6.QtCore import QThread, Signal

from services.network_scanner import NetworkScanner

class ScanWorker(QThread):
    finished = Signal(list)
    
    def run(self):
        scanner = NetworkScanner()
        devices = scanner.scan_network_enhanced()
        self.finished.emit(devices)

class NetworkTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Local Network")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        refresh_btn = QPushButton("Scan Network")
        refresh_btn.clicked.connect(self.start_scan)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["IP Address", "MAC Address", "Hostname", "Type"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def start_scan(self):
        self.progress.setVisible(True)
        self.table.setRowCount(0)
        
        self.worker = ScanWorker()
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.start()
        
    def on_scan_finished(self, devices):
        self.progress.setVisible(False)
        self.update_table(devices)

    def update_table(self, devices):
        self.table.setRowCount(0)
        for dev in devices:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(dev.get('ip', '')))
            self.table.setItem(row, 1, QTableWidgetItem(dev.get('mac', '')))
            self.table.setItem(row, 2, QTableWidgetItem(dev.get('hostname', '')))
            self.table.setItem(row, 3, QTableWidgetItem(dev.get('type', '')))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QLabel,
                               QHBoxLayout, QPushButton)
from PySide6.QtCore import Qt, Slot

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

from services.wifi_scanner import WifiScannerWorker

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#2b2b2b') # Dark background for figure
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#2b2b2b') # Dark background for plot area
        
        # Style ticks and labels for dark mode
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')
        self.axes.yaxis.label.set_color('white')
        self.axes.xaxis.label.set_color('white')
        self.axes.title.set_color('white')
        
        # Remove top and right spines
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['left'].set_color('white')

        super(MplCanvas, self).__init__(self.fig)

class WifiTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Worker for auto-refresh
        self.worker = WifiScannerWorker()
        self.worker.networks_found.connect(self.on_networks_found)
        self.worker.start()

    def closeEvent(self, event):
        self.worker.stop()
        super().closeEvent(event)

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Wi-Fi Networks")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        refresh_btn = QPushButton("Force Refresh")
        refresh_btn.clicked.connect(self.scan_networks)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Matplotlib Chart
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.canvas)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["SSID", "BSSID", "Signal", "Channel", "Security"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.alternatingRowColors()
        self.table.setStyleSheet("gridline-color: #555;")
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def scan_networks(self):
        # Trigger scan manually if needed, but worker loops automatically
        pass

    @Slot(list)
    def on_networks_found(self, networks):
        # Throttle updates if needed, or just proceed. 
        # Matplotlib draw can be slow.
        self.update_table(networks)
        try:
            self.update_chart(networks)
        except Exception as e:
            print(f"Chart update error: {e}")

    def update_table(self, networks):
        self.table.setSortingEnabled(False) # Disable sorting while updating
        self.table.setRowCount(0)
        for net in networks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(net.get('SSID', 'Unknown')))
            self.table.setItem(row, 1, QTableWidgetItem(net.get('BSSID', '')))
            
            signal = str(net.get('Signal', 0))
            self.table.setItem(row, 2, QTableWidgetItem(f"{signal}%"))
            
            self.table.setItem(row, 3, QTableWidgetItem(str(net.get('Channel', ''))))
            
            auth = net.get('Authentication', '')
            self.table.setItem(row, 4, QTableWidgetItem(auth))
        self.table.setSortingEnabled(True)

    def update_chart(self, networks):
        self.canvas.axes.clear()
        
        # Setup axes
        self.canvas.axes.set_xlabel('Channel (2.4 GHz)')
        self.canvas.axes.set_ylabel('Signal Strength')
        self.canvas.axes.set_ylim(0, 1.1)
        self.canvas.axes.set_xlim(1, 14)
        self.canvas.axes.set_xticks(range(1, 15))
        self.canvas.axes.grid(True, linestyle='--', alpha=0.3)
        
        # Plot Gaussian curves
        x = np.linspace(1, 14, 500)
        
        # Colors for different networks
        colors = ['#007acc', '#28a745', '#dc3545', '#ffc107', '#17a2b8', '#e83e8c']
        
        for i, net in enumerate(networks):
            try:
                channel = int(float(net.get('Channel', 0))) # Handle strings or floats
                if channel > 14 or channel < 1: 
                    continue
                    
                full_signal = int(float(net.get('Signal', 0)))
                amplitude = full_signal / 100.0
                
                sigma = 1.0 
                y = amplitude * np.exp(-0.5 * ((x - channel) / sigma)**2)
                
                color = colors[i % len(colors)]
                self.canvas.axes.plot(x, y, label=net.get('SSID', '')[:10], color=color, alpha=0.8)
                self.canvas.axes.fill_between(x, y, alpha=0.2, color=color)
                
            except Exception:
                continue
        
        # Re-apply dark theme
        self.canvas.axes.set_facecolor('#2b2b2b')
        self.canvas.axes.spines['top'].set_visible(False)
        self.canvas.axes.spines['right'].set_visible(False)
        self.canvas.axes.spines['bottom'].set_color('white')
        self.canvas.axes.spines['left'].set_color('white')
        self.canvas.axes.tick_params(axis='x', colors='white')
        self.canvas.axes.tick_params(axis='y', colors='white')
        self.canvas.axes.yaxis.label.set_color('white')
        self.canvas.axes.xaxis.label.set_color('white')
        
        # Use draw_idle to be thread-safe(r) / non-blocking
        self.canvas.draw_idle()

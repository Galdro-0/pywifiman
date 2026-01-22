from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QGridLayout, QFrame)
from PySide6.QtCore import Qt
import pyqtgraph as pg

from services.ping_test import PingWorker
from services.speed_test import SpeedTestWorker

class TestTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Ping Workers
        self.ping_google = PingWorker("8.8.8.8")
        self.ping_google.update_signal.connect(self.update_ping_graph)
        self.ping_google.start()
        
        # Speedtest Worker
        self.speed_worker = None
        
        # Data for graphs
        self.ping_data_x = []
        self.ping_data_y = []
        self.ptr = 0

    def init_ui(self):
        layout = QVBoxLayout()
        
        # --- Speed Test Section ---
        speed_frame = QFrame()
        speed_frame.setFrameShape(QFrame.StyledPanel)
        speed_layout = QVBoxLayout(speed_frame)
        
        speed_header = QLabel("Internet Speed Test")
        speed_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        speed_layout.addWidget(speed_header)
        
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Speedtest")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.clicked.connect(self.start_speedtest)
        btn_layout.addWidget(self.start_btn)
        speed_layout.addLayout(btn_layout)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        speed_layout.addWidget(self.status_label)
        
        # Results Grid
        results_grid = QGridLayout()
        
        self.dl_label = QLabel("Download: -- Mbps")
        self.ul_label = QLabel("Upload: -- Mbps")
        self.ping_label = QLabel("Ping: -- ms")
        
        results_grid.addWidget(self.dl_label, 0, 0)
        results_grid.addWidget(self.ul_label, 0, 1)
        results_grid.addWidget(self.ping_label, 0, 2)
        
        speed_layout.addLayout(results_grid)
        layout.addWidget(speed_frame)
        
        # --- Ping Monitor Section ---
        ping_frame = QFrame()
        ping_frame.setFrameShape(QFrame.StyledPanel)
        ping_layout = QVBoxLayout(ping_frame)
        
        ping_header = QLabel("Latency Monitor (8.8.8.8)")
        ping_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        ping_layout.addWidget(ping_header)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.setLabel('left', 'Latency (ms)')
        self.plot_widget.setYRange(0, 100) # Initial range
        self.ping_curve = self.plot_widget.plot(pen='g')
        
        ping_layout.addWidget(self.plot_widget)
        layout.addWidget(ping_frame)
        
        self.setLayout(layout)

    def start_speedtest(self):
        self.start_btn.setEnabled(False)
        self.status_label.setText("Starting...")
        
        self.speed_worker = SpeedTestWorker()
        self.speed_worker.progress_signal.connect(self.on_speed_progress)
        self.speed_worker.result_signal.connect(self.on_speed_result)
        self.speed_worker.error_signal.connect(self.on_speed_error)
        self.speed_worker.start()

    def on_speed_progress(self, msg):
        self.status_label.setText(msg)

    def on_speed_result(self, dl, ul, ping):
        self.dl_label.setText(f"Download: {dl:.2f} Mbps")
        self.ul_label.setText(f"Upload: {ul:.2f} Mbps")
        self.ping_label.setText(f"Ping: {ping:.0f} ms")
        self.status_label.setText("Test Complete")
        self.start_btn.setEnabled(True)

    def on_speed_error(self, err):
        self.status_label.setText(f"Error: {err}")
        self.start_btn.setEnabled(True)

    def update_ping_graph(self, target, latency, loss):
        try:
            self.ping_data_y.append(latency)
            self.ping_data_x.append(self.ptr)
            self.ptr += 1
            
            # Keep last 60 points
            if len(self.ping_data_y) > 60:
                self.ping_data_y.pop(0)
                self.ping_data_x.pop(0)
                
            self.ping_curve.setData(self.ping_data_x, self.ping_data_y)
        except Exception as e:
            print(f"Ping graph error: {e}")

    def closeEvent(self, event):
        if self.ping_google:
            self.ping_google.stop()
        super().closeEvent(event)

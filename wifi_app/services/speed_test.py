from PySide6.QtCore import QThread, Signal
import speedtest

class SpeedTestWorker(QThread):
    # Signals for progress and results
    progress_signal = Signal(str) # Status messages
    result_signal = Signal(float, float, float) # download (Mbps), upload (Mbps), ping (ms)
    error_signal = Signal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self.progress_signal.emit("Finding best server...")
            st = speedtest.Speedtest()
            st.get_best_server()
            
            self.progress_signal.emit("Testing Download...")
            download_speed = st.download() / 1_000_000 # Convert to Mbps
            
            self.progress_signal.emit("Testing Upload...")
            upload_speed = st.upload() / 1_000_000 # Convert to Mbps
            
            ping = st.results.ping
            
            self.progress_signal.emit("Done.")
            self.result_signal.emit(download_speed, upload_speed, ping)
            
        except Exception as e:
            self.error_signal.emit(str(e))

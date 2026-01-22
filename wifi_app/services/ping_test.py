from PySide6.QtCore import QThread, Signal
import subprocess
import time
import platform
import re

class PingWorker(QThread):
    # Signal emits (target, latency_ms, loss_percent)
    update_signal = Signal(str, float, float)

    def __init__(self, target="8.8.8.8"):
        super().__init__()
        self.target = target
        self.running = True

    def run(self):
        # Determine command based on OS
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', self.target]
        
        while self.running:
            try:
                # Run ping command
                # On Windows, creationflags to hide window
                creation_flags = 0x08000000 if platform.system().lower() == 'windows' else 0
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    creationflags=creation_flags
                )
                
                if result.returncode == 0:
                    # Parse time
                    # Windows: "time=14ms" or "time<1ms"
                    # Linux: "time=14.5 ms"
                    match = re.search(r'time[=<](\d+)', result.stdout)
                    latency = float(match.group(1)) if match else 0.0
                    loss = 0.0
                else:
                    latency = 0.0
                    loss = 100.0

                self.update_signal.emit(self.target, latency, loss)
                
            except Exception as e:
                print(f"Ping error: {e}")
                self.update_signal.emit(self.target, 0.0, 100.0)
            
            time.sleep(1)

    def stop(self):
        self.running = False
        self.wait()

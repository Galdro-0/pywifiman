import socket
import threading
import re
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import QThread, Signal
import logging

try:
    from scapy.all import arping, ARP, Ether, srp
except ImportError:
    print("Scapy not found. Install it via pip install scapy")

class NetworkScanWorker(QThread):
    devices_found = Signal(list)
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        devices = self.scan_scapy()
        self.devices_found.emit(devices)

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def scan_scapy(self):
        """
        Uses Scapy to scan the local network via ARP.
        """
        local_ip = self.get_local_ip()
        print(f"Local IP: {local_ip}")
        if local_ip == "127.0.0.1":
            return []
            
        # Assuming /24 subnet
        subnet = ".".join(local_ip.split(".")[:3]) + ".0/24"
        print(f"Scanning subnet: {subnet}")
        
        devices = []
        try:
            # Try Scapy first
            print("Attempting Scapy scan...")
            ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=subnet), timeout=2, verbose=0)
            print(f"Scapy answered: {len(ans)}")
            
            for sent, received in ans:
                devices.append({
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'type': 'Dynamic', # Scapy sees it live
                    'hostname': '' # Resolve later
                })
        except Exception as e:
            print(f"Scapy scan error: {e}")
            
        # Fallback to arp -a if Scapy likely failed (0 results often means interface issue or permissions)
        if not devices:
            print("Fallback to arp -a...")
            devices = self.scan_arp_fallback()

        # Resolve hostnames
        self.resolve_hostnames(devices)
        return devices

    def scan_arp_fallback(self):
        devices = []
        try:
            creation_flags = 0x08000000 if os.name == 'nt' else 0
            result = subprocess.run(
                ['arp', '-a'],
                capture_output=True,
                text=True,
                encoding='cp850',
                creationflags=creation_flags
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9-]{17})\s+(\w+)', line)
                if match:
                    devices.append({
                        'ip': match.group(1),
                        'mac': match.group(2).replace('-', ':'),
                        'type': match.group(3),
                        'hostname': ''
                    })
        except Exception as e:
            print(f"ARP fallback error: {e}")
        return devices

    def resolve_hostnames(self, devices):
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_device = {executor.submit(socket.gethostbyaddr, d['ip']): d for d in devices}
            for future in future_to_device:
                d = future_to_device[future]
                try:
                    d['hostname'] = future.result()[0]
                except:
                    d['hostname'] = "Unknown"

class NetworkScanner:
    """
    Wrapper for compatibility if needed.
    """
    def __init__(self):
        pass
    
    def scan_network_enhanced(self):
        # Sync version (not recommended for GUI but kept for compatibility)
        worker = NetworkScanWorker()
        return worker.scan_scapy()

import subprocess
import os
import re
import time
from PySide6.QtCore import QObject, QThread, Signal, QMutex

class WifiScannerWorker(QThread):
    networks_found = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            networks = self.scan()
            self.networks_found.emit(networks)
            # Sleep a bit to avoid hammering the system, but the UI timer controls the refresh usually.
            # Here we can just wait for the next call or loop.
            # To respect the user request of "Manual + Automatic", we can let the UI trigger the scan, 
            # or have a loop here. A loop is better for a Worker.
            time.sleep(5) 

    def scan(self):
        """
        Executes 'netsh wlan show networks mode=bssid' and parses the result.
        """
        try:
            creation_flags = 0x08000000 if os.name == 'nt' else 0
            
            # Using check_output and decoding with cp850 as requested
            print("Executing netsh...")
            output_bytes = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                creationflags=creation_flags
            )
            try:
                output = output_bytes.decode('cp850', errors='replace')
            except:
                output = output_bytes.decode('utf-8', errors='ignore')
            
            print(f"Netsh output length: {len(output)}")
            # print(output) # Uncomment to see full output if needed
            
            networks = self.parse_netsh_output(output)
            print(f"Parsed {len(networks)} networks")
            return networks
            
        except subprocess.CalledProcessError as e:
            print(f"Error scanning wifi (CalledProcessError): {e}")
            return []
        except Exception as e:
            print(f"Exception during wifi scan: {e}")
            return []

    def parse_netsh_output(self, output):
        """
        Robust parsing logic using regex for multi-line blocks.
        """
        networks = []
        lines = output.splitlines()
        current_ssid = None
        current_network_base = {}
        
        debug_log = []
        debug_log.append(f"Parsing {len(lines)} lines.")

        for line in lines:
            original_line = line
            line = line.strip()
            if not line:
                continue
                
            # Match SSID
            # Use search with caret ^ to ensure it starts with SSID (avoid matching 'BSSID')
            # Regex: "^SSID <digits> <ANYTHING> : <name>" to handle NBSP/decoding artifacts
            ssid_match = re.search(r'^SSID\s+\d+.*:\s*(.*)$', line, re.IGNORECASE)
            if ssid_match:
                ssid_name = ssid_match.group(1).strip()
                if not ssid_name:
                    ssid_name = "<Hidden>"
                current_ssid = ssid_name
                current_network_base = {
                    'SSID': ssid_name,
                    'Authentication': 'Unknown',
                    'Encryption': 'Unknown'
                }
                debug_log.append(f"MATCH SSID: {ssid_name}")
                continue
            
            if current_ssid:
                # Authentication (Auth/Authentification)
                if re.search(r'Auth', line, re.IGNORECASE):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        current_network_base['Authentication'] = parts[1].strip()
                # Encryption (Encryption/Chiffrage/Chiffrement)
                elif re.search(r'(Cryp|Enc|Chif)', line, re.IGNORECASE):
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        current_network_base['Encryption'] = parts[1].strip()
                
                # Match BSSID (Start of a specific AP for this SSID)
                # Regex: "BSSID" then anything then ":" then MAC
                bssid_match = re.search(r'BSSID.*:\s*([a-fA-F0-9:-]{17})', line, re.IGNORECASE)
                if bssid_match:
                    bssid = bssid_match.group(1).strip().replace('-', ':')
                    ap_data = current_network_base.copy()
                    ap_data['BSSID'] = bssid
                    ap_data['Signal'] = 0
                    ap_data['Channel'] = 0
                    networks.append(ap_data)
                    debug_log.append(f"  MATCH BSSID: {bssid}")
                    continue
                elif "BSSID" in line.upper():
                    debug_log.append(f"  FAILED BSSID MATCH: '{line}'")
                
                if networks and networks[-1]['SSID'] == current_ssid:
                    last_net = networks[-1]
                    
                    # Signal
                    if re.search(r'Si(gnal|gnaux)', line, re.IGNORECASE):
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            try:
                                last_net['Signal'] = int(re.sub(r'[^0-9]', '', parts[1]))
                            except:
                                last_net['Signal'] = 0
                                
                    # Channel (Channel/Canal)
                    elif re.search(r'C(hannel|anal)', line, re.IGNORECASE):
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            try:
                                last_net['Channel'] = int(re.sub(r'[^0-9]', '', parts[1]))
                            except:
                                last_net['Channel'] = 0
        
        # Write debug log to file
        try:
            with open("wifi_parser_debug.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(debug_log))
        except:
            pass

        return networks

    def stop(self):
        self.running = False
        self.wait()

class WifiScanner(QObject):
    """
    Service wrapper to be used by UI.
    """
    def __init__(self):
        super().__init__()
        pass
        
    def scan_sync(self):
        # Helper for immediate scan if needed, reusing 'worker' logic
        worker = WifiScannerWorker()
        return worker.scan()

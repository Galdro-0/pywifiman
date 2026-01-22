import re

def parse_key_value(text, separator=':'):
    """
    Parses text by lines containing a key-value pair separated by `separator`.
    Returns a dictionary.
    """
    data = {}
    for line in text.splitlines():
        if separator in line:
            parts = line.split(separator, 1)
            key = parts[0].strip()
            value = parts[1].strip()
            data[key] = value
    return data

def parse_netsh_networks(output):
    """
    Parses the output of 'netsh wlan show networks mode=bssid'.
    Returns a list of dictionaries, where each dictionary represents a network.
    """
    networks = []
    current_ssid = None
    current_network = {}
    
    # Identify SSID blocks. 
    # Structure is usually:
    # SSID 1 : Name
    #     Network type : Infrastructure
    #     ...
    #     BSSID 1 : xx:xx:xx...
    #         Signal : 99%
    #     BSSID 2 : ...
    
    # We will flatten this to one entry per BSSID (access point) for the "WiFiman" feel,
    # or keep them grouped. WiFiman usually shows APs.
    # Let's create a list of BSSIDs with their parent SSID info.
    
    lines = output.splitlines()
    ssid_info = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("SSID"):
            # New network block likely
            # Format: SSID X : <name>
            match = re.search(r'^SSID\s+\d+\s+:\s+(.*)$', line)
            if match:
                ssid_name = match.group(1).strip()
                if not ssid_name:
                    ssid_name = "<Hidden>"
                ssid_info = {'SSID': ssid_name}
                continue
                
        if line.startswith("Authentication"):
            parts = line.split(":", 1)
            if len(parts) > 1:
                ssid_info['Authentication'] = parts[1].strip()
        
        if line.startswith("Encryption"):
             parts = line.split(":", 1)
             if len(parts) > 1:
                ssid_info['Encryption'] = parts[1].strip()
                
        if line.startswith("BSSID"):
            # Found a specific AP
            # Format: BSSID X : xx:xx...
            match = re.match(r'^BSSID\s+(\d+)\s+:\s+(.*)$', line)
            if match:
                bssid = match.group(2).strip()
                current_network = ssid_info.copy() # Inherit SSID info
                current_network['BSSID'] = bssid
                networks.append(current_network)
                continue
        
        if line.startswith("Signal"):
            parts = line.split(":", 1)
            if len(parts) > 1 and current_network:
                current_network['Signal'] = parts[1].strip()
        
        if line.startswith("Radio type"):
            parts = line.split(":", 1)
            if len(parts) > 1 and current_network:
                current_network['Radio'] = parts[1].strip()
        
        if line.startswith("Channel"):
            parts = line.split(":", 1)
            if len(parts) > 1 and current_network:
                current_network['Channel'] = parts[1].strip()
                
    return networks

# PyWiFiman

<div align="center">

![PyWiFiman Banner](wifi_app/assets/logo.png)
<!-- You can replace this with a real screenshot later -->

**A modern, Python-based network analysis tool for Windows.**  
Inspired by Ubiquiti WiFiman, built with PySide6.

</div>## 🚀 Features

- **Wi-Fi Scanner**: Visualize surrounding networks with a real-time channel overlap graph. Detailed view of SSID, BSSID, Signal strength (dBm/% ), Channel, and Security.
- **Local Network Discovery**: Scan your LAN to discover connected devices (IP, MAC, Hostname). Uses ARP scanning (via Scapy) for accuracy.
- **Speed & Latency Monitor**: Built-in speed test (via `speedtest-cli`) and real-time latency monitoring graph (ping to Google DNS).
- **Modern UI**: sleek, dark-themed interface designed for readability and ease of use.

## 📋 Requirements

- **OS**: Windows 10 or 11
- **Python**: 3.10 or higher
- **Permissions**: Administrator rights are required for:
    - Scapy (ARP packet generation)
    - ICMP Pings (in some configurations)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Galdro-0/pywifiman.git
   cd pywifiman
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Ensure you have [Npcap](https://npcap.com/#download) installed for Scapy to work correctly on Windows.*

## ▶️ Usage

Run the main application script:

```bash
python main.py
```

## 📂 Project Structure

```
wifi_app/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── services/               # Background worker threads
│   ├── wifi_scanner.py     # Wraps 'netsh' commands
│   ├── network_scanner.py  # Scapy/ARP LAN scanning
│   ├── ping_test.py        # Latency monitoring
│   └── speed_test.py       # Internet speed testing
├── ui/                     # PySide6 Widgets
│   ├── main_window.py      # Main GUI container
│   ├── wifi_tab.py         # Wi-Fi visualization tab
│   ├── network_tab.py      # LAN devices tab
│   └── test_tab.py         # Speed & Ping tab
└── utils/                  # Helper utilities
    └── parser.py           # Text parsing logic
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


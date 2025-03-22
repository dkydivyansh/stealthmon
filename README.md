# StealthMon 🕵️‍♂️🔍

**Detect Incognito Mode & Monitor Browser Search Queries**

## Overview
StealthMon is a Python module that helps detect whether a browser is running in **Incognito/Private mode** and monitors **search queries** from the system. It is designed for **privacy monitoring, parental control, cybersecurity research, and system audits**.

## Features
✅ **Detect Incognito Mode** – Identify when browsers like **Chrome, Firefox, Edge, Brave, or Opera** are running in private mode.
✅ **Monitor Search Queries** – Track user searches made on **Google, Bing, DuckDuckGo, and more**.
✅ **Alert System** – Configurable alerts when specific queries are detected.
✅ **Multi-Threading Support** – Efficient monitoring with background threads.
✅ **Visual Notifications** – Optional UI components for alerts and notifications.
✅ **Cross-Platform** – Works on **Windows & Linux** (Mac support coming soon).
✅ **Lightweight & Easy to Use** – Simple Python module with clear API.

## Use Cases
🔹 **Parental Control** – Keep track of Incognito browsing on a child's system.
🔹 **Cybersecurity & Monitoring** – Detect stealth browsing behavior in workplaces or shared systems.
🔹 **Forensics & Investigations** – Useful for analyzing browser activity on compromised systems.

## Installation
```bash
pip install stealthmon
```

Or install from source:
```bash
git clone https://github.com/yourusername/stealthmon
cd stealthmon
pip install -e .
```

## Dependencies
StealthMon requires the following dependencies:
- Python 3.7+
- psutil
- pywin32 (Windows only)
- tkinter (for UI components)
- pygame (for sound alerts)

## Quick Start
```python
from stealthmon import StealthMonitor

# Initialize the monitor
monitor = StealthMonitor()

# Check for incognito mode
incognito_browsers = monitor.check_incognito()
for browser, is_incognito in incognito_browsers.items():
    print(f"{browser}: {'Incognito Mode' if is_incognito else 'Normal Mode'}")

# Start monitoring with a callback function
def handle_detection(event_type, browser, details):
    if event_type == "incognito":
        print(f"Incognito detected: {browser}")
    elif event_type == "query":
        print(f"Search query detected: {details['query']} on {details['engine']}")

# Start continuous monitoring
monitor.start_monitoring(callback=handle_detection)

# To stop monitoring
# monitor.stop_monitoring()
```

## Advanced Usage

### Tracking Specific Search Queries
```python
# Track specific search queries
monitor = StealthMonitor()

def query_callback(browser, query, engine):
    if "python tutorial" in query.lower():
        print(f"Educational search detected: {query}")

monitor.start_query_tracking(callback=query_callback)
```

### Customizing Detection Behavior
```python
# Custom configuration
config = {
    "browsers_to_monitor": ["chrome", "firefox", "edge"],
    "check_interval": 3,  # seconds
    "search_engines": {
        "google": r"google\.com\/search\?.*q=([^&]+)",
        "bing": r"bing\.com\/search\?.*q=([^&]+)"
    }
}

monitor = StealthMonitor(config=config)
monitor.start_monitoring()
```

### UI Components for Alerts
```python
from stealthmon import StealthMonitor, create_alert_window

monitor = StealthMonitor()

def show_alert(event_type, browser, details):
    if event_type == "query" and "sensitive" in details['query'].lower():
        create_alert_window(
            title="Search Alert",
            message=f"Sensitive search detected: {details['query']}",
            duration=10  # seconds
        )

monitor.start_monitoring(callback=show_alert)
```

## Error Handling
StealthMon includes robust error handling for various scenarios:
- Browser detection failures
- Privilege or permission issues
- Missing dependencies
- Platform compatibility issues

## Contributing
We welcome contributions! If you want to enhance the project, feel free to submit issues and pull requests.

## License
MIT License - See LICENSE file for details 
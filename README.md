# StealthMon 🕵️‍♂️🔍

**Detect Brouser Mode & Monitor Browser Search Queries**

## Overview
StealthMon is a Python module that helps detect whether a browser is running in **Normal or Incognito/Private mode** and monitors **search queries** from the system. It is designed for **privacy monitoring, parental control, cybersecurity research, and system audits**.

## Features
✅ **Detect Brouser Mode** – Identify when browsers like **Chrome, Firefox, Edge, Brave, or Opera** are running in private mode.
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
git clone https://github.com/dkydivyansh/stealthmon
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
# You can use either StealthMon or StealthMonitor (they're the same)
from stealthmon import StealthMon
# or
from stealthmon import StealthMonitor

# Initialize the monitor
monitor = StealthMon()

# Check for incognito mode for a specific browser
is_chrome_incognito = monitor.check_browser("chrome")
print(f"Chrome: {'Incognito Mode' if is_chrome_incognito else 'Normal Mode'}")

# Check all browsers
for browser in ["chrome", "firefox", "edge", "opera"]:
    try:
        is_incognito = monitor.check_browser(browser)
        print(f"{browser}: {'Incognito Mode' if is_incognito else 'Normal Mode'}")
    except Exception as e:
        print(f"{browser}: Error - {str(e)}")

# Start monitoring with a callback function
def handle_results(results, queries):
    # results = dict of browser -> incognito status
    for browser, is_incognito in results.items():
        if is_incognito:
            print(f"Incognito detected: {browser}")
    
    # queries = dict of browser -> query data
    for browser, data in queries.items():
        for query_data in data.get('queries', []):
            query = query_data.get('query', '')
            engine = query_data.get('engine', '')
            print(f"Search query detected: {query} on {engine}")

# Start continuous monitoring with 1 second interval
monitor.start(interval=1.0, callback=handle_results)

# To stop monitoring
# monitor.stop()
```

## Advanced Usage

### Tracking Specific Search Queries
```python
from stealthmon import StealthMon

# Initialize with configuration
monitor = StealthMon()

# Define a callback function that filters specific queries
def handle_results(results, queries):
    for browser, data in queries.items():
        for query_data in data.get('queries', []):
            query = query_data.get('query', '').lower()
            if "python tutorial" in query:
                print(f"Educational search detected: {query}")

# Start monitoring with the callback
monitor.start(callback=handle_results)
```

### Customizing Detection Behavior
```python
from stealthmon import StealthMon

# Custom configuration
config = {
    "browsers_to_monitor": ["chrome", "firefox", "edge"],
    "check_interval": 3,  # seconds
    "search_engines": {
        "google": {
            "domain_patterns": ["google.com"],
            "title_pattern": r"(.+) - Google Search"
        },
        "bing": {
            "domain_patterns": ["bing.com"],
            "title_pattern": r"(.+) - Bing"
        }
    }
}

# Initialize with custom config
monitor = StealthMon(config=config)

# Start monitoring
monitor.start()
```

### Command Line Interface
StealthMon also includes a command-line interface:

```bash
# Check all browsers once
stealthmon --once

# Monitor specific browser continuously
stealthmon --browser chrome

# Set custom interval
stealthmon --interval 2.5

# Quiet mode (no continuous display)
stealthmon --quiet
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

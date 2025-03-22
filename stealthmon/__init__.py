"""
StealthMon - A Python module for detecting Incognito mode and tracking browser queries on Windows.
"""

import platform
import psutil
import logging
import time
import re
import os
import sys
from typing import Dict, List, Optional, Callable, Union, Set, Any
from threading import Thread, Event, Lock
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Define supported browsers and their process names
SUPPORTED_BROWSERS = {
    'chrome': ['chrome.exe', 'Google Chrome'],
    'edge': ['msedge.exe', 'Microsoft Edge'],
    'firefox': ['firefox.exe', 'Firefox'],
    'opera': ['opera.exe', 'Opera']
}

# Define incognito indicators for each browser
INCOGNITO_INDICATORS = {
    'chrome': ['Incognito', 'Private'],
    'edge': ['InPrivate', 'Private'],
    'firefox': ['Private Browsing'],
    'opera': ['Private', 'Incognito']
}

# Define search engines and their query patterns
SEARCH_ENGINES = {
    'google': {
        'domain_patterns': ['google.com', 'google.co'],
        'query_param': 'q',
        'title_pattern': r'(.+) - Google Search'
    },
    'bing': {
        'domain_patterns': ['bing.com'],
        'query_param': 'q',
        'title_pattern': r'(.+) - Bing'
    },
    'duckduckgo': {
        'domain_patterns': ['duckduckgo.com'],
        'query_param': 'q',
        'title_pattern': r'(.+) at DuckDuckGo'
    }
}

# Global logger
logger = logging.getLogger(__name__)

# Import platform-specific modules
try:
    if platform.system() == 'Windows':
        import win32gui
        import win32process
        PLATFORM_SUPPORTED = True
    else:
        logger.warning(f"Platform {platform.system()} has limited support. Some features may not work.")
        PLATFORM_SUPPORTED = False
except ImportError as e:
    logger.error(f"Failed to import required modules: {str(e)}")
    logger.error("Please install required dependencies: pip install pywin32 (Windows only)")
    PLATFORM_SUPPORTED = False

class StealthMonException(Exception):
    """Base exception class for StealthMon module."""
    pass

class PlatformNotSupportedError(StealthMonException):
    """Exception raised when the platform is not supported."""
    pass

class BrowserNotSupportedError(StealthMonException):
    """Exception raised when the browser is not supported."""
    pass

class StealthMon:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the StealthMon monitor.
        
        Args:
            config (Dict[str, Any], optional): Configuration options for the monitor
                - browsers_to_monitor: List of browsers to monitor
                - check_interval: Time between checks
                - search_engines: Custom search engine configurations
        """
        self.stop_event = Event()
        self.results_lock = Lock()
        self.results = {}
        self.queries_lock = Lock()
        self.queries = {}
        self.uri_history = set()
        self.logger = logger
        
        # Apply configuration if provided
        self.config = config or {}
        self.check_interval = self.config.get('check_interval', 0.1)
        
        # Set up thread pool with sensible defaults
        max_workers = min(len(SUPPORTED_BROWSERS), os.cpu_count() or 4)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Check platform compatibility
        if not PLATFORM_SUPPORTED and platform.system() == 'Windows':
            self.logger.warning("Required Windows modules not available. Install pywin32 for full functionality.")

    def check_browser(self, browser: str) -> bool:
        """
        Check a single browser for incognito mode.
        
        Args:
            browser (str): Browser name to check
            
        Returns:
            bool: True if browser is in incognito mode, False otherwise
            
        Raises:
            BrowserNotSupportedError: If the browser is not supported
        """
        if browser not in SUPPORTED_BROWSERS:
            raise BrowserNotSupportedError(f"Browser '{browser}' not supported. Supported browsers: {', '.join(SUPPORTED_BROWSERS.keys())}")
            
        try:
            if platform.system() == 'Windows':
                return self._check_windows_incognito(browser)
            else:
                self.logger.warning(f"Incognito detection not implemented for {platform.system()}")
                return False
        except Exception as e:
            self.logger.error(f"Error checking incognito mode for {browser}: {str(e)}")
            # Return False instead of raising to avoid breaking the monitoring loop
            return False

    def update_results(self, browser: str, is_incognito: bool):
        """
        Thread-safe update of results.
        
        Args:
            browser (str): Browser name
            is_incognito (bool): Whether browser is in incognito mode
        """
        with self.results_lock:
            self.results[browser] = is_incognito

    def track_queries(self, browser: str):
        """
        Track search queries and URIs for a browser.
        
        Args:
            browser (str): Browser name to track
        """
        try:
            # Initialize browser data structure if needed
            with self.queries_lock:
                if browser not in self.queries:
                    self.queries[browser] = {'queries': [], 'uris': set()}
            
            # Platform-specific tracking
            if platform.system() == 'Windows':
                window_info = self._get_browser_windows(browser)
                
                for window in window_info:
                    # Process the window data
                    with self.queries_lock:
                        # Track window title as URI
                        title = window.get('title', '')
                        if title and title not in self.uri_history:
                            self.uri_history.add(title)
                            self.queries[browser]['uris'].add(title)
                        
                        # Check for search queries based on window title
                        for engine, config in SEARCH_ENGINES.items():
                            if 'title_pattern' in config:
                                try:
                                    pattern = config['title_pattern']
                                    match = re.search(pattern, title)
                                    if match:
                                        query = match.group(1)
                                        self.queries[browser]['queries'].append({
                                            'engine': engine,
                                            'query': query,
                                            'timestamp': time.time()
                                        })
                                        self.logger.info(f"Detected query: {query} in {browser} using {engine}")
                                except re.error as e:
                                    self.logger.error(f"Invalid regex pattern for {engine}: {str(e)}")
            else:
                self.logger.debug(f"Query tracking not implemented for {platform.system()}")
        except Exception as e:
            self.logger.error(f"Error tracking queries for {browser}: {str(e)}")

    def monitor_loop(self, browsers: List[str], callback: Optional[Callable] = None):
        """
        Main monitoring loop using multiple threads.
        
        Args:
            browsers (List[str]): List of browsers to monitor
            callback (Optional[Callable]): Function to call with results
        """
        self.logger.info(f"Starting monitoring loop for browsers: {', '.join(browsers)}")
        try:
            while not self.stop_event.is_set():
                # Submit all browser checks to thread pool
                futures = {
                    self.executor.submit(self.check_browser, browser): browser 
                    for browser in browsers
                }
                
                # Process results as they complete
                for future in futures:
                    browser = futures[future]
                    try:
                        is_incognito = future.result()
                        self.update_results(browser, is_incognito)
                        
                        # Track queries and URIs
                        self.track_queries(browser)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing {browser}: {str(e)}")
                        self.update_results(browser, False)
                
                # Execute callback with a copy of current results
                if callback:
                    try:
                        with self.results_lock, self.queries_lock:
                            callback(self.results.copy(), self.queries.copy())
                    except Exception as e:
                        self.logger.error(f"Error in callback: {str(e)}")
                
                # Sleep for specified interval
                time.sleep(self.check_interval)
        except Exception as e:
            self.logger.error(f"Error in monitor loop: {str(e)}")
        finally:
            self.logger.info("Monitoring loop ended")

    def start(self, browser: Optional[str] = None, interval: float = 1.0, callback: Optional[Callable] = None) -> Dict[str, bool]:
        """
        Start monitoring browsers.
        
        Args:
            browser (Optional[str]): Specific browser to monitor or None for all
            interval (float): Time between checks
            callback (Optional[Callable]): Function to call with results
            
        Returns:
            Dict[str, bool]: Initial browser incognito status
            
        Raises:
            PlatformNotSupportedError: If platform is not supported
            BrowserNotSupportedError: If specified browser is not supported
        """
        # Check platform compatibility
        if not PLATFORM_SUPPORTED and platform.system() == 'Windows':
            raise PlatformNotSupportedError(
                "Required Windows modules not available. " 
                "Install pywin32 using: pip install pywin32"
            )
        
        # Validate browser input
        if browser and browser.lower() not in SUPPORTED_BROWSERS:
            raise BrowserNotSupportedError(
                f"Unsupported browser: {browser}. "
                f"Supported browsers: {', '.join(SUPPORTED_BROWSERS.keys())}"
            )
        
        # Set check interval
        self.check_interval = interval
        
        # Determine which browsers to monitor
        browsers_to_check = [browser.lower()] if browser else list(SUPPORTED_BROWSERS.keys())
        
        # Start monitoring thread
        self.logger.info(f"Starting StealthMon with interval {interval}s")
        try:
            monitor_thread = Thread(
                target=self.monitor_loop,
                args=(browsers_to_check, callback),
                daemon=True
            )
            monitor_thread.start()
        except Exception as e:
            self.logger.error(f"Failed to start monitoring thread: {str(e)}")
            raise
        
        return self.results

    def stop(self):
        """Stop monitoring and clean up resources."""
        self.logger.info("Stopping StealthMon")
        self.stop_event.set()
        self.executor.shutdown(wait=False)

    def _check_windows_incognito(self, browser: str) -> bool:
        """
        Check if a specific browser is running in incognito mode on Windows.
        
        Args:
            browser (str): Browser name to check
            
        Returns:
            bool: True if browser is in incognito mode, False otherwise
        """
        if platform.system() != 'Windows':
            return False
            
        def callback(hwnd, results):
            if not win32gui.IsWindowVisible(hwnd):
                return
                
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    if process.name().lower() in [p.lower() for p in SUPPORTED_BROWSERS.get(browser, [])]:
                        title = win32gui.GetWindowText(hwnd)
                        if any(indicator in title for indicator in INCOGNITO_INDICATORS.get(browser, [])):
                            results.append(True)
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.debug(f"Process access error (PID {pid}): {str(e)}")
            except Exception as e:
                self.logger.debug(f"Window enumeration error: {str(e)}")
        
        results = []
        try:
            win32gui.EnumWindows(callback, results)
        except Exception as e:
            self.logger.error(f"Failed to enumerate windows: {str(e)}")
            
        return any(results)

    def _get_browser_windows(self, browser: str) -> List[Dict]:
        """
        Get information about browser windows including title and process.
        
        Args:
            browser (str): Browser name
            
        Returns:
            List[Dict]: List of window information dictionaries
        """
        if platform.system() != 'Windows':
            return []
            
        windows = []
        
        def callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return
                
            try:
                title = win32gui.GetWindowText(hwnd)
                if not title:
                    return
                    
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    if process.name().lower() in [p.lower() for p in SUPPORTED_BROWSERS.get(browser, [])]:
                        windows.append({
                            'hwnd': hwnd,
                            'pid': pid,
                            'title': title,
                            'process_name': process.name()
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.debug(f"Process access error (PID {pid}): {str(e)}")
            except Exception as e:
                self.logger.debug(f"Window info error: {str(e)}")
        
        try:
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            self.logger.error(f"Failed to enumerate windows: {str(e)}")
            
        return windows
        
# Simplified API

def stealthmon(browser: Optional[str] = None, interval: float = 1.0, callback: Optional[Callable] = None) -> Dict[str, bool]:
    """
    Check if browsers are running in incognito/private mode and track queries on Windows.
    
    Args:
        browser (str, optional): Specific browser to check ('chrome', 'edge', 'firefox', 'opera')
        interval (float): Time between checks in seconds (default: 1.0)
        callback (Callable): Optional callback function to handle results
    
    Returns:
        Dict[str, bool]: Dictionary mapping browser names to their incognito status
        
    Raises:
        PlatformNotSupportedError: If platform is not supported
        BrowserNotSupportedError: If specified browser is not supported
    """
    try:
        monitor = StealthMon()
        stealthmon.monitor = monitor  # Save reference for stop_monitoring
        return monitor.start(browser, interval, callback)
    except Exception as e:
        logger.error(f"Failed to start StealthMon: {str(e)}")
        raise

def stop_monitoring():
    """Stop the continuous monitoring."""
    if hasattr(stealthmon, 'monitor'):
        try:
            stealthmon.monitor.stop()
        except Exception as e:
            logger.error(f"Error stopping monitoring: {str(e)}") 
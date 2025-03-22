#!/usr/bin/env python3
"""
StealthMon CLI - Command line interface for the StealthMon module
"""

import argparse
import sys
import time
import platform
from typing import Dict, Any
from . import StealthMon

def format_result(browser: str, is_incognito: bool) -> str:
    """Format the result for display"""
    status = "INCOGNITO" if is_incognito else "Normal"
    return f"{browser.capitalize()}: {status}"

def display_callback(results: Dict[str, bool], queries: Dict[str, Any]) -> None:
    """Display callback for monitoring"""
    # Clear screen based on platform
    if platform.system() == "Windows":
        import os
        os.system('cls')
    else:
        print("\033c", end="")
    
    # Print header
    print("\n=== StealthMon Monitoring ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 30)
    
    # Print browser statuses
    print("\nBrowser Status:")
    for browser, is_incognito in results.items():
        print(f"  {format_result(browser, is_incognito)}")
    
    # Print recent queries
    print("\nRecent Search Queries:")
    found_queries = False
    for browser, data in queries.items():
        browser_queries = data.get('queries', [])
        if browser_queries:
            found_queries = True
            print(f"  {browser.capitalize()}:")
            # Show last 5 queries, most recent first
            for query_data in sorted(browser_queries, key=lambda x: x.get('timestamp', 0), reverse=True)[:5]:
                query = query_data.get('query', '')
                engine = query_data.get('engine', '')
                timestamp = time.strftime('%H:%M:%S', time.localtime(query_data.get('timestamp', 0)))
                print(f"    [{timestamp}] {query} (via {engine})")
    
    if not found_queries:
        print("  No queries detected yet")
    
    print("\nPress Ctrl+C to stop monitoring")
    
def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="StealthMon - Detect Incognito Mode & Monitor Browser Search Queries")
    parser.add_argument('-b', '--browser', choices=['chrome', 'firefox', 'edge', 'opera'], 
                        help='Specific browser to monitor (default: all)')
    parser.add_argument('-i', '--interval', type=float, default=1.0,
                        help='Monitoring interval in seconds (default: 1.0)')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Run in quiet mode (no continuous output)')
    parser.add_argument('-o', '--once', action='store_true',
                        help='Check once and exit (don\'t monitor continuously)')
    
    args = parser.parse_args()
    
    monitor = StealthMon()
    
    try:
        if args.once:
            # Just check once and print results
            print("Checking browser status...")
            if args.browser:
                result = monitor.check_browser(args.browser)
                print(format_result(args.browser, result))
            else:
                # Check all browsers
                for browser in monitor.config.get('browsers_to_monitor', ['chrome', 'firefox', 'edge', 'opera']):
                    try:
                        result = monitor.check_browser(browser)
                        print(format_result(browser, result))
                    except Exception as e:
                        print(f"{browser.capitalize()}: Error - {str(e)}")
        else:
            # Continuous monitoring
            print(f"Starting continuous monitoring{' for ' + args.browser if args.browser else ''}...")
            print("Press Ctrl+C to stop")
            
            # Set up callback based on quiet mode
            callback = None if args.quiet else display_callback
            
            # Start monitoring
            monitor.start(args.browser, args.interval, callback)
            
            # If in quiet mode, we need to keep the main thread alive
            if args.quiet:
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            else:
                # In display mode, the callback handles the display
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
                
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up
        monitor.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
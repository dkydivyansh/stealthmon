import time
import os
import subprocess
import threading
import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime, timedelta
import sys
import stealthmon as stealthmon_module
from stealthmon import StealthMon
from stealthmon import StealthMonitor

# Check if required libraries are installed, if not install them
try:
    import pygame
    from PIL import Image, ImageTk, ImageSequence
except ImportError:
    print("Installing required packages...")
    subprocess.call(['pip', 'install', 'pygame', 'pillow'])
    import pygame
    from PIL import Image, ImageTk, ImageSequence

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Define the specific query to detect
TARGET_QUERY = "how to learn c"

# Track active alerts and statistics
active_alerts = {}
detection_count = 0
start_time = datetime.now()
animation_window = None

# Initialize pygame for sound
pygame.mixer.init()

def show_animation_window(query):
    """Show animation window with typing effect messages"""
    global animation_window
    
    # If window already exists, just bring it to front
    if animation_window and animation_window.winfo_exists():
        animation_window.lift()
        return
    
    # Play alert sound
    try:
        # Create a simple beep sound
        pygame.mixer.Sound(pygame.sndarray.array(
            (0.1 * (2**15) * 
             pygame.K_RETURN).astype('int16'))).play()
    except Exception as e:
        # Fall back to default beep if pygame fails
        for i in range(3):
            print('\a')  # System beep
            time.sleep(0.2)
    
    # Create main window
    animation_window = tk.Tk()
    animation_window.title("Computer")  # Changed from COMPORT to Computer
    animation_window.geometry("600x300")
    animation_window.configure(bg='black')
    animation_window.attributes('-topmost', True)
    # Disable close button
    animation_window.protocol("WM_DELETE_WINDOW", lambda: None)
    
    # Try to set the icon
    try:
        icon_path = "icon.ico"  # Relative path in same directory
        # Check if file exists
        if os.path.exists(icon_path):
            animation_window.iconbitmap(icon_path)
        else:
            print(f"{Colors.YELLOW}Warning: Icon file not found at {icon_path}{Colors.END}")
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not set icon: {str(e)}{Colors.END}")
    
    # Create text font
    text_font = tkfont.Font(family="Courier", size=14)
    large_font = tkfont.Font(family="Courier", size=36, weight="bold")
    
    # Messages to display with typing effect
    messages = [
        "Now he's stuck in an infinite loop.",
        "Hey man, step away from the backend for a bit.",
        "Go outside, touch some grass, sync up with friends, and enjoy life."
    ]
    
    # Create text widget for typing animation
    text_area = tk.Text(
        animation_window,
        font=text_font,
        bg="black",
        fg="green",
        height=10,
        width=60,
        bd=0,
        highlightthickness=0
    )
    text_area.pack(pady=20, padx=20)
    
    # Create frame for the countdown and BSOD (initially hidden)
    countdown_frame = tk.Frame(animation_window, bg="black")
    countdown_label = tk.Label(
        countdown_frame,
        text="",
        font=large_font,
        bg="black",
        fg="red"
    )
    countdown_label.pack(pady=20)
    
    # Function to show BSOD
    def show_bsod():
        # Hide all frames
        text_area.pack_forget()
        countdown_frame.pack_forget()
        
        # Create BSOD frame
        bsod_frame = tk.Frame(animation_window, bg="#0000aa")
        bsod_frame.pack(fill=tk.BOTH, expand=True)
        
        # BSOD content
        bsod_text = (
            "A problem has been detected and Windows has been shut down to prevent damage\n"
            "to your computer.\n\n"
            "DRIVER_IRQL_NOT_LESS_OR_EQUAL\n\n"
            "If this is the first time you've seen this error screen,\n"
            "restart your computer. If this screen appears again, follow\n"
            "these steps:\n\n"
            "Check to make sure any new hardware or software is properly installed.\n"
            "If this is a new installation, ask your hardware or software manufacturer\n"
            "for any Windows updates you might need.\n\n"
            "Technical information:\n\n"
            "*** STOP: 0x000000D1 (0x0000000C,0x00000002,0x00000000,0xF86B5A89)\n\n"
            "Beginning dump of physical memory..."
        )
        
        bsod_label = tk.Label(
            bsod_frame,
            text=bsod_text,
            font=tkfont.Font(family="Courier", size=12),
            bg="#0000aa",
            fg="white",
            justify=tk.LEFT
        )
        bsod_label.pack(pady=40, padx=40)
        
        # Force window to maximum size
        animation_window.attributes('-fullscreen', True)
    
    # Function to show goodbye message and countdown
    def show_goodbye():
        # Hide text area
        text_area.pack_forget()
        
        # Show the countdown frame
        countdown_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add closing browser message
        closing_label = tk.Label(
            countdown_frame,
            text="now i am closing browser",
            font=text_font,
            bg="black",
            fg="yellow"
        )
        closing_label.pack(pady=10)
        
        # Function to update countdown timer
        def update_countdown(count):
            if count > 0:
                countdown_label.config(text=f"GOODBYE\n\n{count}")
                animation_window.after(1000, lambda: update_countdown(count - 1))
            else:
                show_bsod()
        
        # Wait 2 seconds with the "closing browser" message visible, then start countdown
        def start_countdown():
            closing_label.destroy()  # Remove the closing message
            update_countdown(10)     # Start the countdown
            
        animation_window.after(2000, start_countdown)
    
    # Check if browser process has ended
    def check_browser_process():
        # Get the list of running browsers from alerts
        running_browsers = set()
        for key in active_alerts:
            browser = key.split(':')[0]
            running_browsers.add(browser)
        
        # If we had browsers but now all alerts are gone, show goodbye
        if not active_alerts and running_browsers:
            show_goodbye()
            return
        
        # Schedule next check
        animation_window.after(1000, check_browser_process)
    
    # Type one character at a time
    def type_text(message, delay=0.05, wait_after=1.5, index=0):
        if index < len(message):
            text_area.insert(tk.END, message[index])
            text_area.see(tk.END)
            animation_window.after(int(delay * 1000), lambda: type_text(message, delay, wait_after, index + 1))
        else:
            # Finished typing the current message, wait and start next one
            animation_window.after(int(wait_after * 1000), next_message)
    
    # Display messages sequentially
    current_message = 0
    
    def next_message():
        nonlocal current_message
        if current_message < len(messages):
            if current_message > 0:
                # Add newline between messages
                text_area.insert(tk.END, "\n\n")
            
            # Start typing the next message
            type_text(messages[current_message])
            current_message += 1
        else:
            # Force a check immediately with a condition that guarantees goodbye sequence
            def force_goodbye():
                show_goodbye()
            
            # Wait 3 seconds after last message, then trigger goodbye
            animation_window.after(3000, force_goodbye)
    
    # Start typing the first message
    next_message()
    
    # Cursor blink function
    def blink_cursor():
        try:
            if text_area.winfo_viewable():
                # Only blink cursor if text area is visible
                cursor_pos = text_area.index(tk.END)
                text_area.see(cursor_pos)
                if text_area.get(cursor_pos + " -1c") == "|":
                    text_area.delete(cursor_pos + " -1c")
                else:
                    text_area.insert(cursor_pos, "|")
                animation_window.after(500, blink_cursor)
        except:
            # If there's an error, stop blinking
            pass
    
    # Start cursor blinking
    blink_cursor()
    
    # Start window loop
    animation_window.mainloop()

def handle_results(results, queries):
    """Callback function to handle monitoring results"""
    clear_console()
    
    # Calculate monitoring duration
    duration = datetime.now() - start_time
    duration_str = format_duration(duration)
    
    # Title and status bar
    print(f"{Colors.BOLD}╔═════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BOLD}║               STEALTHMON PRIVACY MONITOR                ║{Colors.END}")
    print(f"{Colors.BOLD}╚═════════════════════════════════════════════════════════╝{Colors.END}")
    print(f"  {Colors.BLUE}Running for: {duration_str} | Target: \"{TARGET_QUERY}\"{Colors.END}")
    print()
    
    # Process alerts
    global active_alerts, detection_count
    current_alerts = {}
    specific_query_found = False
    
    for browser, data in queries.items():
        for query_data in data.get('queries', []):
            query = query_data.get('query', '').lower()
            if TARGET_QUERY.lower() in query:
                specific_query_found = True
                timestamp = datetime.fromtimestamp(query_data['timestamp']).strftime('%H:%M:%S')
                
                # Store the alert information
                alert_key = f"{browser}:{query}"
                if alert_key not in active_alerts:
                    detection_count += 1
                                       # Show animation window in a separate thread
                    threading.Thread(target=show_animation_window, args=(query,)).start()
                
                current_alerts[alert_key] = {
                    'browser': browser,
                    'query': query,
                    'timestamp': timestamp,
                    'engine': query_data['engine']
                }
    
    # Check for closed tabs
    closed_alerts = {k: v for k, v in active_alerts.items() if k not in current_alerts}
    active_alerts = current_alerts
    
    # SECTION 1: ALERTS (most important, shown first)
    if specific_query_found:
        print(f"{Colors.RED}⚠️  TARGET QUERY DETECTED ({detection_count} total detections) ⚠️{Colors.END}")
        print(f"{Colors.RED}──────────────────────────────────────────────────────{Colors.END}")
        for key, alert in active_alerts.items():
            browser_name = alert['browser'].title()
            timestamp = alert['timestamp']
            engine = alert['engine'].title()
            query = alert['query']
            print(f"  {Colors.BOLD}► {browser_name}{Colors.END} - {engine} - {timestamp}")
            print(f"    Query: \"{query}\"")
        print()
    
    if closed_alerts:
        print(f"{Colors.GREEN}✓ TARGET QUERY TAB CLOSED{Colors.END}")
        print(f"{Colors.GREEN}──────────────────────────────────────────────────────{Colors.END}")
        for key, alert in closed_alerts.items():
            browser_name = alert['browser'].title()
            query = alert['query']
            print(f"  {Colors.BOLD}• {browser_name}{Colors.END} closed tab with query: \"{query}\"")
        print()
    
    # SECTION 2: INCOGNITO STATUS
    print(f"{Colors.BLUE}🔍 BROWSER STATUS{Colors.END}")
    print(f"{Colors.BLUE}──────────────────────────────────────────────────────{Colors.END}")
    has_incognito = False
    for browser, is_incognito in results.items():
        if is_incognito:
            has_incognito = True
            status = f"{Colors.RED}🚨 INCOGNITO MODE{Colors.END}"
        else:
            status = f"{Colors.GREEN}✓ Normal mode{Colors.END}"
        print(f"  {Colors.BOLD}{browser.title()}{Colors.END}: {status}")
    print()
    
    # SECTION 3: RECENT ACTIVITY (if space allows)
    if has_query_data(queries):
        print(f"{Colors.YELLOW}🔎 RECENT ACTIVITY{Colors.END}")
        print(f"{Colors.YELLOW}──────────────────────────────────────────────────────{Colors.END}")
        
        # Show recent searches
        for browser, data in queries.items():
            if data.get('queries'):
                print(f"  {Colors.BOLD}{browser.title()} searches:{Colors.END}")
                for query in sorted(data['queries'], key=lambda q: q['timestamp'], reverse=True)[:2]:
                    timestamp = datetime.fromtimestamp(query['timestamp']).strftime('%H:%M:%S')
                    print(f"    • [{timestamp}] {query['engine']}: \"{query['query']}\"")
    
    # Footer
    print(f"\n{Colors.BOLD}Press Ctrl+C to exit{Colors.END}")

def has_query_data(queries):
    """Check if there's any query data to display"""
    for browser, data in queries.items():
        if data.get('queries'):
            return True
    return False

def format_duration(duration):
    """Format timedelta into readable format"""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def clear_console():
    """Clear the console for better visibility"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print startup banner"""
    clear_console()
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║   ███████╗████████╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗║")
    print("║   ██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║║")
    print("║   ███████╗   ██║   █████╗  ███████║██║     ██║   ███████║║")
    print("║   ╚════██║   ██║   ██╔══╝  ██╔══██║██║     ██║   ██╔══██║║")
    print("║   ███████║   ██║   ███████╗██║  ██║███████╗██║   ██║  ██║║")
    print("║   ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝║")
    print("║                                                           ║")
    print("║                    PRIVACY MONITOR                        ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    print(f"  {Colors.YELLOW}Starting monitoring system...{Colors.END}")
    print(f"  {Colors.YELLOW}Target query: \"{TARGET_QUERY}\"{Colors.END}")
    print()
    print(f"  {Colors.GREEN}[+] Initializing browser monitors...{Colors.END}")
    time.sleep(0.5)
    print(f"  {Colors.GREEN}[+] Setting up detection systems...{Colors.END}")
    time.sleep(0.5)
    print(f"  {Colors.GREEN}[+] Starting monitoring threads...{Colors.END}")
    time.sleep(0.5)
    print(f"\n  {Colors.BOLD}Monitor is now active. Information will update every second.{Colors.END}")
    time.sleep(1.5)

# Program entry point
print_banner()

# Create a monitor instance
monitor = StealthMon()

# Start monitoring with our custom handler
try:
    # Start monitoring with the comprehensive handler defined above
    monitor.start(callback=handle_results)
    
    # Keep the main thread running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(f"\n{Colors.YELLOW}Stopping monitoring...{Colors.END}")
    monitor.stop()
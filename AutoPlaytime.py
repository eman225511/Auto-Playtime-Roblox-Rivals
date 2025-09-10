# PLS DONT SKID 😂 - Support the original creator! (Eman)

import requests
import time
import threading
import keyboard
import tkinter as tk
from io import BytesIO
from datetime import datetime
import getpass
import pyautogui
import os
import sys
import traceback
import json
from pynput.mouse import Controller, Button
from colorama import init, Fore, Style
try:
    from ahk import AHK
    # Try to find AutoHotkey in common installation paths
    import shutil
    ahk_paths = [
        shutil.which('AutoHotkey.exe'),
        r'C:\Program Files\AutoHotkey\AutoHotkey.exe',
        r'C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe',
        r'C:\Users\{}\AppData\Local\Programs\AutoHotkey\AutoHotkey.exe'.format(os.getenv('USERNAME')),
    ]
    
    ahk_exe = None
    for path in ahk_paths:
        if path and os.path.exists(path):
            ahk_exe = path
            break
    
    if ahk_exe:
        ahk = AHK(executable_path=ahk_exe)
        print(Fore.GREEN + f"✅ AutoHotkey found at: {ahk_exe}" + Style.RESET_ALL)
    else:
        ahk = AHK()  # Try default initialization
        print(Fore.GREEN + "✅ AutoHotkey initialized with default path" + Style.RESET_ALL)
        
except ImportError:
    print(Fore.RED + "❌ AutoHotkey library not installed. Install with: pip install ahk" + Style.RESET_ALL)
    ahk = None
except Exception as e:
    print(Fore.YELLOW + f"⚠️  AutoHotkey initialization failed: {e}" + Style.RESET_ALL)
    print(Fore.YELLOW + "Will use fallback mouse control instead." + Style.RESET_ALL)
    ahk = None
init(autoreset=True)


class TrackProgress:
    # ========== CONFIG FOR PROGRESS ==========
    @staticmethod
    def from_user_input():
        print(Fore.CYAN + "\n📋 Setting up Discord webhook:")
        print(Fore.WHITE + "A webhook URL looks like: https://discord.com/api/webhooks/...")
        print(Fore.YELLOW + "💡 To get one: Go to Discord → Server Settings → Integrations → Webhooks → New Webhook")
        webhook_url = input(Fore.CYAN + "Enter your Discord webhook URL: " + Style.RESET_ALL).strip()
        
        print(Fore.CYAN + "\n📸 Screenshot frequency:")
        print(Fore.WHITE + "How often should we send progress screenshots?")
        print(Fore.YELLOW + "💡 Tip: 600 seconds (10 minutes) is usually good")
        try:
            interval_seconds = int(input(Fore.CYAN + "Enter screenshot interval in seconds (default 600): " + Style.RESET_ALL).strip() or "600")
        except ValueError:
            interval_seconds = 600
            print(Fore.YELLOW + "Using default: 600 seconds (10 minutes)" + Style.RESET_ALL)
        
        # Always use 'q' as the kill key
        kill_key = 'q'
        
        print(Fore.CYAN + "\n👤 Discord mentions:")
        print(Fore.WHITE + "Your Discord User ID is used to @mention you in progress messages")
        print(Fore.YELLOW + "💡 To find it: Discord → User Settings → Advanced → Enable Developer Mode → Right-click your name → Copy ID")
        discord_user_id = input(Fore.CYAN + "Enter your Discord User ID (or leave blank to skip mentions): " + Style.RESET_ALL).strip()
        return TrackProgress(webhook_url, interval_seconds, kill_key, discord_user_id)

    def __init__(self, webhook_url, interval_seconds, kill_key, discord_user_id):
        self.webhook_url = webhook_url
        self.interval_seconds = interval_seconds
        self.kill_key = kill_key
        self.discord_user_id = discord_user_id
        self.region = None
        self.running = True

    def select_region(self):
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.attributes('-alpha', 0.3)
        root.configure(background='gray')
        root.title("Select region")

        canvas = tk.Canvas(root, cursor="cross", bg='gray')
        canvas.pack(fill=tk.BOTH, expand=True)

        rect = None
        start_x = start_y = 0

        def on_mouse_down(event):
            nonlocal start_x, start_y, rect
            start_x, start_y = event.x, event.y
            rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='black', width=2)

        def on_mouse_drag(event):
            nonlocal rect
            canvas.coords(rect, start_x, start_y, event.x, event.y)

        def on_mouse_up(event):
            x1, y1 = min(start_x, event.x), min(start_y, event.y)
            x2, y2 = max(start_x, event.x), max(start_y, event.y)
            width, height = x2 - x1, y2 - y1
            self.region = (x1, y1, width, height)
            root.destroy()

        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

        root.mainloop()

    def take_screenshot(self):
        return pyautogui.screenshot(region=self.region)

    def send_to_discord(self, image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        buffered.seek(0)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        username = getpass.getuser()
        screen_width, screen_height = pyautogui.size()

        message = (
            f"<@{self.discord_user_id}>\n"
            f"📸 Screenshot captured at `{timestamp}`\n"
            f"👤 User: `{username}`\n"
            f"🖥️ Resolution: `{screen_width}x{screen_height}`"
        )

        files = {
            'file': ('screenshot.png', buffered, 'image/png')
        }
        payload = {
            "content": message
        }

        response = requests.post(self.webhook_url, data=payload, files=files)
        if response.status_code not in (200, 204):
            print(f"❌ Failed to send to Discord: {response.status_code} - {response.text}")
        else:
            print(f"✅ Screenshot sent to Discord at {timestamp}")

    def monitor_kill_key(self):
        print(f"🛑 Press 'Q' to stop the screenshot loop.")
        keyboard.wait('q')
        self.running = False
        print("🔒 Kill key pressed. Exiting...")
        sys.exit()

    def run(self, skip_region=False):
        if not skip_region:
            print("📐 Please select the region for screenshot...")
            self.select_region()
            if self.region is None:
                print("❌ No region selected. Exiting.")
                return
            print(f"✅ Region selected: {self.region}")
        threading.Thread(target=self.monitor_kill_key, daemon=True).start()
        while self.running:
            screenshot = self.take_screenshot()
            self.send_to_discord(screenshot)
            for _ in range(self.interval_seconds):
                if not self.running:
                    break
                time.sleep(1)

# ------- Auto Playtime with Config System --------

class AutoPlaytime:
    def __init__(self):
        self.config_file = "playtime_config.json"
        self.weapon_images = {
            'primary': 'primary.png',
            'secondary': 'secondary.png', 
            'melee': 'melee.png',
            'utility': 'utility.png'
        }
        self.current_weapon = 'primary'
        self.last_gun_time = None
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(Fore.GREEN + f"✅ Configuration loaded from {self.config_file}" + Style.RESET_ALL)
                return config
            else:
                print(Fore.YELLOW + "No existing config found. Will create new one." + Style.RESET_ALL)
                return {}
        except Exception as e:
            print(Fore.RED + f"❌ Error loading config: {e}" + Style.RESET_ALL)
            return {}

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(Fore.GREEN + f"✅ Configuration saved to {self.config_file}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"❌ Error saving config: {e}" + Style.RESET_ALL)

    def setup_weapons(self):
        """Setup weapon screenshots"""
        print(Fore.CYAN + "\n🔫 WEAPON SETUP")
        print(Fore.WHITE + "You need to capture 4 weapon images for the script to work:")
        print(Fore.YELLOW + "  1. PRIMARY" + Fore.WHITE + "   - Main weapons (rifles, SMGs)")
        print(Fore.YELLOW + "  2. SECONDARY" + Fore.WHITE + " - Pistols and backup weapons")  
        print(Fore.YELLOW + "  3. MELEE" + Fore.WHITE + "     - Knives and close-combat weapons")
        print(Fore.YELLOW + "  4. UTILITY" + Fore.WHITE + "   - Grenades and special gadgets")
        print(Fore.BLUE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)

        # Check if we have existing weapon images
        existing_weapons = []
        for weapon_type, filename in self.weapon_images.items():
            if os.path.exists(os.path.join('pics', filename)):
                existing_weapons.append(weapon_type)

        if existing_weapons:
            print(Fore.GREEN + f"Found existing weapon images: {', '.join(existing_weapons)}")
            use_existing = input(Fore.CYAN + "Do you want to use existing weapon images? (y/n): " + Style.RESET_ALL).strip().lower()
            if use_existing == 'y':
                print(Fore.GREEN + "✅ Using existing weapon images" + Style.RESET_ALL)
                return

        # Capture new weapon images
        for weapon_type, filename in self.weapon_images.items():
            print(Fore.CYAN + f"\n📸 Capturing {weapon_type.upper()} weapon")
            print(Fore.WHITE + f"Instructions:")
            print(Fore.WHITE + f"  1. Make sure your {weapon_type} weapon is visible in the game")
            print(Fore.WHITE + f"  2. You'll see a gray overlay - draw a rectangle around the weapon")
            print(Fore.WHITE + f"  3. Click and drag to select the weapon area")
            print(Fore.WHITE + f"  4. Release to capture the image")
            input(Fore.CYAN + f"Press ENTER when ready to capture {weapon_type.upper()} weapon..." + Style.RESET_ALL)
            self.capture_weapon_screenshot(weapon_type, filename)

    def capture_weapon_screenshot(self, weapon_type, filename):
        """Capture screenshot for a specific weapon"""
        print(f"Select the region for {weapon_type} weapon...")
        region = self.select_region()
        if region:
            screenshot = pyautogui.screenshot(region=region)
            screenshot = screenshot.convert('L')  # Convert to grayscale
            os.makedirs('pics', exist_ok=True)
            screenshot.save(os.path.join('pics', filename))
            print(Fore.GREEN + f"✅ {weapon_type.upper()} weapon saved as pics/{filename}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"❌ No region selected for {weapon_type}" + Style.RESET_ALL)

    def select_region(self):
        """Select a region on screen"""
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.attributes('-alpha', 0.3)
        root.configure(background='gray')
        root.title("Select region")

        canvas = tk.Canvas(root, cursor="cross", bg='gray')
        canvas.pack(fill=tk.BOTH, expand=True)

        rect = None
        start_x = start_y = 0
        region = None

        def on_mouse_down(event):
            nonlocal start_x, start_y, rect
            start_x, start_y = event.x, event.y
            rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='black', width=2)

        def on_mouse_drag(event):
            nonlocal rect
            canvas.coords(rect, start_x, start_y, event.x, event.y)

        def on_mouse_up(event):
            nonlocal region
            x1, y1 = min(start_x, event.x), min(start_y, event.y)
            x2, y2 = max(start_x, event.x), max(start_y, event.y)
            width, height = x2 - x1, y2 - y1
            region = (x1, y1, width, height)
            root.destroy()

        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

        root.mainloop()
        return region

    def click(self, x=None, y=None):
        """Click using AutoHotkey if available, otherwise fallback to pynput"""
        if ahk and x is not None and y is not None:
            ahk.click(x, y)
            print(f"AHK clicked at ({x}, {y})")
        elif ahk:
            ahk.click()
            print("AHK clicked at current position")
        else:
            mouse = Controller()
            if x is not None and y is not None:
                mouse.position = (x, y)
                time.sleep(0.05)
            mouse.click(Button.left)
            print(f"Pynput clicked at ({x}, {y})" if x and y else "Pynput clicked")

    def find_and_click_weapon(self, weapon_type):
        """Find and click on a specific weapon with persistent detection"""
        filename = self.weapon_images[weapon_type]
        
        # Try multiple times to find the weapon in case screen is loading
        for attempt in range(3):
            try:
                location = pyautogui.locateCenterOnScreen(os.path.join('pics', filename), grayscale=True, confidence=0.69)
                if location:
                    self.last_gun_time = time.time()
                    # Click once only, faster timing
                    x, y = location
                    self.click(x, y)
                    time.sleep(0.05)  # Very short delay for faster execution
                    return True
            except Exception:
                pass
            
            # Brief pause between attempts
            if attempt < 2:
                time.sleep(0.05)
        
        return False

    def is_gun_screen_visible(self):
        """Check if any weapon is visible on screen (indicates gun selection screen)"""
        for weapon_type in ['primary', 'secondary', 'melee', 'utility']:
            filename = self.weapon_images[weapon_type]
            try:
                location = pyautogui.locateOnScreen(os.path.join('pics', filename), grayscale=True, confidence=0.6)
                if location:
                    return True
            except Exception:
                continue
        return False

    def switch_weapon(self, weapon_type):
        """Switch to specific weapon using number keys"""
        weapon_keys = {
            'primary': '1',
            'secondary': '2', 
            'melee': '3',
            'utility': '4'
        }
        if weapon_type in weapon_keys:
            keyboard.press_and_release(weapon_keys[weapon_type])

    def check_and_press_respawn(self):
        """Check for respawn buttons and press space"""
        try:
            found1 = pyautogui.locateOnScreen(os.path.join('pics', 'Respawn.png'), grayscale=True, confidence=0.7)
            found2 = pyautogui.locateOnScreen(os.path.join('pics', 'Respawn2.png'), grayscale=True, confidence=0.7)
            if found1 or found2:
                print("Respawn button detected! Pressing SPACE.")
                keyboard.press_and_release('space')
                time.sleep(0.5)
        except Exception as e:
            pass  # Respawn images might not exist

    def safe_sleep(self, seconds):
        """Sleep with interrupt capability"""
        interval = 0.05
        elapsed = 0
        while elapsed < seconds:
            if keyboard.is_pressed('q'):
                print("Exiting...")
                sys.exit()
            time.sleep(interval)
            elapsed += interval

    def run(self):
        """Main automation loop"""
        print(Fore.GREEN + "\n🚀 Starting automation loop...")
        print(Fore.YELLOW + "Will continuously look for gun screen and cycle through weapons")
        print(Fore.MAGENTA + "💡 Press 'Q' to stop safely at any time!" + Style.RESET_ALL)
        
        time.sleep(5)
        self.last_gun_time = None
        weapon_cycle = ['primary', 'secondary', 'melee', 'utility']
        weapons_clicked_this_round = 0

        while True:
            if keyboard.is_pressed('q'):
                print("Exiting...")
                sys.exit()

            self.check_and_press_respawn()
            
            # Check if gun screen is visible
            if self.is_gun_screen_visible():
                print(Fore.CYAN + "🔫 Gun selection screen detected!" + Style.RESET_ALL)
                weapons_clicked_this_round = 0  # Reset counter for new round
                
                # Click all 4 weapons in sequence (faster)
                for weapon_type in weapon_cycle:
                    if keyboard.is_pressed('q'):
                        print("Exiting...")
                        sys.exit()
                        
                    weapon_found = self.find_and_click_weapon(weapon_type)
                    if weapon_found:
                        self.switch_weapon(weapon_type)
                        print(Fore.GREEN + f"✓ {weapon_type.upper()}" + Style.RESET_ALL)
                        weapons_clicked_this_round += 1
                    
                    # Very short delay between weapons for speed
                    time.sleep(0.1)
                
                print(Fore.YELLOW + f"Clicked {weapons_clicked_this_round}/4 weapons this round" + Style.RESET_ALL)
            else:
                # Gun screen not visible, just do movement
                pass
            
            # Always do movement (whether gun screen is visible or not)
            print("Movement: A → D")
            
            # Hold A key for 0.15 seconds (faster)
            keyboard.press('a')
            time.sleep(0.15)
            keyboard.release('a')
            
            # Hold D key for 0.15 seconds (faster)
            keyboard.press('d')
            time.sleep(0.15)
            keyboard.release('d')
            
            # Brief pause before next check
            time.sleep(0.2)

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        print(Fore.YELLOW + "\n👋 Exiting by user request (Ctrl+C or 'q')." + Style.RESET_ALL)
    else:
        print(Fore.RED + "\n❌ Unhandled exception occurred!" + Style.RESET_ALL)
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    sys.exit(1)

sys.excepthook = global_exception_handler


def print_banner():
    print(Fore.CYAN + Style.BRIGHT + r"""
    
 █████╗ ██╗   ██╗████████╗ ██████╗     ██████╗ ██╗      █████╗ ██╗   ██╗████████╗██╗███╗   ███╗███████╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗    ██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║████╗ ████║██╔════╝
███████║██║   ██║   ██║   ██║   ██║    ██████╔╝██║     ███████║ ╚████╔╝    ██║   ██║██╔████╔██║█████╗  
██╔══██║██║   ██║   ██║   ██║   ██║    ██╔═══╝ ██║     ██╔══██║  ╚██╔╝     ██║   ██║██║╚██╔╝██║██╔══╝  
██║  ██║╚██████╔╝   ██║   ╚██████╔╝    ██║     ███████╗██║  ██║   ██║      ██║   ██║██║ ╚═╝ ██║███████╗
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝     ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝
                                                                                                       
    """)
    print(Fore.YELLOW + Style.BRIGHT + "Auto Playtime - Roblox Rivals 🚀" + Style.RESET_ALL)
    print(Fore.GREEN + Style.BRIGHT + "Developed by: Eman" + Style.RESET_ALL)
    print(Fore.BLUE + Style.BRIGHT + "Discord: https://discord.gg/W5DgDZ4Hu6\n\n" + Style.RESET_ALL)

if __name__ == "__main__":
    try:
        print_banner()
        
        # Welcome and instructions
        print(Fore.YELLOW + Style.BRIGHT + "💡 Welcome to Auto Playtime for Roblox Rivals!")
        print(Fore.CYAN + "This script helps you automatically farm playtime in Roblox Rivals game.")
        print(Fore.GREEN + "📋 Here's what this script does:")
        print(Fore.WHITE + "   • Automatically detects and selects your weapons")
        print(Fore.WHITE + "   • Performs basic movements (A and D keys)")
        print(Fore.WHITE + "   • Can send progress screenshots to Discord")
        print(Fore.WHITE + "   • Handles respawning automatically")
        print(Fore.MAGENTA + "\n⚠️  IMPORTANT: Press " + Fore.YELLOW + "'Q'" + Fore.MAGENTA + " at ANY TIME to stop the script safely.\n" + Style.RESET_ALL)
        
        # Discord webhook tracking setup
        print(Fore.BLUE + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
        print(Fore.CYAN + "📱 STEP 1: Discord Progress Tracking (Optional)")
        print(Fore.WHITE + "This feature sends screenshots of your progress to Discord.")
        print(Fore.YELLOW + "💡 Tip: This is completely optional - you can skip it if you don't want Discord notifications.")
        track = input(Fore.CYAN + "\n🔗 Do you want Discord progress tracking? (y/n): " + Style.RESET_ALL).strip().lower()
        progress = None
        if track == 'y':
            print(Fore.GREEN + "\n✅ Great! Setting up Discord tracking...")
            try:
                progress = TrackProgress.from_user_input()
                print(Fore.YELLOW + "\n📐 Now select the area of your screen to screenshot...")
                progress.select_region()
            except Exception as e:
                print(Fore.RED + f"❌ Error setting up Discord tracking: {e}")
                print(Fore.YELLOW + "Don't worry, we'll continue without Discord tracking." + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "✅ Skipping Discord tracking - that's perfectly fine!" + Style.RESET_ALL)

        # Create AutoPlaytime instance and setup
        print(Fore.BLUE + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
        print(Fore.CYAN + "🔫 STEP 2: Weapon Setup")
        auto = AutoPlaytime()
        auto.setup_weapons()

        # Start automation
        print(Fore.BLUE + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
        print(Fore.GREEN + "🚀 Starting automation...")
        print(Fore.YELLOW + "✅ The script will now:")
        print(Fore.WHITE + "   • Cycle through ALL weapons (Primary → Secondary → Melee → Utility)")
        print(Fore.WHITE + "   • Click on weapons automatically when found")
        print(Fore.WHITE + "   • Switch between weapons using number keys")
        print(Fore.WHITE + "   • Hold A key, then hold D key for movement")
        print(Fore.WHITE + "   • Handle respawning automatically")
        print(Fore.WHITE + f"   • Look for your {auto.current_weapon.upper()} weapon on screen")
        print(Fore.WHITE + "   • Click on it automatically when found")
        print(Fore.WHITE + "   • Switch to the weapon using number keys")
        print(Fore.WHITE + "   • Perform movement keys (A and D)")
        print(Fore.WHITE + "   • Handle respawning automatically")
        print(Fore.MAGENTA + "💡 Remember: Press 'Q' to stop safely at any time!" + Style.RESET_ALL)
        
        threading.Thread(target=auto.run, daemon=True).start()

        # Start Discord tracking if enabled
        if progress:
            print(Fore.CYAN + "\n📱 Starting Discord progress tracking...")
            def run_progress():
                progress.run(skip_region=True)
            threading.Thread(target=run_progress, daemon=True).start()

        # Final status message
        print(Fore.GREEN + "\n" + "="*60)
        print(Fore.GREEN + "🎉 AUTOMATION IS NOW RUNNING! 🎉")
        print(Fore.WHITE + "The script is working in the background.")
        print(Fore.YELLOW + "💡 What's happening:")
        print(Fore.WHITE + "   • Monitoring your game screen")
        print(Fore.WHITE + "   • Cycling through ALL weapons automatically")
        print(Fore.WHITE + "   • Holding A key, then holding D key for movement")
        if progress:
            print(Fore.WHITE + "   • Sending progress to Discord")
        print()
        print(Fore.MAGENTA + "🛑 IMPORTANT: Press 'Q' key to stop the automation safely")
        print(Fore.RED + "⚠️  Do NOT close this window - minimize it instead!")
        print(Fore.GREEN + "="*60 + Style.RESET_ALL)

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n👋 Script stopped by user (Ctrl+C)" + Style.RESET_ALL)
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n❌ Unexpected error occurred: {e}")
        print(Fore.YELLOW + "💡 Try restarting the script. If the problem persists, check:")
        print(Fore.WHITE + "   • Roblox Rivals is running")
        print(Fore.WHITE + "   • You're in a game (not in lobby)")
        print(Fore.WHITE + "   • Your weapon is visible on screen" + Style.RESET_ALL)
        sys.exit(1)

    # Keep the script running
    print(Fore.CYAN + "\nScript running... (Press Ctrl+C or 'Q' to exit)" + Style.RESET_ALL)
    try:
        while True:
            alive_threads = [t for t in threading.enumerate() if t is not threading.main_thread()]
            if not alive_threads:
                print(Fore.YELLOW + "\n✅ All automation threads have stopped.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n👋 Goodbye!" + Style.RESET_ALL)
        sys.exit(0)

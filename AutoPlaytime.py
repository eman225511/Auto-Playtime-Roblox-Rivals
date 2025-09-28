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
        # Initialize AHK with the found executable
        ahk = AHK(executable_path=ahk_exe)
        print(Fore.GREEN + f"✅ AutoHotkey found at: {ahk_exe}" + Style.RESET_ALL)
    else:
        # Try default initialization
        ahk = AHK()
        print(Fore.GREEN + "✅ AutoHotkey initialized with default path" + Style.RESET_ALL)
        
except ImportError:
    print(Fore.RED + "❌ AutoHotkey library not installed. Install with: pip install ahk" + Style.RESET_ALL)
    ahk = None
except Exception as e:
    print(Fore.YELLOW + f"⚠️  AutoHotkey initialization failed: {e}" + Style.RESET_ALL)
    print(Fore.YELLOW + "Will use fallback mouse control instead." + Style.RESET_ALL)
    ahk = None
# Detect AHK major version (v1 vs v2) to use correct script syntax
AHK_IS_V2 = False
try:
    exe_path = None
    # Prefer the discovered executable path, else try attribute on ahk object
    if 'ahk_exe' in globals() and 'v' in str(locals().get('ahk_exe', '')):
        exe_path = locals().get('ahk_exe')
    if not exe_path and ahk is not None:
        exe_path = getattr(ahk, 'executable_path', None)
    if exe_path and 'v2' in str(exe_path).lower():
        AHK_IS_V2 = True
except Exception:
    AHK_IS_V2 = False

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
        self.config = {
            'weapon_positions': {
                'primary': None,
                'secondary': None, 
                'melee': None,
                'utility': None
            },
            'current_weapon': 'primary',
            'discord_settings': {},
            # New: mouse move tuning (human-like glide)
            'mouse_move': {
                'steps': 60,            # number of incremental moves
                'step_sleep_ms': 8,     # sleep per step (ms)
                'final_sleep_ms': 100   # final pause before click (ms)
            },
            # Image detection settings
            'image_detection': {
                'confidence': 0.7       # confidence level for image matching (0.0-1.0)
            }
        }
        self.current_weapon = 'primary'
        self.last_gun_time = None
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge loaded config with defaults
                    self.config.update(loaded_config)
                print(Fore.GREEN + f"✅ Configuration loaded from {self.config_file}" + Style.RESET_ALL)
                return True
            else:
                print(Fore.YELLOW + "No existing config found. Will create new one." + Style.RESET_ALL)
                return False
        except Exception as e:
            print(Fore.RED + f"❌ Error loading config: {e}" + Style.RESET_ALL)
            return False

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(Fore.GREEN + f"✅ Configuration saved to {self.config_file}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"❌ Error saving config: {e}" + Style.RESET_ALL)

    @property
    def weapon_positions(self):
        """Get weapon positions from config"""
        return self.config.get('weapon_positions', {})

    @weapon_positions.setter
    def weapon_positions(self, value):
        """Set weapon positions in config"""
        self.config['weapon_positions'] = value

    def setup_weapons(self):
        """Setup weapon positions by clicking"""
        print(Fore.CYAN + "\n🔫 WEAPON POSITION SETUP")
        print(Fore.WHITE + "You need to set the click positions for 4 weapon types:")
        print(Fore.YELLOW + "  1. PRIMARY" + Fore.WHITE + "   - Main weapons (rifles, SMGs)")
        print(Fore.YELLOW + "  2. SECONDARY" + Fore.WHITE + " - Pistols and backup weapons")  
        print(Fore.YELLOW + "  3. MELEE" + Fore.WHITE + "     - Knives and close-combat weapons")
        print(Fore.YELLOW + "  4. UTILITY" + Fore.WHITE + "   - Grenades and special gadgets")
        print(Fore.BLUE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)

        # Check if we have existing positions
        has_existing = any(pos is not None for pos in self.weapon_positions.values())
        
        if has_existing:
            print(Fore.GREEN + "Found existing weapon positions:")
            for weapon_type, pos in self.weapon_positions.items():
                if pos:
                    print(f"  {weapon_type.upper()}: ({pos[0]}, {pos[1]})")
            
            use_existing = input(Fore.CYAN + "Do you want to use existing positions? (y/n): " + Style.RESET_ALL).strip().lower()
            if use_existing == 'y':
                print(Fore.GREEN + "✅ Using existing weapon positions" + Style.RESET_ALL)
                return

        # Capture new weapon positions
        weapon_order = ['primary', 'secondary', 'melee', 'utility']
        for weapon_type in weapon_order:
            self.capture_weapon_position(weapon_type)
        
        # Save positions to file
        self.save_config()

    def capture_weapon_position(self, weapon_type):
        """Capture position for a specific weapon by having user hover and press Enter"""
        print(Fore.CYAN + f"\n� Setting up {weapon_type.upper()} weapon position")
        print(Fore.WHITE + "Instructions:")
        print(Fore.WHITE + f"  1. Open your game and go to the weapon selection screen")
        print(Fore.WHITE + f"  2. Hover your mouse over the {weapon_type.upper()} weapon")
        print(Fore.WHITE + f"  3. Press ENTER to capture the position")
        print(Fore.YELLOW + f"💡 Make sure you're hovering over the {weapon_type} weapon before pressing Enter!")
        
        while True:
            try:
                keyboard.wait('enter')  # Wait for Enter key
                # Get current mouse position
                current_pos = pyautogui.position()
                
                # Store as a list with integer coordinates in the unified config
                self.config['weapon_positions'][weapon_type] = [int(current_pos.x), int(current_pos.y)]
                print(Fore.GREEN + f"✅ {weapon_type.upper()} position captured: ({current_pos.x}, {current_pos.y})" + Style.RESET_ALL)
                time.sleep(0.5)  # Brief delay to prevent double-capture
                break
                
            except KeyboardInterrupt:
                print(Fore.YELLOW + f"\nSkipping {weapon_type} setup..." + Style.RESET_ALL)
                break
            except Exception as e:
                print(Fore.RED + f"Error capturing position: {e}" + Style.RESET_ALL)
                retry = input(Fore.CYAN + "Try again? (y/n): " + Style.RESET_ALL).strip().lower()
                if retry != 'y':
                    break

    def click(self, x=None, y=None):
        """Click using AutoHotkey only"""
        # Validate coordinates if provided
        if x is not None and y is not None:
            try:
                x, y = int(x), int(y)
                # Basic bounds checking
                if x < 0 or y < 0 or x > 4000 or y > 4000:
                    print(f"Warning: Coordinates ({x}, {y}) may be out of bounds")
                    return
            except (ValueError, TypeError):
                print(f"Error: Invalid coordinates ({x}, {y})")
                return

        if not ahk:
            print("❌ AutoHotkey not available! Please install AutoHotkey.")
            return

        try:
            if x is not None and y is not None:
                # Pull human-like glide params from config with sensible bounds
                mm = self.config.get('mouse_move', {})
                steps = int(mm.get('steps', 60))
                step_sleep_ms = int(mm.get('step_sleep_ms', 8))
                final_sleep_ms = int(mm.get('final_sleep_ms', 100))
                # Clamp values to avoid extremes
                steps = max(5, min(200, steps))
                step_sleep_ms = max(1, min(50, step_sleep_ms))
                final_sleep_ms = max(0, min(1000, final_sleep_ms))

                # Build script based on AHK major version
                if AHK_IS_V2:
                    # AHK v2 syntax - stepped, human-like glide to target then click
                    ahk_script = f"""
CoordMode "Mouse", "Screen"
MouseGetPos &curX, &curY
targetX := {x}
targetY := {y}
steps := {steps}
DX := (targetX - curX) / steps
DY := (targetY - curY) / steps
Loop steps {{
    curX += DX
    curY += DY
    MouseMove curX, curY, 0
    Sleep {step_sleep_ms}
}}
; ensure exact final position
MouseMove targetX, targetY, 0
Sleep {final_sleep_ms}
Click
"""
                else:
                    # AHK v1 syntax - stepped, human-like glide to target then click
                    ahk_script = f"""
CoordMode, Mouse, Screen
MouseGetPos, curX, curY
targetX := {x}
targetY := {y}
steps := {steps}
DX := (targetX - curX) / steps
DY := (targetY - curY) / steps
Loop, %steps% {{
    curX := curX + DX
    curY := curY + DY
    MouseMove, %curX%, %curY%, 0
    Sleep, {step_sleep_ms}
}}
; ensure exact final position
MouseMove, %targetX%, %targetY%, 0
Sleep, {final_sleep_ms}
Click
"""
                ahk.run_script(ahk_script)
                print(f"AHK smoothly moved to ({x}, {y}) and clicked")
            else:
                # Click at current position
                if AHK_IS_V2:
                    ahk.run_script("Click")
                else:
                    ahk.run_script("Click")
                print("AHK clicked at current position")

        except Exception as e:
            print(f"AHK click error: {e}")
            print(f"Failed to click at ({x}, {y})" if x is not None and y is not None else "Failed to click at current position")

    def find_and_click_weapon(self, weapon_type):
        """Click on a specific weapon using saved position"""
        position = self.weapon_positions.get(weapon_type)
        
        if not position:
            print(f"{weapon_type} position not set.")
            return False

        try:
            # Extract and validate coordinates
            if not isinstance(position, (list, tuple)) or len(position) != 2:
                print(f"Invalid position format for {weapon_type}: {position}")
                return False
                
            x, y = position[0], position[1]
            
            # Ensure coordinates are valid numbers
            if x is None or y is None:
                print(f"Invalid coordinates for {weapon_type}: ({x}, {y})")
                return False
                
            # Click at the saved position
            self.click(x, y)
            self.last_gun_time = time.time()
            time.sleep(0.3)  # Increased delay to prevent miss clicks
            return True
        except Exception as e:
            print(f"Error clicking {weapon_type}: {e}")
            print(f"Position data: {position}")
            return False

    def is_gun_screen_visible(self):
        """Check if gun screen is visible by trying to click at any weapon position"""
        # For position-based clicking, we'll assume gun screen is available
        # You could enhance this by checking for a specific UI element if needed
        return any(pos is not None for pos in self.weapon_positions.values())

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

    def check_random_image(self):
        """Check if Random.png is visible on screen"""
        try:
            # Use absolute path and check if file exists first
            random_image_path = os.path.join(os.getcwd(), 'pics', 'Random.png')
            
            # Check if the file exists
            if not os.path.exists(random_image_path):
                print(f"Warning: Random.png not found at {random_image_path}")
                return False
            
            # Get confidence setting from config
            confidence = self.config.get('image_detection', {}).get('confidence', 0.7)
            confidence = max(0.1, min(1.0, float(confidence)))  # Clamp between 0.1 and 1.0
                
            random_found = pyautogui.locateOnScreen(random_image_path, grayscale=True, confidence=confidence)
            return random_found is not None
        except pyautogui.ImageNotFoundException:
            # Image file exists but not found on screen - this is normal
            return False
        except Exception as e:
            print(f"Error checking Random.png: {e}")
            return False

    def check_and_press_respawn(self):
        """Check for respawn buttons and press space"""
        try:
            # Get confidence setting from config
            confidence = self.config.get('image_detection', {}).get('confidence', 0.7)
            confidence = max(0.1, min(1.0, float(confidence)))  # Clamp between 0.1 and 1.0
            
            found1 = pyautogui.locateOnScreen(os.path.join('pics', 'Respawn.png'), grayscale=True, confidence=confidence)
            found2 = pyautogui.locateOnScreen(os.path.join('pics', 'Respawn2.png'), grayscale=True, confidence=confidence)
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
        print(Fore.YELLOW + "Will click at saved weapon positions only when Random.png is detected")
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
            
            # Check if Random.png is visible before clicking weapons
            random_detected = self.check_random_image()
            
            if random_detected:
                print(Fore.CYAN + "🎯 Random.png detected! Performing weapon clicks..." + Style.RESET_ALL)
                weapons_clicked_this_round = 0
                
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
                    
                    # Longer delay between weapons to prevent miss clicks
                    time.sleep(0.5)
                
                if weapons_clicked_this_round > 0:
                    print(Fore.YELLOW + f"Clicked {weapons_clicked_this_round}/4 weapons this cycle" + Style.RESET_ALL)
            else:
                print(Fore.BLUE + "⏳ Random.png not detected, skipping weapon clicks..." + Style.RESET_ALL)
            
            # Always do movement (whether weapons were clicked or not)
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
        print(Fore.WHITE + "   • Monitor for Random.png on screen")
        print(Fore.WHITE + "   • Click at saved weapon positions only when Random.png is detected")
        print(Fore.WHITE + "   • Switch between weapons using number keys")
        print(Fore.WHITE + "   • Hold A key, then hold D key for movement")
        print(Fore.WHITE + "   • Handle respawning automatically")
        print(Fore.GREEN + "   • Tip: Adjust mouse glide in playtime_config.json → mouse_move (steps, step_sleep_ms, final_sleep_ms)")
        print(Fore.GREEN + "   • Tip: Adjust image detection confidence in playtime_config.json → image_detection.confidence (0.1-1.0)")
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
        print(Fore.WHITE + "   • Monitoring your game screen for Random.png")
        print(Fore.WHITE + "   • Clicking at saved weapon positions only when Random.png is detected")
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

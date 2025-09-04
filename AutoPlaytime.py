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

# ------- Auto Any Gun --------

class AutoAnyGun:
    def __init__(self):
        print(Fore.CYAN + "\n🔫 [Any Weapon Automation Setup]")
        print(Fore.GREEN + "This mode works with ANY weapon in the game!" + Style.RESET_ALL)
        
        # Equipment type with better explanations
        print(Fore.CYAN + "\n🛠️  STEP 1: Choose your weapon type")
        print(Fore.WHITE + "What kind of weapon do you want to use?")
        print(Fore.YELLOW + "  • primary" + Fore.WHITE + "   - Main weapons like assault rifles, SMGs")
        print(Fore.YELLOW + "  • secondary" + Fore.WHITE + " - Pistols and backup weapons")
        print(Fore.YELLOW + "  • melee" + Fore.WHITE + "     - Knives and close-combat weapons")
        print(Fore.YELLOW + "  • utility" + Fore.WHITE + "   - Grenades and special gadgets")
        print(Fore.MAGENTA + "💡 If unsure, choose 'primary' - it works for most weapons!" + Style.RESET_ALL)
        
        self.WHAT_EQUIP = input(Fore.CYAN + "Enter weapon type (primary/secondary/melee/utility) [default: primary]: " + Style.RESET_ALL).strip().lower() or "primary"
        if self.WHAT_EQUIP not in ['primary', 'secondary', 'melee', 'utility']:
            print(Fore.YELLOW + f"'{self.WHAT_EQUIP}' isn't recognized. Using 'primary' instead." + Style.RESET_ALL)
            self.WHAT_EQUIP = 'primary'
        print(Fore.GREEN + f"✅ Selected: {self.WHAT_EQUIP.upper()} weapon" + Style.RESET_ALL)

        # Switch method with better explanations
        print(Fore.CYAN + "\n🎮 STEP 2: Weapon switching method")
        print(Fore.WHITE + "How do you want to switch weapons in-game?")
        print(Fore.YELLOW + "  Method 1:" + Fore.WHITE + " Use number keys (1, 2, 3, 4) - " + Fore.GREEN + "RECOMMENDED for beginners")
        print(Fore.YELLOW + "  Method 2:" + Fore.WHITE + " Use custom keybind - " + Fore.CYAN + "For advanced users only")
        
        self.SWITCH_METHOD = input(Fore.CYAN + "Enter 1 or 2 [default: 1]: " + Style.RESET_ALL).strip() or "1"
        if self.SWITCH_METHOD not in ['1', '2']:
            print(Fore.YELLOW + f"'{self.SWITCH_METHOD}' isn't valid. Using Method 1." + Style.RESET_ALL)
            self.SWITCH_METHOD = '1'

        self.KEYBIND = None
        if self.SWITCH_METHOD == '2':
            print(Fore.CYAN + "\n⌨️  Advanced keybind setup:")
            print(Fore.WHITE + "Enter the key you use for 'Equip Next Weapon' in your game settings")
            while True:
                self.KEYBIND = input(Fore.CYAN + "⌨️  What is the keybind you set in game for Equip Next Weapon? (for help enter H): " + Style.RESET_ALL).strip().lower()
                if self.KEYBIND == 'h':
                    print(Fore.YELLOW + "Opening help.png for keybind setup..." + Style.RESET_ALL)
                    try:
                        os.startfile(os.path.join('pics', 'help.png'))
                    except Exception as e:
                        print(Fore.RED + f"❌ Could not open help.png: {e}" + Style.RESET_ALL)
                    continue
                if self.KEYBIND:
                    print(Fore.GREEN + f"✅ Keybind set to: {self.KEYBIND.upper()}" + Style.RESET_ALL)
                    break
                else:
                    print(Fore.RED + "Please enter a valid key!" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "✅ Using number keys (1-4) for weapon switching" + Style.RESET_ALL)

        # Always ask for gun picture with detailed instructions
        print(Fore.CYAN + "\n� STEP 3: Capture your weapon image")
        print(Fore.WHITE + "The script needs to recognize your weapon on screen.")
        print(Fore.YELLOW + "📋 Instructions:")
        print(Fore.WHITE + "  1. Make sure your weapon selection menu is visible in the game")
        print(Fore.WHITE + "  2. You'll see a gray overlay - draw a rectangle around your weapon")
        print(Fore.WHITE + "  3. Click and drag to select the weapon area")
        print(Fore.WHITE + "  4. Release to capture the image")
        print(Fore.MAGENTA + "💡 Tip: Select just the weapon icon, not the whole UI!" + Style.RESET_ALL)
        input(Fore.CYAN + "Press ENTER when you're ready to take the screenshot..." + Style.RESET_ALL)
        self.capture_and_save_gun_screenshot()

        self.region = None
        self.last_gun_time = None

    def switch_method_1(self, EQUIP):
        if EQUIP == 'primary':
            keyboard.press_and_release('1')
        elif EQUIP == 'secondary':
            keyboard.press_and_release('2')
        elif EQUIP == 'melee':
            keyboard.press_and_release('3')
        elif EQUIP == 'utility':
            keyboard.press_and_release('4')

    def switch_method_2(self, EQUIP):
        if EQUIP == 'secondary':
            keyboard.press_and_release(self.KEYBIND)
        elif EQUIP == 'melee':
            keyboard.press_and_release(self.KEYBIND)
            keyboard.press_and_release(self.KEYBIND)
        elif EQUIP == 'utility':
            keyboard.press_and_release(self.KEYBIND)
            keyboard.press_and_release(self.KEYBIND)
            keyboard.press_and_release(self.KEYBIND)

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

    def click(self, x=None, y=None):
        """Click using AutoHotkey if available, otherwise fallback to pynput"""
        if ahk and x is not None and y is not None:
            # Click at specific coordinates using AHK
            ahk.click(x, y)
            print(f"AHK clicked at ({x}, {y})")
        elif ahk:
            # Click at current mouse position using AHK
            ahk.click()
            print("AHK clicked at current position")
        else:
            # Fallback to pynput
            mouse = Controller()
            if x is not None and y is not None:
                mouse.position = (x, y)
                time.sleep(0.05)  # Small delay for positioning
            mouse.click(Button.left)
            print(f"Pynput clicked at ({x}, {y})" if x and y else "Pynput clicked")

    def find_gun_and_press_keys(self):
        try:
            location = pyautogui.locateCenterOnScreen(os.path.join('pics', 'userGun.png'), grayscale=True, confidence=0.69)
        except Exception:
            print("userGun.png not found on screen (exception).")
            return False

        if location:
            print("userGun.png found!")
            self.last_gun_time = time.time()
            for i in range(4):
                # Click directly on the gun instead of using key sequence
                x, y = location
                self.click(x, y)
                time.sleep(0.2)  # Small delay after clicking
            return True
        else:
            print("userGun.png not found on screen.")
            return False

    def capture_and_save_gun_screenshot(self):
        print("Select the region to capture for userGun.png...")
        self.select_region()
        if self.region:
            screenshot = self.take_screenshot()
            screenshot = screenshot.convert('L')
            screenshot.save(os.path.join('pics', 'userGun.png'))
            print("Screenshot saved as pics/userGun.png (black and white).")
        else:
            print("No region selected.")

    def is_health_found(self):
        try:
            location = pyautogui.locateOnScreen(os.path.join('pics', 'health.png'), grayscale=True, confidence=0.7)
            return location is not None
        except Exception:
            return False

    def safe_sleep(self, seconds):
        interval = 0.05
        elapsed = 0
        while elapsed < seconds:
            if keyboard.is_pressed('q'):
                print("Exiting...")
                sys.exit()
            time.sleep(interval)
            elapsed += interval

    def check_and_press_respawn(self):
        try:
            found1 = pyautogui.locateOnScreen(os.path.join('pics', 'Respawn.png'), grayscale=True, confidence=0.8)
            found2 = pyautogui.locateOnScreen(os.path.join('pics', 'Respawn2.png'), grayscale=True, confidence=0.8)
            if found1 or found2:
                print("Respawn button detected! Pressing SPACE.")
                keyboard.press_and_release('space')
                time.sleep(0.5)
        except Exception as e:
            print(f"Respawn not found: {e}")

    def run(self):
        time.sleep(5)
        self.last_gun_time = None

        if self.SWITCH_METHOD == '1':
            while True:
                if keyboard.is_pressed('q'):
                    print("Exiting...")
                    sys.exit()

                self.check_and_press_respawn()

                self.find_gun_and_press_keys()
                self.safe_sleep(2)
                self.switch_method_1(self.WHAT_EQUIP)

                # Hold A for 0.2 seconds, then D for 0.2 seconds
                print("Holding A key...")
                keyboard.press('a')
                time.sleep(0.2)
                keyboard.release('a')
                
                print("Holding D key...")
                keyboard.press('d')
                time.sleep(0.2)
                keyboard.release('d')

        elif self.SWITCH_METHOD == '2':
            health_was_found = False
            while True:
                if keyboard.is_pressed('q'):
                    print("Exiting...")
                    sys.exit()

                self.find_gun_and_press_keys()
                self.safe_sleep(2)

                health_found = self.is_health_found()
                if health_found and not health_was_found:
                    self.switch_method_2(self.WHAT_EQUIP)
                    print("switch_method_2 executed because health.png was found.")
                health_was_found = health_found

                # Hold A for 0.2 seconds, then D for 0.2 seconds
                print("Holding A key...")
                keyboard.press('a')
                time.sleep(0.2)
                keyboard.release('a')
                
                print("Holding D key...")
                keyboard.press('d')
                time.sleep(0.2)
                keyboard.release('d')

# --------- Auto G Nade -------

class AutoGNade:
    def __init__(self):
        print(Fore.CYAN + "\n💥 [Grenade Launcher Automation Setup]")
        print(Fore.GREEN + "This mode is specifically designed for grenade launchers!" + Style.RESET_ALL)
        print(Fore.WHITE + "Perfect for glass wrap farming and explosive weapons.")
        
        # Always ask for grenade launcher picture with detailed instructions
        print(Fore.CYAN + "\n� STEP 1: Capture your grenade launcher image")
        print(Fore.WHITE + "The script needs to recognize your grenade launcher on screen.")
        print(Fore.YELLOW + "📋 Instructions:")
        print(Fore.WHITE + "  1. Make sure your weapon selection menu is visible in the game")
        print(Fore.WHITE + "  2. You'll see a gray overlay - draw a rectangle around the launcher")
        print(Fore.WHITE + "  3. Click and drag to select the weapon area")
        print(Fore.WHITE + "  4. Release to capture the image")
        print(Fore.MAGENTA + "💡 Tip: Select just the grenade launcher icon for best results!" + Style.RESET_ALL)
        input(Fore.CYAN + "Press ENTER when you're ready to take the screenshot..." + Style.RESET_ALL)
        self.capture_and_save_gnade_screenshot()
        
        print(Fore.GREEN + "✅ Grenade launcher setup complete!" + Style.RESET_ALL)
        self.last_gun_time = None

    def click(self, x=None, y=None):
        """Click using AutoHotkey if available, otherwise fallback to pynput"""
        if ahk and x is not None and y is not None:
            # Click at specific coordinates using AHK
            ahk.click(x, y)
            print(f"AHK clicked at ({x}, {y})")
        elif ahk:
            # Click at current mouse position using AHK
            ahk.click()
            print("AHK clicked at current position")
        else:
            # Fallback to pynput
            mouse = Controller()
            if x is not None and y is not None:
                mouse.position = (x, y)
                time.sleep(0.05)  # Small delay for positioning
            mouse.click(Button.left)
            print(f"Pynput clicked at ({x}, {y})" if x and y else "Pynput clicked")
        
    def check_and_press_respawn(self):
        try:
            found1 = pyautogui.locateOnScreen(os.path.join('pics', 'Respawn.png'), grayscale=True, confidence=0.8)
            found2 = pyautogui.locateOnScreen(os.path.join('pics', 'Respawn2.png'), grayscale=True, confidence=0.8)
            if found1 or found2:
                print("Respawn button detected! Pressing SPACE.")
                keyboard.press_and_release('space')
                time.sleep(0.5)
        except Exception as e:
            print(f"Respawn not found: {e}")

    def find_gun_and_press_keys(self):
        try:
            # Use correct path for GNade.png in the pics folder
            location = pyautogui.locateCenterOnScreen(os.path.join('pics', 'GNade.png'), grayscale=True, confidence=0.69)
        except pyautogui.ImageNotFoundException:
            print("GNade.png not found on screen (exception).")
            return

        if location:
            print("GNade.png found!")
            self.last_gun_time = time.time()
            for i in range(4):
                # Click directly on the gun instead of using key sequence
                x, y = location
                self.click(x, y)
                time.sleep(0.2)  # Small delay after clicking
        else:
            print("GNade.png not found on screen.")

    def capture_and_save_gnade_screenshot(self):
        # Region selection for custom GNade.png
        print("Select the region to capture for GNade.png...")
        region = [None]
        def select_region():
            import tkinter as tk
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
                region[0] = (x1, y1, width, height)
                root.destroy()
            canvas.bind("<ButtonPress-1>", on_mouse_down)
            canvas.bind("<B1-Motion>", on_mouse_drag)
            canvas.bind("<ButtonRelease-1>", on_mouse_up)
            root.mainloop()
            return region[0]
        try:
            selected_region = select_region()
            if selected_region:
                import pyautogui
                screenshot = pyautogui.screenshot(region=selected_region)
                screenshot = screenshot.convert('L')
                os.makedirs('pics', exist_ok=True)
                screenshot.save(os.path.join('pics', 'GNade.png'))
                print(Fore.GREEN + "✅ Screenshot saved as pics/GNade.png (black and white)." + Style.RESET_ALL)
            else:
                print(Fore.RED + "❌ No region selected." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"❌ Error capturing GNade.png: {e}" + Style.RESET_ALL)

    def safe_sleep(self, seconds):
        interval = 0.05
        elapsed = 0
        while elapsed < seconds:
            if keyboard.is_pressed('q'):
                print("Exiting...")
                sys.exit()
            time.sleep(interval)
            elapsed += interval

    def run(self):
        time.sleep(5)
        self.last_gun_time = None
        while True:
            if keyboard.is_pressed('q'):
                print("Exiting...")
                sys.exit()
                
            self.check_and_press_respawn()
            
            self.find_gun_and_press_keys()
            self.safe_sleep(2)

            # Hold A for 0.2 seconds, then D for 0.2 seconds
            print("Holding A key...")
            keyboard.press('a')
            time.sleep(0.2)
            keyboard.release('a')
            
            print("Holding D key...")
            keyboard.press('d')
            time.sleep(0.2)
            keyboard.release('d')

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
        print(Fore.WHITE + "   • Automatically detects and selects your weapon")
        print(Fore.WHITE + "   • Performs basic movements (A and D keys)")
        print(Fore.WHITE + "   • Can send progress screenshots to Discord")
        print(Fore.WHITE + "   • Handles respawning automatically")
        print(Fore.MAGENTA + "\n⚠️  IMPORTANT: Press " + Fore.YELLOW + "'Q'" + Fore.MAGENTA + " at ANY TIME to stop the script safely.\n" + Style.RESET_ALL)
        
        # Simple setup guide
        print(Fore.BLUE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
        print(Fore.CYAN + "📖 QUICK SETUP GUIDE:")
        print(Fore.WHITE + "1. Make sure Roblox Rivals is open and you're in a game")
        print(Fore.WHITE + "2. Choose if you want Discord notifications (optional)")
        print(Fore.WHITE + "3. Pick your automation type (we'll guide you)")
        print(Fore.WHITE + "4. Take a screenshot of your weapon (we'll show you how)")
        print(Fore.WHITE + "5. The script will do the rest automatically!")
        print(Fore.BLUE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)

        # Discord webhook tracking setup
        print(Fore.BLUE + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
        print(Fore.CYAN + "📱 STEP 1: Discord Progress Tracking (Optional)")
        print(Fore.WHITE + "This feature sends screenshots of your progress to Discord.")
        print(Fore.YELLOW + "� Tip: This is completely optional - you can skip it if you don't want Discord notifications.")
        track = input(Fore.CYAN + "\n🔗 Do you want Discord progress tracking? (y/n): " + Style.RESET_ALL).strip().lower()
        progress = None
        if track == 'y':
            print(Fore.GREEN + "\n✅ Great! Setting up Discord tracking...")
            print(Fore.YELLOW + "📝 You'll need:")
            print(Fore.WHITE + "   • A Discord webhook URL (we'll help you get one)")
            print(Fore.WHITE + "   • How often to send screenshots (in seconds)")
            print(Fore.WHITE + "   • Your Discord user ID (for @mentions)")
            try:
                progress = TrackProgress.from_user_input()
                print(Fore.YELLOW + "\n📐 Now select the area of your screen to screenshot...")
                print(Fore.WHITE + "   • Draw a rectangle around the game area you want to track")
                print(Fore.WHITE + "   • This will be used for progress screenshots")
                progress.select_region()  # Wait for user to select region before starting thread
            except Exception as e:
                print(Fore.RED + f"❌ Error setting up Discord tracking: {e}")
                print(Fore.YELLOW + "Don't worry, we'll continue without Discord tracking." + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "✅ Skipping Discord tracking - that's perfectly fine!" + Style.RESET_ALL)

        # Automation type selection menu
        print(Fore.BLUE + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
        print(Fore.CYAN + "🤖 STEP 2: Choose Your Automation Type")
        print(Fore.WHITE + "Which type of weapon automation do you want?")
        print()
        print(Fore.YELLOW + "Option 1: Grenade Launcher" + Fore.WHITE + " (Glass Wrap Farming)")
        print(Fore.WHITE + "   • " + Fore.GREEN + "Perfect for:" + Fore.WHITE + " Glass wrap farming with grenade launchers")
        print(Fore.WHITE + "   • " + Fore.GREEN + "Setup:" + Fore.WHITE + " Simple - just capture your grenade launcher")
        print()
        print(Fore.YELLOW + "Option 2: Any Weapon" + Fore.WHITE + " (Universal)")
        print(Fore.WHITE + "   • " + Fore.GREEN + "Perfect for:" + Fore.WHITE + " Any weapon type (rifles, pistols, knives, etc.)")
        print(Fore.WHITE + "   • " + Fore.GREEN + "Setup:" + Fore.WHITE + " Choose weapon type and switching method")
        print()
        print(Fore.MAGENTA + "💡 New to this? Choose Option 2 - it works with everything!" + Style.RESET_ALL)
        print(Fore.BLUE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
        choice = input(Fore.CYAN + "Enter your choice (1 or 2): " + Style.RESET_ALL).strip()

        if choice == '1':
            print(Fore.CYAN + f"\n🎯 You chose: Grenade Launcher Automation")
            try:
                auto = AutoGNade()
                print(Fore.GREEN + "\n🚀 Starting Grenade Launcher automation...")
                print(Fore.YELLOW + "✅ The script will now:")
                print(Fore.WHITE + "   • Look for your grenade launcher on screen")
                print(Fore.WHITE + "   • Click on it automatically when found") 
                print(Fore.WHITE + "   • Perform movement keys (A and D)")
                print(Fore.WHITE + "   • Handle respawning automatically")
                print(Fore.MAGENTA + f"💡 Remember: Press 'Q' to stop safely at any time!" + Style.RESET_ALL)
                threading.Thread(target=auto.run, daemon=True).start()
            except Exception as e:
                print(Fore.RED + f"❌ Error starting automation: {e}" + Style.RESET_ALL)

        elif choice == '2':
            print(Fore.CYAN + f"\n🎯 You chose: Universal Weapon Automation")
            try:
                # Start Any Gun automation in a background thread
                auto = AutoAnyGun()
                print(Fore.GREEN + "\n🚀 Starting Universal Weapon automation...")
                print(Fore.YELLOW + "✅ The script will now:")
                print(Fore.WHITE + "   • Look for your weapon on screen")
                print(Fore.WHITE + "   • Click on it automatically when found")
                print(Fore.WHITE + "   • Switch to your chosen weapon type")
                print(Fore.WHITE + "   • Perform movement keys (A and D)")
                print(Fore.WHITE + "   • Handle respawning automatically")
                print(Fore.MAGENTA + f"� Remember: Press 'Q' to stop safely at any time!" + Style.RESET_ALL)
                threading.Thread(target=auto.run, daemon=True).start()
            except Exception as e:
                print(Fore.RED + f"❌ Error starting automation: {e}" + Style.RESET_ALL)
        else:
            # Invalid menu choice
            print(Fore.RED + f"❌ '{choice}' is not a valid option.")
            print(Fore.YELLOW + "Please run the script again and choose either 1 or 2." + Style.RESET_ALL)
            sys.exit(1)

        # --- Only now, after all setup, start the Discord screenshot thread ---
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
        print(Fore.WHITE + "   • Looking for your weapon")
        print(Fore.WHITE + "   • Automatically clicking and moving")
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
        # Catch any unexpected error in the main logic
        print(Fore.RED + f"\n❌ Unexpected error occurred: {e}")
        print(Fore.YELLOW + "💡 Try restarting the script. If the problem persists, check:")
        print(Fore.WHITE + "   • Roblox Rivals is running")
        print(Fore.WHITE + "   • You're in a game (not in lobby)")
        print(Fore.WHITE + "   • Your weapon is visible on screen" + Style.RESET_ALL)
        sys.exit(1)

    # Keep the script running as long as any background thread is alive
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

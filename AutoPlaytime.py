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
init(autoreset=True)


class TrackProgress:
    # ========== CONFIG FOR PROGRESS ==========
    @staticmethod
    def from_user_input():
        webhook_url = input("Enter your Discord webhook URL: ").strip()
        try:
            interval_seconds = int(input("Enter screenshot interval in seconds (e.g., 600): ").strip())
        except ValueError:
            interval_seconds = 600
            print("Invalid input. Using default interval: 600 seconds.")
        # Always use 'q' as the kill key
        kill_key = 'q'
        print(Fore.YELLOW + "The kill key for stopping screenshots is now always 'q' (same as automation exit)." + Style.RESET_ALL)
        discord_user_id = input("Enter your Discord User ID to @mention: ").strip()
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
        print(Fore.CYAN + "\n🔫 [Any Gun Setup]")
        print(Fore.YELLOW + "Let's configure your automation for any weapon!" + Style.RESET_ALL)
        # Equipment type
        print(Fore.CYAN + "Choose your equipment type:")
        print(Fore.YELLOW + "  - primary: Your main weapon")
        print(Fore.YELLOW + "  - secondary: Your backup weapon")
        print(Fore.YELLOW + "  - melee: Knife or melee weapon")
        print(Fore.YELLOW + "  - utility: Grenades or gadgets" + Style.RESET_ALL)
        self.WHAT_EQUIP = input(Fore.CYAN + "🛠️  What equipment do you want to use? (default: primary): " + Style.RESET_ALL).strip().lower() or "primary"
        if self.WHAT_EQUIP not in ['primary', 'secondary', 'melee', 'utility']:
            print(Fore.RED + "❌ Invalid equipment choice. Defaulting to 'primary'." + Style.RESET_ALL)
            self.WHAT_EQUIP = 'primary'

        # Switch method
        print(Fore.CYAN + "\n🔄 Choose how to switch weapons:")
        print(Fore.YELLOW + "  1: Use number keys (1-4)")
        print(Fore.YELLOW + "  2: Use your custom keybind for 'Equip Next Weapon'" + Style.RESET_ALL)
        self.SWITCH_METHOD = input(Fore.CYAN + "🔢 Switch guns with Method 1 or 2? (default: 1): " + Style.RESET_ALL).strip() or "1"
        if self.SWITCH_METHOD not in ['1', '2']:
            print(Fore.RED + "❌ Invalid switch method choice. Defaulting to '1'." + Style.RESET_ALL)
            self.SWITCH_METHOD = '1'

        self.KEYBIND = None
        if self.SWITCH_METHOD == '2':
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
                    break

        # Only ask ONCE here:
        print(Fore.CYAN + "\n🖼️  You can capture a new detection image for your gun if needed.")
        answer = input(Fore.CYAN + "Capture a new userGun.png? (y/n): " + Style.RESET_ALL).strip().lower()
        if answer == 'y':
            self.capture_and_save_gun_screenshot()

        try:
            self.SLOT = int(input(Fore.CYAN + "🔢 Enter SLOT value (default 3): " + Style.RESET_ALL).strip() or "3")
        except ValueError:
            self.SLOT = 3
            print(Fore.RED + "❌ Invalid input. Using default SLOT = 3." + Style.RESET_ALL)

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

    def click(self):
        mouse = Controller()
        mouse.click(Button.left)

    def find_gun_and_press_keys(self):
        try:
            location = pyautogui.locateCenterOnScreen(os.path.join('pics', 'userGun.png'), grayscale=True, confidence=0.65)
        except Exception:
            print("userGun.png not found on screen (exception).")
            return False

        if location:
            print("userGun.png found!")
            self.last_gun_time = time.time()
            for i in range(4):
                keyboard.press_and_release('\\')
                time.sleep(0.1)
                for _ in range(1 + self.SLOT):
                    keyboard.press_and_release('s')
                    time.sleep(0.15)
                keyboard.press_and_release('enter')
                keyboard.press_and_release('\\')
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
            print(f"Error checking for Respawn: {e}")

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

                if self.last_gun_time and (time.time() - self.last_gun_time) <= 420:
                    self.click()

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

                if self.last_gun_time and (time.time() - self.last_gun_time) <= 420:
                    self.click()

# --------- Auto G Nade -------

class AutoGNade:
    def __init__(self):
        print(Fore.CYAN + "\n💥 [Glass Wrap (GNade) Setup]")
        print(Fore.YELLOW + "Let's configure your automation for the grenade launcher!" + Style.RESET_ALL)
        # Offer help for grid setting
        print(Fore.CYAN + "⚠️  Make sure your weapon picker mode is set to " + Fore.YELLOW + "GRID" + Fore.CYAN + " in-game for Glass Wrap automation!" + Style.RESET_ALL)
        need_help = input(Fore.CYAN + "❓ Need help finding the grid setting? (y/n): " + Style.RESET_ALL).strip().lower()
        if need_help == 'y':
            try:
                os.startfile(os.path.join('pics', 'grid.png'))
                print(Fore.GREEN + "✅ Opened grid.png for reference." + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"❌ Could not open grid.png: {e}" + Style.RESET_ALL)
        # Option to take a custom GNade.png screenshot
        custom = input(Fore.CYAN + "🖼️  Take a custom GNade.png? (y/n): " + Style.RESET_ALL).strip().lower()
        if custom == 'y':
            print(Fore.YELLOW + "📸 You'll now select the region of your screen that contains the grenade launcher icon." + Style.RESET_ALL)
            self.capture_and_save_gnade_screenshot()
        # Slot help for GNade
        print(Fore.CYAN + "🗂️  You will now be prompted for the SLOT value (which slot your grenade launcher is in)." + Style.RESET_ALL)
        slot_help = input(Fore.CYAN + "❓ Need help finding your slot number? (y/n): " + Style.RESET_ALL).strip().lower()
        if slot_help == 'y':
            try:
                os.startfile(os.path.join('pics', 'grid-slot.png'))
                print(Fore.GREEN + "✅ Opened grid-slot.png for reference." + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"❌ Could not open grid-slot.png: {e}" + Style.RESET_ALL)
        while True:
            try:
                self.SLOT = int(input(Fore.CYAN + "🔢 Enter SLOT value (which slot your grenade launcher is in): " + Style.RESET_ALL))
                break
            except ValueError:
                print(Fore.RED + "❌ Invalid input. Please enter an integer." + Style.RESET_ALL)
        self.last_gun_time = None

    def click(self):
        mouse = Controller()
        mouse.click(Button.left)
        
    def check_and_press_respawn(self):
        try:
            found1 = pyautogui.locateOnScreen(os.path.join('pics', 'Respawn.png'), grayscale=True, confidence=0.8)
            found2 = pyautogui.locateOnScreen(os.path.join('pics', 'Respawn2.png'), grayscale=True, confidence=0.8)
            if found1 or found2:
                print("Respawn button detected! Pressing SPACE.")
                keyboard.press_and_release('space')
                time.sleep(0.5)
        except Exception as e:
            print(f"Error checking for Respawn: {e}")

    def find_gun_and_press_keys(self):
        try:
            # Use correct path for GNade.png in the pics folder
            location = pyautogui.locateCenterOnScreen(os.path.join('pics', 'GNade.png'), grayscale=True, confidence=0.65)
        except pyautogui.ImageNotFoundException:
            print("GNade.png not found on screen (exception).")
            return

        if location:
            print("GNade.png found!")
            self.last_gun_time = time.time()
            for i in range(4):
                keyboard.press_and_release('\\')
                time.sleep(0.1)
                for _ in range(1 + self.SLOT):
                    keyboard.press_and_release('s')
                    time.sleep(0.15)
                keyboard.press_and_release('enter')
                keyboard.press_and_release('\\')
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

            if self.last_gun_time and (time.time() - self.last_gun_time) <= 420:
                self.click()

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
        print(Fore.CYAN + "This script can auto farm play time and send periodic screenshots to a Discord webhook for progress tracking." + Style.RESET_ALL)
        print(Fore.MAGENTA + "Press " + Fore.YELLOW + "'q'" + Fore.MAGENTA + " at any time to exit ALL automation and Discord tracking.\n" + Style.RESET_ALL)

        # Discord webhook tracking setup
        print(Fore.BLUE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
        track = input(Fore.CYAN + "🔗 Do you want to track progress to a Discord webhook? (y/n): " + Style.RESET_ALL).strip().lower()
        progress = None
        if track == 'y':
            print(Fore.GREEN + "📝 You'll be prompted for your Discord webhook URL, screenshot interval, and Discord user ID for mentions." + Style.RESET_ALL)
            try:
                progress = TrackProgress.from_user_input()
                print("📐 Please select the region for Discord screenshot tracking...")
                progress.select_region()  # Wait for user to select region before starting thread
            except Exception as e:
                print(Fore.RED + f"❌ Error in Discord progress tracking: {e}" + Style.RESET_ALL)

        # Automation type selection menu
        print(Fore.BLUE + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
        print(Fore.MAGENTA + "🤖 Which automation do you want to use?" + Style.RESET_ALL)
        print(Fore.CYAN + "1. Glass Wrap (grenade launcher) " + Fore.YELLOW + "💥 - Automates using the grenade launcher for glass wrap farming.")
        print(Fore.CYAN + "2. Any Gun " + Fore.GREEN + "🔫 - Automates any weapon. Lets you pick equipment type, switching method, and region for detection." + Style.RESET_ALL)
        print(Fore.BLUE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
        choice = input(Fore.CYAN + "👉 Enter 1 for Glass Wrap or 2 for Any Gun: " + Style.RESET_ALL).strip()

        if choice == '1':
            try:
                auto = AutoGNade()
                print(Fore.GREEN + "🚀 Starting Glass Wrap automation... Press 'q' to exit at any time." + Style.RESET_ALL)
                threading.Thread(target=auto.run, daemon=True).start()
            except Exception as e:
                print(Fore.RED + f"❌ Error in Glass Wrap automation: {e}" + Style.RESET_ALL)

        elif choice == '2':
            # Any Gun automation setup
            print(Fore.YELLOW + "\n[Any Gun Automation] 🔫" + Style.RESET_ALL)
            print(Fore.GREEN + "This mode lets you automate any weapon. You can choose:" + Style.RESET_ALL)
            print(Fore.CYAN + "- Equipment type (primary, secondary, melee, utility)")
            print(Fore.CYAN + "- How to switch weapons (number keys or custom keybind)")
            print(Fore.CYAN + "- Whether to capture a new detection image for your gun")
            print(Fore.YELLOW + "You'll be prompted for each option." + Style.RESET_ALL)
            print(Fore.CYAN + "⚠️  Make sure your weapon picker mode is set to " + Fore.YELLOW + "LIST" + Fore.CYAN + " in-game for Any Gun automation!" + Style.RESET_ALL)
            # Offer help for list setting
            need_help = input(Fore.CYAN + "❓ Need help finding the list setting? (y/n): " + Style.RESET_ALL).strip().lower()
            if need_help == 'y':
                try:
                    os.startfile(os.path.join('pics', 'list.png'))
                    print(Fore.GREEN + "✅ Opened list.png for reference." + Style.RESET_ALL)
                except Exception as e:
                    print(Fore.RED + f"❌ Could not open list.png: {e}" + Style.RESET_ALL)
            # Slot help for Any Gun
            slot_help = input(Fore.CYAN + "❓ Need help finding your slot number? (y/n): " + Style.RESET_ALL).strip().lower()
            if slot_help == 'y':
                try:
                    os.startfile(os.path.join('pics', 'list-slot.png'))
                    print(Fore.GREEN + "✅ Opened list-slot.png for reference." + Style.RESET_ALL)
                except Exception as e:
                    print(Fore.RED + f"❌ Could not open list-slot.png: {e}" + Style.RESET_ALL)
            try:
                # Start Any Gun automation in a background thread
                auto = AutoAnyGun()
                print(Fore.GREEN + "🚀 Starting Any Gun automation... Press 'q' to exit at any time." + Style.RESET_ALL)
                threading.Thread(target=auto.run, daemon=True).start()
            except Exception as e:
                print(Fore.RED + f"❌ Error in Any Gun automation: {e}" + Style.RESET_ALL)
        else:
            # Invalid menu choice
            print(Fore.RED + "❌ Invalid choice. Exiting." + Style.RESET_ALL)

        # --- Only now, after all setup, start the Discord screenshot thread ---
        if progress:
            def run_progress():
                progress.run(skip_region=True)
            threading.Thread(target=run_progress, daemon=True).start()

    except Exception as e:
        # Catch any unexpected error in the main logic
        print(Fore.RED + f"❌ Unexpected error: {e}" + Style.RESET_ALL)

    # Keep the script running as long as any background thread is alive
    while True:
        alive_threads = [t for t in threading.enumerate() if t is not threading.main_thread()]
        if not alive_threads:
            break
        time.sleep(1)

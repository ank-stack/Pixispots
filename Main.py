import pyautogui
import pydirectinput
import pygetwindow as gw
import tkinter as tk
from tkinter import ttk
import time
import sys, os
import keyboard
import threading
from datetime import datetime, timezone
import requests
import pytz

stop_macro_flag = threading.Event()

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller .exe"""
    try:
        base_path = sys._MEIPASS  # PyInstaller extracts to temp here
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Paths
data_dir = resource_path("data")
esc_dir = resource_path("data/esc")
esc_mark = resource_path("data/esc/Invite_Friends.png")
chat_dir = resource_path("data/chat")
chat_close_dir = resource_path('data/chat/chat_close.png')
chat_open_dir = resource_path("data/chat/chat_open.png")
leader_dir = resource_path("data/leaderboard")
leader_png = resource_path("data/leaderboard/image.png")
stock_dir = resource_path("data/stock")
NoStock_png = resource_path("data/stock/No_Stock.png")
No_Stock_honey = resource_path("data/stock/No_Stock_honey.png")
Red_Cross_dir = resource_path("data/Red Cross")
Close_Button_png = resource_path("data/Red Cross/Close_Button.png")
odds_png = resource_path("data/odds.png")
Fail_safe_dir = resource_path("data/Fail_Safe")
Restock_Robux_png = resource_path("data/Fail_Safe/Restock_Robux.png")
robux_store_icon = resource_path("data/Fail_Safe/robux_store_icon.png")
robux_store_icon_honey = resource_path("data/Fail_Safe/robux_store_icon_honey.png")
Settings = resource_path("data/Fail_Safe/Settings.png")
Shop = resource_path("data/Fail_Safe/Shop.png")
egg_dir = resource_path("data/egg")
# Running Func
global Is_Buying_Seeds, Is_Buying_Gears, Is_Buying_Eggs, Is_Buying_Honey
Is_Buying_Seeds = False
Is_Buying_Gears = False
Is_Buying_Eggs = False
Is_Buying_Event = False

# List of Items
seeds_list = {"Carrot Seed":1, "Strawberry Seed":2, "Blueberry Seed":3, "Tomato Seed":4, "Cauliflower Seed":5, "Watermelon Seed":6,"Rafflesia  Seed":7, "Green Apple Seed":8, 
            "Avokado Seed":9, "Banana Seed":10,"Pineapple Seed":11, "Kiwi Seed":12, "Bell Pepper Seed":13, "Prickly Pear Seed":14, "Loquat Seed":15, "Feijoa Seed":16, 
            "Pitcher Plant":17,"Sugar Apple Seed":18}

gears_list = {"Watering Can":1,"Trowel":2,"Recall Wrench":3,"Basic Sprinkler":4,"Advanced Sprinkler":5,"Godly Sprinkler":6,"Magnifying Glass":7, "Tanning Mirror":8,
            "Master Sprinkler":9, "Cleaning Spray":10,"Favorite Tool":11,"Harvest Tool":12,"Frindship Pot":13}

eggs_list = {"Common Egg":1,"Common Summer Egg":2,"Rare Summer Egg":3,"Mythical Egg":4,"Paradise Egg":5,"Bug Egg":6,"Bee Egg":7}

event_shop_list= {"Flower Seed Pack":1,"Lavender Seed":3,"Nectarshade Seed":4,"Necrarine Seed":5,"Hive Fruit Seed":6,"Pollen Radar":7,"Nectar Staff":8,
                "Honey Sprinkler":9,"Bee Egg":10, "Bee Crate":12,"Honey Comb":14,"Bee Chair":15,"Honey Torch":16,"Honey Walkway":17}

special_odd_items = {"Flower Seed Pack"}

# Vars
seeds_vars = {}
gears_vars = {}
eggs_vars = {}
event_shop_vars = {}

# URLs
five_min_url = "https://raw.githubusercontent.com/ank-stack/Grow-A-Garden-Macro/refs/heads/main/five_minutes_timer.json"
thirty_min_url = "https://raw.githubusercontent.com/ank-stack/Grow-A-Garden-Macro/refs/heads/main/thirty_minutes_timer.json"

# Main UI
class MacroUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pixispots")
        self.geometry("870x380+810+240")
        self.configure(bg="#1e1e1e")

        # Configure grid
        self.columnconfigure(0, weight=1)  # Side menu
        self.columnconfigure(1, weight=0)  # Main notebook
        self.columnconfigure(2, weight=0)  # Timer & Logs
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        # Left side panel for buttons
        self.side_menu = tk.Frame(self, bg="#1e1e1e")
        self.side_menu.grid(row=0, column=0, sticky="ns")

        self.build_side_buttons()
        
        # Hide notebook tab bar
        style = ttk.Style()
        style.layout("TNotebook.Tab", [])  # Hides the tabs

        # Center: Main notebook tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=1, sticky="nsew")

        # Right panel: Timer & Logs
        self.side_panel = tk.Frame(self, bg="#1e1e1e")
        self.side_panel.grid(row=0, column=2, sticky="ns")

        self.side_panel.config(width=240)
        self.side_panel.grid_propagate(False)

        self.build_timer_ui()
        self.build_log_ui()

        # Configure the side_panel grid to handle both timers and logs.
        self.side_panel.grid_rowconfigure(0, weight=0)  # First row for timers
        self.side_panel.grid_rowconfigure(1, weight=10)  # Second row for logs
        self.side_panel.grid_columnconfigure(0, weight=0)  # Single column

        # Bottom status bar
        self.status_label = tk.Label(self, text="STATUS: STOPPED", font=("Arial", 14, "bold"),
                                     bg="#1e1e1e", fg="red")
        self.status_label.grid(row=1, column=0, columnspan=3, sticky="ew", pady=4)

        self.watermark = tk.Label(self,text="discord.gg/EjBdR9hzQ4", font=('Arial',14,'bold'),
                                bg="#1e1e1e", fg="White")
        self.watermark.grid(row=2,column=0,columnspan=3, sticky="ew", pady=2)

        # Tabs dictionary
        self.tabs = {}
        for tab_name in ["Seeds", "Gears", "Eggs", "Cosmetics", "Settings", "Summer", "Donate", "Credits"]:
            tab = tk.Frame(self.notebook, bg="#1e1e1e")
            self.notebook.add(tab, text=tab_name)
            self.tabs[tab_name] = tab

        # Build the actual content inside each tab
        self.build_seed_tab(self.tabs["Seeds"])
        self.build_gear_tab(self.tabs["Gears"])
        self.build_egg_tab(self.tabs["Eggs"])
        self.build_setting_tab(self.tabs["Settings"])
        #self.build_event_tab(self.tabs["Summer"])

        # Load saved config
        load_configuration(self)

        # Register hotkeys
        keyboard.add_hotkey("F1", lambda: resize())
        keyboard.add_hotkey("F2", lambda: app.start_macro())
        keyboard.add_hotkey("F4", lambda: app.stop_macro())
        keyboard.add_hotkey("F5", lambda: fix_camera())
        keyboard.add_hotkey("F8", lambda: test_func())

        # Buttons for UI
        #tk.Button(self, text="Start Macro (F5)", command=buy_seeds).pack()
        #tk.Button(self, text="Stop Macro (F7)", command=self.stop_macro).pack()

    # Build Side buttons
    def build_side_buttons(self):
        buttons = [
            ("SEED", lambda: self.notebook.select(self.tabs["Seeds"])),
            ("GEAR", lambda: self.notebook.select(self.tabs["Gears"])),
            ("EGG", lambda: self.notebook.select(self.tabs["Eggs"])),
            ("COSMETIC", lambda: self.notebook.select(self.tabs["Cosmetics"])),
            ("EVENT", lambda: self.notebook.select(self.tabs["Summer"])),
            ("SETTING", lambda: self.notebook.select(self.tabs["Settings"])),
        ]

        for text, command in buttons:
            btn = tk.Button(self.side_menu, text=text, command=command,
                            bg="#333333", fg="white", font=("Arial", 8, "bold"),
                            relief="flat", anchor="center", width=10, height=1)
            btn.pack(fill="x", pady=4)

    # SEED TAB
    def build_seed_tab(self, tab):
        # Outer frame
        seed_frame = tk.LabelFrame(self.notebook.nametowidget(tab), text="Seed Shop Items", fg="lime",
                                   bg="#1e1e1e", font=('Arial', 10, 'bold'), padx=10, pady=10)
        seed_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Select All Seeds checkbox
        self.select_all_seed_var = tk.IntVar()
        select_all_cb = tk.Checkbutton(seed_frame, text="Select All Seeds", fg="white", bg="#1e1e1e",
                                    selectcolor="#1e1e1e", activebackground="#1e1e1e",
                                    font=("Arial", 10), variable=self.select_all_seed_var,
                                    command=self.toggle_all_seeds)
        select_all_cb.grid(row=0, column=0, columnspan=3, sticky="w")

        # Seed Checkbuttons in grid layout
        row_offset = 1
        for index, name in enumerate(seeds_list):
            seed_var = tk.IntVar()
            seeds_vars[name] = seed_var
            cb = tk.Checkbutton(seed_frame, text=name, fg="white", bg="#1e1e1e",
                                selectcolor="#1e1e1e", activebackground="#1e1e1e",
                                font=("Arial", 10), variable=seed_var, command=save_configuration)
            r = row_offset + index // 3
            c = index % 3
            cb.grid(row=r, column=c, sticky="w", padx=10, pady=2)

    def toggle_all_seeds(self):
        val = self.select_all_seed_var.get()
        for var in seeds_vars.values():
            var.set(val)

        save_configuration()

    # GEAR TAB
    def build_gear_tab(self, tab):
        # Outer frame
        gear_frame = tk.LabelFrame(self.notebook.nametowidget(tab), text="Gear Shop Items", fg="lightblue",
                                   bg="#1e1e1e", font=('Arial', 10, 'bold'), padx=10, pady=10)
        gear_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Select All gears checkbox
        self.select_all_gear_var = tk.IntVar()
        select_all_cb = tk.Checkbutton(gear_frame, text="Select All Gears", fg="white", bg="#1e1e1e",
                                    selectcolor="#1e1e1e", activebackground="#1e1e1e",
                                    font=("Arial", 10), variable=self.select_all_gear_var,
                                    command=self.toggle_all_gears)
        select_all_cb.grid(row=0, column=0, columnspan=3, sticky="w")

        # Seed Checkbuttons in grid layout
        row_offset = 1
        for index, name in enumerate(gears_list):
            gear_var = tk.IntVar()
            gears_vars[name] = gear_var
            cb = tk.Checkbutton(gear_frame, text=name, fg="white", bg="#1e1e1e",
                                selectcolor="#1e1e1e", activebackground="#1e1e1e",
                                font=("Arial", 10), variable=gear_var,command=save_configuration)
            r = row_offset + index // 3
            c = index % 3
            cb.grid(row=r, column=c, sticky="w", padx=10, pady=2)

    def toggle_all_gears(self):
        val = self.select_all_gear_var.get()
        for var in gears_vars.values():
            var.set(val)

        save_configuration()

    # EGG TAB
    def build_egg_tab(self, tab):
        # Outer frame
        gear_frame = tk.LabelFrame(self.notebook.nametowidget(tab), text="Gear Shop Items", fg="yellow",
                                   bg="#1e1e1e", font=('Arial', 10, 'bold'), padx=10, pady=10)
        gear_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Select All eggs checkbox
        self.select_all_egg_var = tk.IntVar()
        select_all_cb = tk.Checkbutton(gear_frame, text="Select All Gears", fg="white", bg="#1e1e1e",
                                    selectcolor="#1e1e1e", activebackground="#1e1e1e",
                                    font=("Arial", 10), variable=self.select_all_egg_var,
                                    command=self.toggle_all_eggs)
        select_all_cb.grid(row=0, column=0, columnspan=3, sticky="w")

        # Seed Checkbuttons in grid layout
        row_offset = 1
        for index, name in enumerate(eggs_list):
            egg_var = tk.IntVar()
            eggs_vars[name] = egg_var
            cb = tk.Checkbutton(gear_frame, text=name, fg="white", bg="#1e1e1e",
                                selectcolor="#1e1e1e", activebackground="#1e1e1e",
                                font=("Arial", 10), variable=egg_var,command=save_configuration)
            r = row_offset + index // 3
            c = index % 3
            cb.grid(row=r, column=c, sticky="w", padx=10, pady=2)

    def toggle_all_eggs(self):
        val = self.select_all_egg_var.get()
        for var in eggs_vars.values():
            var.set(val)

        save_configuration()
        
    # SETTING TAB
    def build_setting_tab(self, tab):

        global auto_align

        frame = tk.LabelFrame(self.notebook.nametowidget(tab), text="Settings", fg="white",
                            bg="#1e1e1e", font=('Arial', 10, 'bold'), padx=10, pady=10)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # grid_columnconfigure
        frame.columnconfigure(0,weight=1,minsize=10)
        frame.columnconfigure(1,weight=10,minsize=10)
        frame.columnconfigure(2,weight=1,minsize=10)
        frame.columnconfigure(3,weight=1,minsize=10)

        # Webhook URL
        tk.Label(frame, text="Webhook URL:", fg="white", bg="#1e1e1e", font=('Arial', 9)).grid(row=0, column=0, sticky="w")
        self.webhook_entry = tk.Entry(frame, width=25, font=("Arial", 9))
        self.webhook_entry.grid(row=0, column=1, padx=3, pady=1)
        self.webhook_entry.bind("<KeyRelease>", lambda e: save_configuration())
        tk.Button(frame, text="Save Webhook", command=lambda: print("Webhook Saved")).grid(row=0, column=2, padx=5)

        # Discord User ID
        tk.Label(frame, text="Discord User ID:", fg="white", bg="#1e1e1e", font=('Arial', 9)).grid(row=1, column=0, sticky="w")
        self.userid_entry = tk.Entry(frame, width=25, font=("Arial", 9))
        self.userid_entry.grid(row=1, column=1, padx=3, pady=1)
        self.userid_entry.bind("<KeyRelease>", lambda e: save_configuration())
        tk.Button(frame, text="Save UserID", command=lambda: print("User ID Saved")).grid(row=1, column=2, padx=5)

        # Private Server URL
        tk.Label(frame, text="Private Server URL:", fg="white", bg="#1e1e1e", font=('Arial', 9)).grid(row=2, column=0, sticky="w")
        self.server_entry = tk.Entry(frame, width=25, font=("Arial", 9))
        self.server_entry.grid(row=2, column=1, padx=3, pady=1)
        self.server_entry.bind("<KeyRelease>", lambda e: save_configuration())
        tk.Button(frame, text="Save Link", command=lambda: print("Link Saved")).grid(row=2, column=2, padx=5)

        # Checkbuttons
        self.discord_ping = tk.IntVar()
        self.auto_align = tk.BooleanVar()
        self.fast_mode = tk.IntVar()
        self.multi_instance = tk.IntVar()

        # Discord Ping Checkbutton
        self.Webhook = tk.Checkbutton(frame, text="Discord Pings", variable=self.discord_ping, bg="#1e1e1e", fg="white",
                        selectcolor="#1e1e1e", activebackground="#1e1e1e", command=save_configuration)
        self.Webhook.grid(row=3, column=0, sticky="w", pady=2)

        # Auto Align Checkbutton
        self.AutoAlign = tk.Checkbutton(frame, text="Auto-Align", variable=self.auto_align, bg="#1e1e1e", fg="white",
                        selectcolor="#1e1e1e", activebackground="#1e1e1e", command=save_configuration)
        self.AutoAlign.grid(row=4, column=0, sticky="w", pady=2)

        # UI navigation key
        tk.Label(frame, text="UI navigation key:", fg="white", bg="#1e1e1e", font=('Arial', 9)).grid(row=7, column=0, sticky="w", pady=(8, 0))
        self.ui_nav_key = tk.Entry(frame, width=10, font=("Arial", 10))
        self.ui_nav_key.insert(0, "\\")
        self.ui_nav_key.grid(row=7, column=1, sticky="w", pady=(8,1))
        self.ui_nav_key.bind("<KeyRelease>", lambda e: save_configuration())

        # Save/Clear buttons
        tk.Button(frame, text="Clear Saves", command=lambda: print("Cleared")).grid(row=2, column=3, padx=5)

        # Start/Stop Buttons
        tk.Button(frame, text="Start Macro (F5)", width=16, bg="white", fg="black", font=("Arial", 9, "bold")).grid(row=8, column=0, pady=5)
        tk.Button(frame, text="Stop Macro (F4)", width=16, bg="white", fg="black", font=("Arial", 9, "bold"),command=self.stop_macro).grid(row=8, column=1, pady=5)

    def start_macro(self, event=None):
        print("Macro Started")
        stop_macro_flag.clear()
        self.status_label.config(text="STATUS: RUNNING", fg="lime")
        if hasattr(self, "settings_status_label"):
            self.settings_status_label.config(text="STATUS: RUNNING", fg="lime")
        threading.Thread(target=main_loop, daemon=True).start()


    def stop_macro(self, event=None):
        print("Stopping macro...")
        stop_macro_flag.set()
        self.status_label.config(text="STATUS: STOPPED", fg="red")
        print("Macro stopped via hotkey (F4)")
        

    # Build Timer Ui
    def build_timer_ui(self):
        self.timer_frame = tk.LabelFrame(self.side_panel, text="TIMERS", fg="yellow", bg="#1e1e1e",
                                        font=("Arial", 10, "bold"), labelanchor='n')
        self.timer_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.timer_frame.config(width=100)

        self.seed_timer_label = tk.Label(self.timer_frame, text="SEED: 5m", fg="white", bg="#1e1e1e", font=("Arial", 9))
        self.seed_timer_label.grid(row=0, column=0, sticky="w")
        self.gear_timer_label = tk.Label(self.timer_frame, text="GEAR: 5m", fg="white", bg="#1e1e1e", font=("Arial", 9))
        self.gear_timer_label.grid(row=1, column=0, sticky="w")
        self.egg_timer_label = tk.Label(self.timer_frame, text="EGG: 30m", fg="white", bg="#1e1e1e", font=("Arial", 9))
        self.egg_timer_label.grid(row=2, column=0, sticky="w")
        self.event_timer_label = tk.Label(self.timer_frame, text="EVENT: 30m", fg="white", bg="#1e1e1e", font=("Arial", 9))
        self.event_timer_label.grid(row=3, column=0, sticky="w")

        self.start_universal_timer_updater(
            url="https://raw.githubusercontent.com/ankan-stack/Grow-A-Garden-Macro/main/seed_timer.json",
            label_widget=self.seed_timer_label,
            prefix="SEED",
            cycle_minutes=5
            )
        self.start_universal_timer_updater(
            url="https://raw.githubusercontent.com/ankan-stack/Grow-A-Garden-Macro/main/seed_timer.json",
            label_widget=self.gear_timer_label,
            prefix="GEAR",
            cycle_minutes=5
            )
        self.start_universal_timer_updater(
            url= thirty_min_url,
            label_widget=self.egg_timer_label,
            prefix="EGG",
            cycle_minutes=30
            )
        self.start_universal_timer_updater(
            url="https://raw.githubusercontent.com/ankan-stack/Grow-A-Garden-Macro/main/seed_timer.json",
            label_widget=self.event_timer_label,
            prefix="EVENT",
            cycle_minutes=60
            )

    # Build Log Ui
    def build_log_ui(self):
        self.log_frame = tk.LabelFrame(self.side_panel, text="LOGS", fg="yellow", bg="#1e1e1e",
                                    font=("Arial", 10, "bold"), labelanchor='n')
        self.log_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.log_frame.config(width=100)
        
        self.log_text = tk.Text(self.log_frame, height=10, width=30, bg="#1e1e1e", fg="white", font=("Consolas", 9), wrap="word")
        self.log_text.grid(row=0, column=0,padx=5, sticky="nsew")
        self.log_text.config(state="disabled")

    def start_universal_timer_updater(self, url, label_widget, prefix="TIMER", cycle_minutes=5):
        def update_loop():
            while True:
                try:
                    response = requests.get(url, timeout=5)
                    data = response.json()

                    start_time_str = data.get("cycle_start")
                    if not start_time_str:
                        raise ValueError("Missing 'cycle_start' in response.")

                    # Parse ISO datetime string
                    cycle_start = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
                    cycle_start = cycle_start.replace(tzinfo=pytz.UTC)
                    now = datetime.utcnow().replace(tzinfo=pytz.UTC)

                    # Calculate time until next cycle
                    elapsed = (now - cycle_start).total_seconds()
                    cycle_length = cycle_minutes * 60
                    remaining = cycle_length - (elapsed % cycle_length)

                    mins = int(remaining // 60)
                    secs = int(remaining % 60)

                    label_widget.config(text=f"{prefix}: {mins}m {secs}s")
                except Exception as e:
                    label_widget.config(text=f"{prefix}: Error")
                    print(f"[{prefix}] Timer fetch failed → {e}")

                time.sleep(1)

        threading.Thread(target=update_loop, daemon=True).start()

# CUSTOM CLICK
class Click:
    def __init__(self,name):
        self.name = name

    def M_Click(self,x,y):
        pydirectinput.moveTo(x,y)
        pydirectinput.moveTo(x+1,y)
        pydirectinput.moveTo(x-1,y)
        pydirectinput.moveTo(x,y+1)
        pydirectinput.moveTo(x,y-1)
        time.sleep(0.3)
        pydirectinput.click()

    def F_Click(self,x,y):
        pydirectinput.moveTo(x,y)
        pydirectinput.moveTo(x+1,y)
        pydirectinput.moveTo(x,y-1)
        time.sleep(0.2)
        pydirectinput.click()
    
    def Single_Click(self,x,y):
        pydirectinput.moveTo(x,y)
        pydirectinput.click()

    def Path_Click(self,path,reg,conf=8):
        try:
            locate = pyautogui.locateOnScreen(path,confidence=conf,region=reg)
            pydirectinput.moveTo(locate)
            pydirectinput.click
            print(f"{os.path.basename(path)} located on {locate} \n{os.path.basename(path)} Clicked")
            return True
        except FileNotFoundError:
            print(f"{path} not found")
            return False
        except pyautogui.ImageNotFoundException:
            print(f"Couldn't locate {os.path.basename(path)} on screen")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def __str__(self):
        return f'Clicked on {self.name}'
    
# key up and down class
class Press:
    def __init__(self,name):
        self.name = name

    def S_Press(self,key):
        pydirectinput.keyDown(key)
        pydirectinput.keyUp(key)
        return f"Key {key} Clicked"

    def M_Press(self,key,times):
        clicked = 0
        for _ in range(times):
            pydirectinput.keyDown(key)
            pydirectinput.keyUp(key)
            clicked +=1
        return f"Key {key} Clicked {clicked}"

# Main loop
def main_loop():
    print("Macro Started")
    stop_macro_flag.clear()

    resize()
    if stop_macro_flag.is_set(): return

    close_chat(chat_open_dir, chat_close_dir)
    if stop_macro_flag.is_set(): return

    leaderboard(leader_png)
    if stop_macro_flag.is_set(): return

    time.sleep(1)
    if stop_macro_flag.is_set(): return

    if app.auto_align.get():

        fix_camera()
        if stop_macro_flag.is_set(): return

    # Timer URLs
    five_min_url = "https://raw.githubusercontent.com/ankan-stack/Grow-A-Garden-Macro/main/five_minutes_timer.json"
    thirty_min_url = "https://raw.githubusercontent.com/ankan-stack/Grow-A-Garden-Macro/main/thirty_minutes_timer.json"

    first_run = True

    while not stop_macro_flag.is_set():
        if not first_run:
            # Wait for 5-minute cycle
            print("⌛ Waiting for 5-minute cycle to trigger")
            wait_until_next_cycle(five_min_url, 300)
            if stop_macro_flag.is_set(): return

        # 🔁 5-minute tasks
        if sum(seeds_list[name] for name, var in seeds_vars.items() if var.get() == 1) > 0:
            buy_seeds(NoStock_png)
            if stop_macro_flag.is_set(): return
        else:
            if stop_macro_flag.is_set(): return

        if sum(gears_list[name] for name, var in gears_vars.items() if var.get() == 1) > 0:
            buy_gears(NoStock_png)
            if stop_macro_flag.is_set(): return
        else:
            if stop_macro_flag.is_set(): return

        # ✅ On first run or when 30-minute cycle hits
        if first_run or should_run_30min_task(thirty_min_url):
            print("🔔 Running 30-minute tasks")

            if sum(eggs_list[name] for name, var in eggs_vars.items() if var.get() == 1) > 0:
                buy_eggs()
                if stop_macro_flag.is_set(): return

            #buy_honey(No_Stock_honey)
            if stop_macro_flag.is_set(): return

        first_run = False
        print("✅ Completed a full macro cycle.")

# Buy click
def buy_func(name, img):
    global Is_Buying_Seeds, Is_Buying_Gears, Is_Buying_Eggs, Is_Buying_Honey

    Func_click = Click("buy_func")
    Buy_press = Press('Buy Press')
    fail_safe_trigger = 0

    print(f"→ Entered buy_func for {name}")
    if stop_macro_flag.is_set(): return

    # Main buy logic
    print(f"Buying: {name}")
    pydirectinput.press('enter')
    pydirectinput.press('down')
    time.sleep(1)

    if name in special_odd_items:
        print(f"{name} is a special/odd item, performing extra step")
        pydirectinput.press('down')

    print("Opened Seed Buying option")

    while not stop_macro_flag.is_set():

        if fail_safe_trigger > 4:
            safe_open(name)
            print("Running Fail Safe Trigger")
            Buy_press.S_Press('up')
            Buy_press.S_Press('enter')
            Buy_press.S_Press('down')

        try:
            pyautogui.locateOnScreen(img, confidence=0.7)
            time.sleep(1)
            print("No stock detected, skipping.")
            pydirectinput.press('up')
            pydirectinput.press('enter')
            print("Closed seed window\n")
            break
        except pyautogui.ImageNotFoundException:
            fail_safe_trigger += 1
            print("Stock available, buying...")
            Buy_press.M_Press('enter', 8)
            time.sleep(0.2)

    print("Bought item and closed menu\n")

# Pre Fail safe
def safe_open(name):
    while True:
        pydirectinput.press('enter')
        try:
            item_open_mark = safe_locate(robux_store_icon,confidence=0.8)
            
            if item_open_mark:
                pydirectinput.press('enter')
                break
            if item_open_mark == None:
                break
        except Exception as e:
            print(f"ERROR: Unexpected {e}")

# Fail Safe
def handle_fail_safe(Func_click):
    global Is_Buying_Seeds, Is_Buying_Gears, Is_Buying_Eggs, Is_Buying_Honey

    store_icon = safe_locate(robux_store_icon, confidence=0.8)
    honey_icon = safe_locate(robux_store_icon_honey, confidence=0.8)
    cancel_icon = safe_locate(Restock_Robux_png, confidence=0.8)

    if store_icon or honey_icon or cancel_icon:

        pydirectinput.press('enter')
        pydirectinput.press('\\')
        close_stall(Close_Button_png)

        if cancel_icon:
            x = cancel_icon.left + cancel_icon.width // 2
            y = cancel_icon.top + cancel_icon.height // 2
            Func_click.F_Click(x, y)

        if Is_Buying_Seeds:
            Is_Buying_Seeds = False
            threading.Thread(target=buy_seeds, args=(NoStock_png,), daemon=True).start()
        elif Is_Buying_Gears:
            Is_Buying_Gears = False
            threading.Thread(target=buy_gears, args=(NoStock_png,), daemon=True).start()
        elif Is_Buying_Eggs:
            Is_Buying_Eggs = False
            threading.Thread(target=buy_eggs, daemon=True).start()
        elif Is_Buying_Honey:
            Is_Buying_Honey = False
            print("Fixing Camera")
            pydirectinput.click(408, 319)
            pydirectinput.mouseDown(button='right')
            pydirectinput.moveTo(408, 419, duration=1)
            pydirectinput.mouseUp(button='right')
            print("Fixed Camera")
            threading.Thread(target=buy_honey, args=(No_Stock_honey,), daemon=True).start()

        return True  # Fail-safe was triggered
    return False  # No fail-safe triggered

# Buy Seeds
def buy_seeds(img_path):

    global Is_Buying_Seeds

    if stop_macro_flag.is_set(): return
    
    Is_Buying_Seeds= True

    Buy_Press = Press("Buy")
    Buy_Click = Click("Buy")
    print("Running buy_seeds func")

    Buy_Click.F_Click(408,319)
    time.sleep(1)

    # Navigation to seed shop
    Buy_Press.S_Press('\\')
    Buy_Press.S_Press('down')
    Buy_Press.S_Press('enter')
    Buy_Press.S_Press('\\')
    time.sleep(0.3)
    if stop_macro_flag.is_set(): return
    Buy_Press.S_Press('e')  # Open shop
    time.sleep(2)
    if stop_macro_flag.is_set(): return

    # --- Detect seed reset timer ---
    print("Fetching global seed timer from GitHub...")
    github_timer_url = "https://raw.githubusercontent.com/ankan-stack/Grow-A-Garden-Macro/main/seed_timer.json"
    try:
        seed_timer_text = get_seed_timer(github_timer_url)
        print(f"Global Seed Timer: {seed_timer_text}")
        if hasattr(app, 'update_seed_timer'):
            app.update_seed_timer(seed_timer_text)

            if stop_macro_flag.is_set(): return
    except Exception as e:
        print(f"Failed to fetch seed timer: {e}")

    Buy_Press.S_Press('\\')
    Buy_Press.S_Press('\\')
    Buy_Press.S_Press('\\')
    Buy_Press.S_Press('down')
    Buy_Press.S_Press('down')
    print("In Seed Shop list pos 1")

    if stop_macro_flag.is_set(): return

    # Pre Fail Safe
    print("Running Pre Fail Safe")
    safe_open(name="Seed")

    if stop_macro_flag.is_set(): return

    # Get enabled seeds
    checked_seeds = [name for name, var in seeds_vars.items() if var.get() == 1]
    sorted_checked = sorted(checked_seeds, key=lambda x: seeds_list[x])

    current_pos = 1

    for seed in sorted_checked:
        if stop_macro_flag.is_set():
            return

        target_pos = seeds_list[seed]
        down_count = target_pos - current_pos

        if down_count > 0:
            for _ in range(down_count):
                if stop_macro_flag.is_set():
                    return
                Buy_Press.S_Press('down')
                time.sleep(0.1)
                if stop_macro_flag.is_set(): return

        buy_func(seed, img=img_path)
        current_pos = target_pos

    # Exit the shop
    Buy_Press.S_Press('\\')

    close_stall(Close_Button_png)

    Is_Buying_Seeds = False

# Buy gears
def buy_gears(img_path):

    global Is_Buying_Gears

    if stop_macro_flag.is_set():
        return

    Is_Buying_Gears = True

    print("Running buy_gears")

    # Going to gear
    GearClick = Click("Gear Click")
    time.sleep(1)
    if stop_macro_flag.is_set(): return
    pydirectinput.press('2')
    GearClick.F_Click(375, 195)
    if stop_macro_flag.is_set(): return

    # Open shop
    time.sleep(1.5)
    if stop_macro_flag.is_set(): return
    Open_Shop = Click("Open Shop")
    pydirectinput.press('e')
    time.sleep(2)
    if stop_macro_flag.is_set(): return
    Open_Shop.F_Click(663, 302)
    print("Opened Gear Shop")
    time.sleep(3)

    if stop_macro_flag.is_set(): return

    # Go to top of the shop list
    pydirectinput.press('\\')
    pydirectinput.press('\\')
    print("Restarting gear list from top")
    time.sleep(1.5)

    if stop_macro_flag.is_set(): return

    # Press again to focus list
    pydirectinput.press('\\')
    pydirectinput.press('down')
    pydirectinput.press('down')
    print("Moved to positions 1")
    time.sleep(1.5)

    if stop_macro_flag.is_set(): return

    # Pre Fail Safe
    print("Running Pre Fail Safe")
    safe_open(name="Seed")

    if stop_macro_flag.is_set(): return

    # Get checked gears
    checked_gears = [name for name, var in gears_vars.items() if var.get() == 1]
    sorted_checked = sorted(checked_gears, key=lambda x: gears_list[x])

    current_pos = 1  # start at position 1
    for gear in sorted_checked:
        if stop_macro_flag.is_set(): return

        target_pos = gears_list[gear]
        down_count = target_pos - current_pos

        print(f"target pos: {target_pos}")
        print(f"down count: {down_count}")

        if down_count > 0:
            print(f"Moving down {down_count} to reach {gear}")
            for _ in range(down_count):
                if stop_macro_flag.is_set():
                    return
                pydirectinput.press('down')
                time.sleep(0.1)

                if stop_macro_flag.is_set(): return
        else:
            print(f"{gear} is already selected")

        buy_func(gear, img=img_path)
        current_pos = target_pos

        if stop_macro_flag.is_set(): return

    # Exit shop
    pydirectinput.press('\\')

    close_stall(Close_Button_png)

    if stop_macro_flag.is_set(): return
    Is_Buying_Gears = False

# Buying Eggs
def buy_eggs():
    global Is_Buying_Eggs

    egg_click = Click("Egg")
    Is_Buying_Eggs = True

    print("Running Buy Eggs Func")

    if stop_macro_flag.is_set(): return

    # Go to gear area
    GearClick = Click("Gear Click")
    pydirectinput.press('2')
    time.sleep(1)
    GearClick.F_Click(375, 195)
    time.sleep(1)

    if stop_macro_flag.is_set(): return

    # Get selected eggs
    selected_eggs = [name for name, var in eggs_vars.items() if var.get() == 1]
    selected_egg_images = [os.path.join(egg_dir, f"{egg}.png") for egg in selected_eggs]

    def handle_egg():
        if stop_macro_flag.is_set(): return

        print("Opening Egg Details")
        pydirectinput.press('e')
        time.sleep(1.2)

        print("Checking for selected egg matches...")

        matched = False
        for img_path in selected_egg_images:
            try:
                if safe_locate(img_path, confidence=0.95):
                    Buy = Click("Egg Buy Click")
                    print(f"✅ Matched selected egg: {os.path.basename(img_path)} → Buying")
                    Buy.F_Click(374, 387)
                    time.sleep(0.5)
                    matched = True
                    break
            except pyautogui.ImageNotFoundException:
                continue

        if not matched:
            print("❌ No selected egg matched. Skipping...")

        # Fail-safe for egg refresh
        try:
            fail_icon = safe_locate(Restock_Robux_png, confidence=0.8)
            if fail_icon:
                x = fail_icon.left + fail_icon.width // 2
                y = fail_icon.top + fail_icon.height // 2
                egg_click.F_Click(x, y)
                print("⚠️ Egg refresh closed via fail-safe")
        except Exception as e:
            print("Fail-safe error:", e)

        # Close egg detail view
        Close = Click("Egg Close Click")
        Close.F_Click(546, 254)
        print("Closed Egg Details")

    # Navigate and process each egg (3 slots)
    """for i in range(3):
        if stop_macro_flag.is_set(): return
        if i > 0:
            pydirectinput.keyDown('down')
            time.sleep(0.1)
            pydirectinput.keyUp('down')
        print(f"Moved to egg {i + 1}")
        handle_egg()
        time.sleep(2)"""
    
    # First egg
    pydirectinput.keyDown('down')
    time.sleep(0.7)
    if stop_macro_flag.is_set(): return
    pydirectinput.keyUp('down')
    print("Moved to egg 1")
    handle_egg()
    if stop_macro_flag.is_set(): return

    time.sleep(2)
    if stop_macro_flag.is_set(): return

    # Second egg
    pydirectinput.keyDown('down')
    time.sleep(0.1)
    if stop_macro_flag.is_set(): return
    pydirectinput.keyUp('down')
    print("Moved to egg 2")
    handle_egg()
    if stop_macro_flag.is_set(): return

    time.sleep(2)
    if stop_macro_flag.is_set(): return

    # Third egg
    pydirectinput.keyDown('down')
    time.sleep(0.1)
    if stop_macro_flag.is_set(): return
    pydirectinput.keyUp('down')
    print("Moved to egg 3")
    handle_egg()
    if stop_macro_flag.is_set(): return

    Is_Buying_Eggs = False

# Buy Honey Shop
def buy_honey(img_path):

    global Is_Buying_Honey
    Is_Buying_Honey = True

    # Honey click
    Honey_click = Click("Honey")

    if not os.path.exists(No_Stock_honey):
        return

    if stop_macro_flag.is_set(): return
    
    # Go to Honey shop
    pydirectinput.press('\\')
    pydirectinput.press('down')
    pydirectinput.press('right')
    pydirectinput.press('right')
    pydirectinput.press('enter')
    pydirectinput.press('\\')
    if stop_macro_flag.is_set(): return

    # Center click [PREVENT FAIL]
    Honey_click.F_Click(408,319)
    if stop_macro_flag.is_set(): return

    # Move to Bee
    pydirectinput.keyDown('a')
    time.sleep(9.2)
    if stop_macro_flag.is_set(): return
    pydirectinput.keyUp('a')
    pydirectinput.keyDown('w')
    time.sleep(0.8)
    if stop_macro_flag.is_set(): return
    pydirectinput.keyUp('w')
    print("AT HONEY SHOP")
    time.sleep(1.5)
    if stop_macro_flag.is_set(): return

    # Open Shop
    pydirectinput.moveTo(408,319)
    pydirectinput.mouseDown(button='right')
    pydirectinput.moveTo(408,319-5)
    pydirectinput.mouseUp(button='right')
    pydirectinput.press('e')
    pydirectinput.press('e')
    print("Pressed E")
    time.sleep(1.5)
    if stop_macro_flag.is_set(): return
    Honey_click.F_Click(714, 382)
    Honey_click.F_Click(714, 382)
    print("Opened Shop")
    time.sleep(2)
    if stop_macro_flag.is_set(): return

    # Go to First in list
    pydirectinput.press('\\')
    pydirectinput.press('\\')
    time.sleep(0.5)
    if stop_macro_flag.is_set(): return

    # Press again to focus list
    pydirectinput.press('\\')
    pydirectinput.press('down')
    pydirectinput.press('down')
    print("Moved to positions 1")
    time.sleep(1.5)
    if stop_macro_flag.is_set(): return

    # Get checked honey
    checked_honey = [name for name, var in event_shop_vars.items() if var.get() == 1]
    sorted_honey_checked = sorted(checked_honey, key=lambda x: event_shop_list[x])

    current_pos = 1  # start at position 1
    for honey in sorted_honey_checked:
        if stop_macro_flag.is_set():
            return

        target_pos = event_shop_list[honey]
        down_count = target_pos - current_pos

        print(f"target pos: {target_pos}")
        print(f"down count: {down_count}")

        if down_count > 0:
            print(f"Moving down {down_count} to reach {honey}")
            for _ in range(down_count):
                if stop_macro_flag.is_set():
                    return
                pydirectinput.press('down')
                time.sleep(0.1)
        else:
            print(f"{honey} is already selected")

        buy_func(honey, img=img_path)
        current_pos = target_pos

    # Exit shop
    pydirectinput.press('\\')
    time.sleep(0.5)
    if stop_macro_flag.is_set(): return

    # Close stall
    close_stall(Close_Button_png)
    print("Honey func Executed: close_stall(Close_Button_png)")
    time.sleep(0.5)
    if stop_macro_flag.is_set(): return

    # Fix Camera
    print("\nFixing Camera")
    Honey_click.F_Click(408,319)
    pydirectinput.mouseDown(button='right')
    pydirectinput.moveTo(408,319 + 100, duration=1)
    pydirectinput.mouseUp(button='right')
    print("Fixed Camera")

    Is_Buying_Honey = False
    
    if stop_macro_flag.is_set(): return

# Camera Mode Settings
def camera_mode(image):
    while not stop_macro_flag.is_set():
        try:
            print("Trying")
            if not os.path.exists(image):
                print(f"ESC Mark not found {image} at {esc_dir}")
                break
            print(f"Looking for {os.path.basename(image)}")
            time.sleep(0.5)
            pyautogui.locateOnScreen(image,confidence=0.8)
            print(f"Esc Mark found, Button clicked Confirmed")
            # Click Settings 259, 115
            setting = Click("Settings")
            setting.M_Click(259, 115)
            # Click CameraMode 561, 232
            setting.F_Click(561, 232)
            setting.F_Click(561, 232)
            # Close Esc
            key = Press("esc")
            key.S_Press("esc")
            break

        except pyautogui.ImageNotFoundException:
            pydirectinput.moveTo(408,319)
            pydirectinput.click()
            print("Moved to Center")
            key = Press("esc")
            key.S_Press("esc")
            print("Pressed Esc")

# FORCE RESIZE
def resize():
    while not stop_macro_flag.is_set():
        windows = gw.getWindowsWithTitle("Roblox")
        if windows:
            win = windows[0]
            try:
                win.moveTo(-8, -8)
                win.resizeTo(816, 638)
                print("Roblox window resized")
                win.activate()  # this is the line that sometimes fails
            except Exception as e:
                print(f"Resize error: {e}")  # Safe fail

            # Refocus after 1 second
            app.after(1000, lambda: app.focus_force())
        else:
            print("Window Roblox not found.")
        return  # Prevent infinite loop!

# FIX CAMERA
Fix_Camera = True

def fix_camera():
    while not stop_macro_flag.is_set():
        while Fix_Camera:
            if stop_macro_flag.is_set(): return

            # Camera Mode Follow
            camera_mode(esc_mark)
            if stop_macro_flag.is_set(): return

            # zoom in and out
            time.sleep(0.5)
            if stop_macro_flag.is_set(): return
            pyautogui.scroll(30000)
            time.sleep(0.5)
            if stop_macro_flag.is_set(): return
            pyautogui.scroll(-1900)
            if stop_macro_flag.is_set(): return

            # Move the cursor to the center
            screen_width, screen_height = 816, 638
            center_x, center_y = screen_width // 2, screen_height // 2
            pydirectinput.moveTo(center_x, center_y)
            if stop_macro_flag.is_set(): return

            # Drag cursor below
            pydirectinput.mouseDown(button='right')
            pydirectinput.moveTo(center_x, center_y + 100, duration=1)
            pydirectinput.mouseUp(button='right')
            if stop_macro_flag.is_set(): return

            # Go to seed shop
            pydirectinput.press('\\')
            pydirectinput.press('down')
            pydirectinput.press('enter')
            pydirectinput.press('\\')
            time.sleep(1)

            # Move back and forth
            for _ in range(4):
                if stop_macro_flag.is_set(): return
                Sell_Seed = Click("sell seed")
                Sell_Seed.Single_Click(286, 111)
                Sell_Seed.Single_Click(526, 112)
                Sell_Seed.Single_Click(286, 111)
                Sell_Seed.Single_Click(526, 112)
            pydirectinput.press('\\')
            Sell_Seed.F_Click(286, 111)
            Sell_Seed.F_Click(286, 111)

            pydirectinput.press('\\')
            pydirectinput.press('down')
            pydirectinput.press('enter')
            pydirectinput.press('\\')

            # Camera Mode Default
            camera_mode(esc_mark)
            if stop_macro_flag.is_set(): return

            # Add Recall Wrench to 2
            time.sleep(1)
            if stop_macro_flag.is_set(): return

            pydirectinput.press('\\')
            pydirectinput.press('right')
            pydirectinput.press('enter')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('down')
            pydirectinput.press('enter')

            if stop_macro_flag.is_set(): return

            pydirectinput.keyDown('ctrl')
            pydirectinput.press('a')
            pydirectinput.keyUp('ctrl')

            for _ in range(3):
                if stop_macro_flag.is_set(): return
                pydirectinput.press('backspace')

            pyautogui.write("recall Wrench", interval=0.05)
            if stop_macro_flag.is_set(): return

            pydirectinput.press('enter')
            if stop_macro_flag.is_set(): return

            # Drag Recall Wrench
            DragClick = Click("drag")
            DragClick.F_Click(110, 298)
            DragClick.F_Click(110, 298)
            pydirectinput.mouseDown()
            time.sleep(0.2)
            if stop_macro_flag.is_set(): return
            pydirectinput.moveTo(172, 587)
            pydirectinput.mouseUp()
            if stop_macro_flag.is_set(): return

            pydirectinput.press('\\')
            DragClick.F_Click(375, 195)
            if stop_macro_flag.is_set(): return

            return  # only one cycle as per current logic

# Close Chat
def close_chat(open_img, close_img):
    if stop_macro_flag.is_set():
        return

    print("Starting close_chat")
    ChatButton = Click("chat")
    print(f"clicked on {ChatButton} 2 times")

    # Move to center for safe positioning
    pydirectinput.moveTo(408, 319)
    pydirectinput.click()
    print("Moved to Center")

    retries = 0
    max_retries = 10

    while not stop_macro_flag.is_set() and retries < max_retries:
        try:
            print("trying to locate open")
            if pyautogui.locateOnScreen(open_img, confidence=0.8):
                print("Found open chat image")
                ChatButton.F_Click(139, 59)
                print("Chat closed")
                break  # ✅ exit after closing
        except pyautogui.ImageNotFoundException:
            pass

        try:
            print("trying to locate close")
            if pyautogui.locateOnScreen(close_img, confidence=0.8):
                print("Found close chat image")
                print("Chat already closed")
                break  # ✅ exit if already closed
        except pyautogui.ImageNotFoundException:
            print("SAFE CLICK ACTIVATED")
            for _ in range(3):
                pydirectinput.click(139, 59)
                pydirectinput.moveTo(408, 319)

        retries += 1
        time.sleep(0.5)

    print("Exited close_chat loop")

# Close Leaderboard
def leaderboard(image):

    while not stop_macro_flag.is_set():

        if not os.path.exists(image):
            print(f"Leaderboard dir not found at {image}")
            break
        elif not os.path.exists(image):
            print(f"LeaderBoard Png not found at {image}")
            break
        else:
            print("LeaderBoard Png path found")
        
        try:
            pydirectinput.click(408,319)
            pyautogui.locateOnScreen(image,confidence=0.8)
            pydirectinput.press('tab')
            print("Image located on the screen \nPressed Tab")
            break
        except pyautogui.ImageNotFoundException:
            print("Image not matching from the screen")
            break

# Close Stall
def close_stall(img):
    while not stop_macro_flag.is_set():

        if not os.path.exists(Red_Cross_dir):
            print(f"Red Cross Folder Not found")
            break
        if not os.path.exists(Close_Button_png):
            print(f"Close_Button_png Not found")
            break
        try:
            print("Trying to locate Red Cross Button")
            red_cross = pyautogui.locateOnScreen(img,confidence=0.8)
            print("Found Red Cross Button")
            if red_cross:
                x = red_cross.left + red_cross.width // 2
                y = red_cross.top + red_cross.height // 2
                CloseB = Click("Close Button")
                CloseB.F_Click(x,y)
                print("Clicked on Red Cross Button")
                break
            else:
                print("Red cross not found, retrying...")
                time.sleep(1)

        except pyautogui.ImageNotFoundException:
            print("Retrying With another option")
            CloseStore = Click("Close Button")
            CloseStore.F_Click(49, 347)
            CloseStore.F_Click(49, 347)
            print("Clicked on shop button 2 times")
            break

# Get seed time for GitHub
def get_seed_timer(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        start_time = datetime.fromisoformat(data['cycle_start'].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)

        # Game resets every 5 minutes = 300 seconds
        elapsed = (now - start_time).total_seconds()
        countdown = 300 - (elapsed % 300)

        minutes = int(countdown // 60)
        seconds = int(countdown % 60)
        return f"{minutes}m {seconds:02d}s"
    except Exception as e:
        print("Error fetching seed timer:", e)
        return "Unavailable"

# Returns True if 30-minute GitHub timer has reached 0
def should_run_30min_task(github_url):
    try:
        response = requests.get(github_url, timeout=5)
        response.raise_for_status()
        data = response.json()

        start_time = datetime.fromisoformat(data['cycle_start'].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        elapsed = (now - start_time).total_seconds()
        remaining = 1800 - (elapsed % 1800)

        print(f"⏳ Time until next 30-min cycle: {int(remaining)} seconds")
        return remaining <= 1
    except Exception as e:
        print("⚠️ Failed to check 30-min timer:", e)
        return False
    
# Wait until GitHub timer reaches 0
def wait_until_next_cycle(github_url, duration):
    print(f"⏳ Waiting for next {duration//60}-minute cycle...")

    start_time = time.time()  # ⬅️ Start the timeout clock

    while not stop_macro_flag.is_set():
        try:
            response = requests.get(github_url, timeout=5)
            response.raise_for_status()
            data = response.json()

            start_time_str = data.get("cycle_start")
            if not start_time_str:
                raise ValueError("Missing 'cycle_start' in response.")

            start_time_obj = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            elapsed = (now - start_time_obj).total_seconds()
            remaining = duration - (elapsed % duration)

            print(f"⏳ Time until next cycle: {int(remaining)} seconds")

            if remaining <= 2:  # 🔁 increased from 1 to 2 seconds
                break

            # Check every 0.5s
            for _ in range(int(min(remaining, 5) * 2)):
                if stop_macro_flag.is_set():
                    return
                time.sleep(0.5)

        except Exception as e:
            print("⚠️ Error in wait_until_next_cycle:", e)
            time.sleep(2)

        # ⏲️ Add timeout check
        if time.time() - start_time > 360:
            print("⚠️ Timeout waiting for cycle. Forcing next step.")
            break

    print("✅ Timer reached. Proceeding to next cycle.")

# Safe Locate
def safe_locate(image_path, confidence=0.8):
    try:
        return pyautogui.locateOnScreen(image_path, confidence=confidence)
    except pyautogui.ImageNotFoundException:
        return None

# Saves configuration
def save_configuration():
    with open("configuration.txt", "w") as file:
        file.write("[Seeds]\n")
        for name, var in seeds_vars.items():
            file.write(f"{name}={var.get()}\n")

        file.write("\n[Gears]\n")
        for name, var in gears_vars.items():
            file.write(f"{name}={var.get()}\n")

        file.write("\n[Eggs]\n")
        for name, var in eggs_vars.items():
            file.write(f"{name}={var.get()}\n")

        #file.write("\n[EventShop]\n")
        #for name, var in event_shop_vars.items():
        #    file.write(f"{name}={var.get()}\n")

        file.write("\n[Settings]\n")
        file.write(f"Webhook={app.webhook_entry.get()}\n")
        file.write(f"UserID={app.userid_entry.get()}\n")
        file.write(f"PrivateServerURL={app.server_entry.get()}\n")
        file.write(f"DiscordPing={app.discord_ping.get()}\n")
        file.write(f"AutoAlign={app.auto_align.get()}\n")
        file.write(f"FastMode={app.fast_mode.get()}\n")
        file.write(f"MultiInstance={app.multi_instance.get()}\n")
        file.write(f"UINavigationKey={app.ui_nav_key.get()}\n")
        #file.write(f"SellPollinated={app.sell_pollinated_var.get()}\n")
        #file.write(f"PollinatedName={app.poll_entry.get()}\n")
        file.write("\n[SelectAll]\n")
        file.write(f"SelectAllSeeds={app.select_all_seed_var.get()}\n")
        file.write(f"SelectAllGears={app.select_all_gear_var.get()}\n")
        file.write(f"SelectAllEggs={app.select_all_egg_var.get()}\n")
        #file.write(f"SelectAllHoney={app.select_all_event_var.get()}\n")


    print("✅ Configuration saved to configuration.txt")

# Load configuration
def load_configuration(self):
    if not os.path.exists("configuration.txt"):
        return  # No saved config yet

    with open("configuration.txt", "r") as f:
        lines = f.readlines()

    config = {}
    for line in lines:
        if "=" in line:
            key, val = line.strip().split("=", 1)
            config[key.strip()] = val.strip()

    # Now set widget values
    self.webhook_entry.delete(0, tk.END)
    self.webhook_entry.insert(0, config.get("Webhook", ""))

    self.userid_entry.delete(0, tk.END)
    self.userid_entry.insert(0, config.get("UserID", ""))

    self.server_entry.delete(0, tk.END)
    self.server_entry.insert(0, config.get("PrivateServerURL", ""))

    self.ui_nav_key.delete(0, tk.END)
    self.ui_nav_key.insert(0, config.get("UINavigationKey", ""))

    #self.poll_entry.delete(0, tk.END)
    #self.poll_entry.insert(0, config.get("PollinatedName", ""))

    # Restore Settings checkbuttons
    self.discord_ping.set(int(config.get("DiscordPing", 0)))
    self.fast_mode.set(int(config.get("FastMode", 0)))
    self.auto_align.set(1 if config.get("AutoAlign", "0") in ["1", "True", "true"] else 0)
    #self.sell_pollinated_var.set(1 if config.get("SellPollinated", "0") in ["1", "True", "true"] else 0)

    # Restore Select All checkboxes
    self.select_all_seed_var.set(int(config.get("SelectAllSeeds", 0)))
    self.select_all_gear_var.set(int(config.get("SelectAllGears", 0)))
    self.select_all_egg_var.set(int(config.get("SelectAllEggs", 0)))
    #self.select_all_event_var.set(int(config.get("SelectAllHoney", 0)))

    print("✅ Configuration loaded")

    # Example: checkbox restore
    for name, var in seeds_vars.items():
        if name in config:
            var.set(int(config[name]))

    for name, var in gears_vars.items():
        if name in config:
            var.set(int(config[name]))

    for name, var in eggs_vars.items():
        if name in config:
            var.set(int(config[name]))

    for name, var in event_shop_vars.items():
        if name in config:
            var.set(int(config[name]))


def test_func():

    buy_eggs()

    #buy_seeds(NoStock_png)

    print("Executed")

def stop_macro_from_hotkey():
    print("Macro stopped via hotkey (F4)")
    stop_macro_flag.set()
    if hasattr(app, "status_label"):
        app.status_label.config(text="Status: STOPPED", fg="red")

def register_global_hotkeys():
    keyboard.add_hotkey("F4", stop_macro_from_hotkey)

global app

if __name__ == "__main__":
    app = MacroUI()

    # Start live seed timer update
    github_timer_url = "https://raw.githubusercontent.com/ankan-stack/Grow-A-Garden-Macro/main/seed_timer.json"

    register_global_hotkeys()
    app.mainloop()

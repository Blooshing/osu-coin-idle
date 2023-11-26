import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageTk
import math
import random
import json


class OsuCoinClicker:
    def __init__(self, root):
        self.load_user_data()
        # Check if a password is set; if not, prompt the user to set one

        self.root = root
        self.root.iconbitmap("osu!coins.ico")
        self.root.title("osu!coin Clicker")
        self.root.geometry("1000x800")
        self.root.resizable(False, False)  # Disable resizing of the window
        if not hasattr(self, 'username'):
            self.username = "Player"
        # Set dark mode color scheme
        self.root.configure(bg="#181818")  # Dark background color
        style = ttk.Style()
        style.theme_use("clam")  # Use the 'clam' theme for better styling
        style.configure("Dark.TFrame", background="#303030")
        style.configure("Dark.TPanedwindow", background="#303030")
        style.configure(
            "Dark.TLabel", foreground="#FFFFFF", background="#121212"
        )  # White text on dark background
        style.configure(
            "Dark.TButton", foreground="#FFFFFF", background="#303030"
        )  # White text on dark button

        # PanedWindow for sliding effect
        self.paned_window = ttk.PanedWindow(
            self.root, orient=tk.HORIZONTAL, style="Dark.TPanedwindow"
        )
        self.paned_window.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Initial resources
        self.osu_coins = 0
        self.click_multiplier = 1
        self.idle_rate = 1
        self.combo_multiplier = 1
        self.lucky_charm_multiplier = 1
        self.multiplier_boost_active = False
        self.special_events_enabled = True

        # Initial costs
        self.lucky_charm_multiplier_cost = 1000
        self.double_idle_cost = 5000
        self.special_events_cost = 10000
        self.time_warp_cost = 2000
        self.combo_multiplier_cost = 7000

        # Load sprite image
        self.sprite_image = ImageTk.PhotoImage(
            Image.open("sprite.png")
        )  # Replace "sprite.png" with your image file

        # Create GUI components for the game frame
        self.game_frame = ttk.Frame(self.paned_window, style="Dark.TFrame")
        self.paned_window.add(self.game_frame)
        self.paned_window.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.canvas = tk.Canvas(
            root, width=600, height=600, bg="#121212"
        )  # Dark canvas background
        self.canvas.grid(row=0, column=1, pady=10, padx=10, sticky="e")

        self.button = ttk.Button(
            root,
            text="Click to Earn osu!coin",
            command=self.click,
            style="Dark.TButton",
        )
        self.button.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        self.button = ttk.Button(
            root,
            text="Click to Earn osu!coin",
            command=self.click,
            style="Dark.TButton",
        )
        self.button.grid(row=0, column=2, pady=10, padx=10, sticky="nsew")

        self.label = ttk.Label(
            root,
            text=f"osu!coins: {self.osu_coins}",
            style="Dark.TLabel",
        )
        self.label.grid(row=4, column=2, pady=10, padx=10, sticky="e")

        # Upgrade buttons
        self.upgrade_click_button = ttk.Button(
            root,
            text=f"Upgrade Click Multiplier\nCost: {self.get_upgrade_cost(self.click_multiplier)}",
            command=self.upgrade_click_multiplier,
            style="Dark.TButton",
        )
        self.upgrade_click_button.grid(row=2, column=1, pady=10, padx=10, sticky="nsew")

        self.upgrade_idle_button = ttk.Button(
            root,
            text=f"Upgrade Idle Rate\nCost: {self.get_upgrade_cost(self.idle_rate)}",
            command=self.upgrade_idle_rate,
            style="Dark.TButton",
        )
        self.upgrade_idle_button.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

        self.upgrade_auto_clicker_button = ttk.Button(
            root,
            text=f"Upgrade Auto-Clicker\nCost: {self.get_upgrade_cost(self.combo_multiplier)}",
            command=self.upgrade_auto_clicker,
            style="Dark.TButton",
        )
        self.upgrade_auto_clicker_button.grid(
            row=2, column=0, pady=10, padx=10, sticky="nsew"
        )

        self.upgrade_critical_click_button = ttk.Button(
            root,
            text=f"Upgrade Critical Click\nCost: {self.get_upgrade_cost(self.lucky_charm_multiplier_cost)}",
            command=self.lucky_charm_multiplier,
            style="Dark.TButton",
        )
        self.upgrade_critical_click_button.grid(
            row=4, column=1, pady=10, padx=10, sticky="nsew"
        )

        self.upgrade_double_idle_button = ttk.Button(
            root,
            text=f"Upgrade Double Idle Rate\nCost: {self.get_upgrade_cost(self.idle_rate)}",
            command=self.upgrade_double_idle_rate,
            style="Dark.TButton",
        )
        self.upgrade_double_idle_button.grid(
            row=2, column=2, pady=10, padx=10, sticky="nsew"
        )

        self.upgrade_combo_button = ttk.Button(
            root,
            text=f"Upgrade Combo Multiplier\nCost: {self.get_upgrade_cost(self.combo_multiplier)}",
            command=self.upgrade_combo_multiplier,
            style="Dark.TButton",
        )
        self.upgrade_combo_button.grid(row=3, column=2, pady=10, padx=10, sticky="nsew")

        self.upgrade_time_warp_button = ttk.Button(
            root,
            text=f"Upgrade Time Warp\nCost: {self.get_upgrade_cost(1)}",
            command=self.upgrade_time_warp,
            style="Dark.TButton",
        )
        self.upgrade_time_warp_button.grid(
            row=3, column=0, pady=10, padx=10, sticky="nsew"
        )

        self.upgrade_special_events_button = ttk.Button(
            root,
            text=f"Upgrade Special Events\nCost: {self.get_upgrade_cost(1)}",
            command=self.upgrade_special_events,
            style="Dark.TButton",
        )
        self.upgrade_special_events_button.grid(
            row=4, column=0, pady=10, padx=10, sticky="nsew"
        )

        self.sprites = []  # List to store sprite IDs
        self.sprite_speed = 20  # Speed of sprite falling (adjust as needed)
        self.max_sprites = 25  # Maximum number of sprites allowed
        # Idle collection parameters
        self.idle_collection_interval = (
            1000  # Idle collection interval in milliseconds (adjust as needed)
        )
        self.root.after(
            self.idle_collection_interval, self.idle
        )  # Schedule the first idle collection

        # Configure row and column weights
        root.rowconfigure(0, weight=1)  # Allocate all vertical space to row 0
        root.columnconfigure(0, weight=1)  # Allocate all horizontal space to column 0
        self.game_frame.rowconfigure(
            1, weight=1
        )  # Allocate all vertical space to row 1 in game_frame
    
    def load_user_data(self):
        try:
            with open("game_state.json", "r") as file:
                data = json.load(file)
                self.osu_coins = data.get("osu_coins", 0)
                self.click_multiplier = data.get("click_multiplier", 1)
                self.idle_rate = data.get("idle_rate", 1)
                self.combo_multiplier = data.get("combo_multiplier", 1)
                self.lucky_charm_multiplier = data.get("lucky_charm_multiplier", 1)
                self.multiplier_boost_active = data.get(
                    "multiplier_boost_active", False
                )
                self.special_events_enabled = data.get("special_events_enabled", True)

        except FileNotFoundError:
            # Initialize default values if the file is not found
            self.osu_coins = 0
            self.click_multiplier = 1
            self.idle_rate = 1
            self.combo_multiplier = 1
            self.lucky_charm_multiplier = 1
            self.multiplier_boost_active = False
            self.special_events_enabled = True
            self.username = "Player"


    def save_user_data(self):
        data = {
            "username": self.username,
            "osu_coins": self.osu_coins,
            "click_multiplier": self.click_multiplier,
            "idle_rate": self.idle_rate,
            "combo_multiplier": self.combo_multiplier,
            "lucky_charm_multiplier": self.lucky_charm_multiplier,
            "multiplier_boost_active": self.multiplier_boost_active,
            "special_events_enabled": self.special_events_enabled,
        }
        with open("game_state.json", "w") as file:
            json.dump(data, file)

    def click(self, event=None):
        # Function to handle the click event
        click_amount = (
            self.click_multiplier * self.combo_multiplier * self.lucky_charm_multiplier
        )

        # Apply Time Warp bonus if active
        if self.multiplier_boost_active:
            click_amount *= 2  # Double the click amount during Time Warp

        self.osu_coins += click_amount
        self.update_label()
        self.check_special_events()

        # Spawn a sprite falling animation for each osu!coin added
        for _ in range(int(click_amount)):
            self.spawn_sprite()
        self.save_user_data()

    def spawn_sprite(self):
        if len(self.sprites) < self.max_sprites:
            sprite_x = random.randint(
                0, self.root.winfo_screenwidth() - 50
            )  # Random x-coordinate within the window
            sprite_y = -50  # Start sprite above the window
            sprite_id = self.canvas.create_image(
                sprite_x, sprite_y, anchor=tk.N, image=self.sprite_image
            )
            self.sprites.append(sprite_id)
            self.animate_sprite_fall(sprite_id)

    def animate_sprite_fall(self, sprite_id):
        coords = self.canvas.coords(sprite_id)
        if len(coords) == 2:
            x, y = coords
            width, height = 50, 50  # Set default width and height values
        else:
            x, y, width, height = coords

        delay = random.randint(0, 200)  # Random delay in milliseconds
        if y < self.root.winfo_screenheight() - height:
            self.root.after(
                delay, lambda: self.canvas.move(sprite_id, 0, self.sprite_speed)
            )
            self.root.after(delay + 20, lambda: self.animate_sprite_fall(sprite_id))
        else:
            self.canvas.delete(sprite_id)
            self.sprites.remove(sprite_id)

    def idle(self):
        # Function for automatic resource generation
        self.osu_coins += self.idle_rate * self.combo_multiplier
        self.update_label()
        for _ in range(int(self.osu_coins)):
            self.spawn_sprite()
        self.root.after(
            1000, self.idle
        )  # Schedule the idle function to run again after 1000ms
        self.save_user_data()

    def upgrade_click_multiplier(self):
        # Function to handle the upgrade click multiplier event
        if self.osu_coins >= self.get_upgrade_cost(self.click_multiplier):
            self.osu_coins -= self.get_upgrade_cost(self.click_multiplier)
            self.click_multiplier += 1
            self.update_label()

    def upgrade_idle_rate(self):
        # Function to handle the upgrade idle rate event
        if self.osu_coins >= self.get_upgrade_cost(self.idle_rate):
            self.osu_coins -= self.get_upgrade_cost(self.idle_rate)
            self.idle_rate += 1
            self.update_label()

    def upgrade_auto_clicker(self):
        # Function to handle the upgrade auto-clicker event
        if self.osu_coins >= self.get_upgrade_cost(self.combo_multiplier):
            self.osu_coins -= self.get_upgrade_cost(self.combo_multiplier)
            self.combo_multiplier += 1
            self.update_label()

    def upgrade_lucky_charm_multiplier(self):
        self.update_label()
        if self.osu_coins >= self.critical_click_cost:
            self.osu_coins -= self.critical_click_cost
            self.critical_click_cost = self.get_upgrade_cost(self.critical_click_cost)
            self.lucky_charm_multiplier += 1
            self.update_label()

    def upgrade_double_idle_rate(self):
        # Function to handle the upgrade double idle rate event
        if self.osu_coins >= self.get_upgrade_cost(self.idle_rate):
            self.osu_coins -= self.get_upgrade_cost(self.idle_rate)
            self.idle_rate *= 2
            self.update_label()

    def upgrade_combo_multiplier(self):
        # Function to handle the upgrade combo multiplier event
        if self.osu_coins >= self.get_upgrade_cost(self.combo_multiplier):
            self.osu_coins -= self.get_upgrade_cost(self.combo_multiplier)
            self.combo_multiplier += 1
            self.update_label()

    def upgrade_time_warp(self):
        # Function to handle the upgrade time warp event
        if self.osu_coins >= self.get_upgrade_cost(1):
            self.osu_coins -= self.get_upgrade_cost(1)
            self.multiplier_boost_active = True
            self.root.after(
                3000, self.deactivate_multiplier_boost
            )  # Deactivate after 10 seconds
            self.update_label()

    def upgrade_special_events(self):
        # Function to handle the upgrade special events event
        if self.osu_coins >= self.get_upgrade_cost(1):
            self.osu_coins -= self.get_upgrade_cost(1)
            self.special_events_enabled = not self.special_events_enabled
            self.update_label()

    def check_special_events(self):
        # Function to check and apply special events
        if (
            self.special_events_enabled and random.random() < 0.01
        ):  # 1% chance of a special event
            self.osu_coins += random.randint(
                10, 100
            )  # Bonus osu!coins for a special event
            self.update_label()

    def deactivate_multiplier_boost(self):
        # Function to deactivate the multiplier boost
        self.multiplier_boost_active = False
        self.update_label()

    def get_upgrade_cost(self, level):
        # Exponential growth formula for cost
        return int(10 * (1.5**level))

    def update_label(self):

        # Function to update the label with the current osu!coins and upgrades
        self.label.config(
            text=f"Username: {self.username}\n"
            f"osu!coins: {self.osu_coins}\n"
            f"Click Multiplier: {self.click_multiplier}\n"
            f"Idle Rate: {self.idle_rate}\n"
            f"Auto-Clicker: {self.combo_multiplier}\n"
            f"Critical Click: {self.lucky_charm_multiplier}\n"
            f"Double Idle Rate: {self.idle_rate}\n"
            f"Combo Multiplier: {self.combo_multiplier}\n"
            f"Time Warp Active: {self.multiplier_boost_active}\n"
            f"Special Events Enabled: {self.special_events_enabled}"
        )
        self.upgrade_click_button.config(
            text=f"Upgrade Click Multiplier\nCost: {self.get_upgrade_cost(self.click_multiplier)}"
        )
        self.upgrade_idle_button.config(
            text=f"Upgrade Idle Rate\nCost: {self.get_upgrade_cost(self.idle_rate)}"
        )
        self.upgrade_auto_clicker_button.config(
            text=f"Upgrade Auto-Clicker\nCost: {self.get_upgrade_cost(self.combo_multiplier)}"
        )
        self.upgrade_critical_click_button.config(
            text=f"Upgrade Critical Click\nCost: {self.get_upgrade_cost(self.lucky_charm_multiplier)}"
        )
        self.upgrade_double_idle_button.config(
            text=f"Upgrade Double Idle Rate\nCost: {self.get_upgrade_cost(self.idle_rate)}"
        )
        self.upgrade_combo_button.config(
            text=f"Upgrade Combo Multiplier\nCost: {self.get_upgrade_cost(self.combo_multiplier)}"
        )
        self.upgrade_time_warp_button.config(
            text=f"Upgrade Time Warp\nCost: {self.get_upgrade_cost(1)}"
        )
        self.upgrade_special_events_button.config(
            text=f"Upgrade Special Events\nCost: {self.get_upgrade_cost(1)}"
        )
        self.label.config(relief=tk.RAISED, borderwidth=2)

    def change_username(self):
        new_username = simpledialog.askstring("Change Username", "Enter your new username:")
        if new_username:
            self.username = new_username
            self.save_user_data()
            self.update_label()


if __name__ == "__main__":
    root = tk.Tk()
    app = OsuCoinClicker(root)
    change_username_button = ttk.Button(
        root, text="Change Username", command=app.change_username, style="Dark.TButton"
    )
    change_username_button.grid(row=5, column=2, pady=10, padx=10, sticky="e")
    root.mainloop()

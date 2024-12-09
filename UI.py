import tkinter as tk
from tkinter import messagebox

class RPGGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI RPG Game")
        self.root.geometry("800x600")

        # Game Display Area
        self.game_display = tk.Canvas(root, width=600, height=400, bg="black")
        self.game_display.pack(side=tk.TOP, pady=10)

        # Character Info Panel
        self.character_info = tk.Frame(root, width=800, height=100, bg="gray")
        self.character_info.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.health_label = tk.Label(self.character_info, text="Health: 100", bg="gray", fg="white", font=("Arial", 14))
        self.health_label.pack(side=tk.LEFT, padx=10)

        self.inventory_label = tk.Label(self.character_info, text="Inventory: [Sword, Potion]", bg="gray", fg="white", font=("Arial", 14))
        self.inventory_label.pack(side=tk.LEFT, padx=10)

        # Action Buttons
        self.action_buttons = tk.Frame(root, width=800, height=100, bg="lightgray")
        self.action_buttons.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.attack_button = tk.Button(self.action_buttons, text="Attack", command=self.attack, font=("Arial", 14))
        self.attack_button.pack(side=tk.LEFT, padx=10)

        self.defend_button = tk.Button(self.action_buttons, text="Defend", command=self.defend, font=("Arial", 14))
        self.defend_button.pack(side=tk.LEFT, padx=10)

        self.use_item_button = tk.Button(self.action_buttons, text="Use Item", command=self.use_item, font=("Arial", 14))
        self.use_item_button.pack(side=tk.LEFT, padx=10)

    def attack(self):
        messagebox.showinfo("Action", "You chose to attack!")

    def defend(self):
        messagebox.showinfo("Action", "You chose to defend!")

    def use_item(self):
        messagebox.showinfo("Action", "You used an item!")

# Create the main window
root = tk.Tk()
app = RPGGameUI(root)
root.mainloop()

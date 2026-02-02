import customtkinter as ctk
import threading
import time
import webbrowser
from datetime import datetime
from PIL import Image
import os

from scraper import check_stock_browser, check_stock_api, fetch_product_metadata
from utils import play_alert_sound

# --- Theme Configuration ---
COLOR_BG = "#F5F5F7"
COLOR_CARD_BG = "#FFFFFF"
COLOR_TEXT_PRIMARY = "#1D1D1F"
COLOR_TEXT_SECONDARY = "#86868B"
COLOR_ACCENT = "#0071E3"
COLOR_SUCCESS = "#34C759"
COLOR_DANGER = "#FF3B30"
COLOR_WARNING = "#FF9500"

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class StatusPill(ctk.CTkFrame):
    def __init__(self, master, text="Ready", color=COLOR_TEXT_SECONDARY):
        super().__init__(master, fg_color=color, corner_radius=20, height=24)
        self.label = ctk.CTkLabel(self, text=text, font=("Segoe UI", 11, "bold"), text_color="white")
        self.label.pack(padx=10, pady=2)
    
    def set_status(self, text, bg_color):
        self.label.configure(text=text)
        self.configure(fg_color=bg_color)

class ProductCard(ctk.CTkFrame):
    def __init__(self, master, delete_callback):
        super().__init__(master, fg_color=COLOR_CARD_BG, corner_radius=15, border_width=0)
        self.delete_callback = delete_callback
        
        self.grid_columnconfigure(1, weight=1)
        
        # Icon
        self.icon_frame = ctk.CTkFrame(self, width=40, height=40, corner_radius=10, fg_color=COLOR_BG)
        self.icon_frame.grid(row=0, column=0, rowspan=2, padx=(15, 10), pady=15)
        self.icon_label = ctk.CTkLabel(self.icon_frame, text="🛍️", font=("Segoe UI", 20))
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Inputs
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Paste Zara Link Here...", border_width=0, fg_color=COLOR_BG, text_color=COLOR_TEXT_PRIMARY, height=30, font=("Segoe UI", 13))
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=(15, 2))
        
        self.size_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.size_frame.grid(row=1, column=1, sticky="w", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(self.size_frame, text="Size:", font=("Segoe UI", 12), text_color=COLOR_TEXT_SECONDARY).pack(side="left")
        self.size_entry = ctk.CTkEntry(self.size_frame, width=60, placeholder_text="Any", border_width=0, fg_color=COLOR_BG, font=("Segoe UI", 12))
        self.size_entry.pack(side="left", padx=5)

        # Status & Delete
        self.status_pill = StatusPill(self, text="Idle", color=COLOR_TEXT_SECONDARY)
        self.status_pill.grid(row=0, column=2, padx=15, pady=(15, 0), sticky="e")
        
        self.del_btn = ctk.CTkButton(self, text="✕", width=30, height=30, fg_color="#F2F2F7", text_color="gray", hover_color=COLOR_DANGER, corner_radius=15, font=("Segoe UI", 14, "bold"), command=lambda: delete_callback(self))
        self.del_btn.grid(row=1, column=2, padx=15, pady=10, sticky="e")
        
        # Metadata Cache
        self.meta_product_id = None
        self.meta_sku = None
        self.meta_fetched = False
        self.size_map = {}

    def get_data(self):
        return {
            "url": self.url_entry.get().strip(),
            "size": self.size_entry.get().strip()
        }

    def set_active(self, active):
        state = "disabled" if active else "normal"
        self.url_entry.configure(state=state)
        self.size_entry.configure(state=state)
        self.del_btn.configure(state=state)
    
    # Thread-safe update
    def safe_set_status(self, text, bg_color):
        self.after(0, lambda: self.status_pill.set_status(text, bg_color))

class ZaraStockCheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("StockMonitor V4.1 (Safe)")
        self.geometry("900x800")
        self.configure(fg_color=COLOR_BG)

        self.monitoring = False
        self.monitor_thread = None
        self.rows = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        ctk.CTkLabel(self.header_frame, text="Zara Stock Monitor", font=("Segoe UI", 24, "bold"), text_color=COLOR_TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(self.header_frame, text="Real-time availability checker", font=("Segoe UI", 14), text_color=COLOR_TEXT_SECONDARY).pack(side="left", padx=10, pady=(8, 0))

        # List
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        
        # Log Panel
        self.log_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, height=150, corner_radius=10)
        self.log_text = ctk.CTkTextbox(self.log_frame, font=("Consolas", 11), text_color=COLOR_TEXT_PRIMARY, fg_color="transparent")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Controls
        self.bottom_bar = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, height=120, corner_radius=0)
        self.bottom_bar.grid(row=2, column=0, sticky="ew", ipadx=20, ipady=10)
        
        self.add_btn = ctk.CTkButton(self.bottom_bar, text="+ Add Product", fg_color=COLOR_BG, text_color=COLOR_ACCENT, font=("Segoe UI", 13, "bold"), hover_color="#E5E5EA", corner_radius=20, command=self.add_product_row)
        self.add_btn.pack(side="left", padx=20, pady=15)

        self.settings_frame = ctk.CTkFrame(self.bottom_bar, fg_color="transparent")
        self.settings_frame.pack(side="left", padx=20)

        ctk.CTkLabel(self.settings_frame, text="Mode:", text_color=COLOR_TEXT_SECONDARY, font=("Segoe UI", 12)).pack(side="left", padx=(0,5))
        self.mode_var = ctk.StringVar(value="Browser")
        self.mode_switch = ctk.CTkSegmentedButton(self.settings_frame, values=["Browser", "API"], variable=self.mode_var, font=("Segoe UI", 12, "bold"))
        self.mode_switch.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(self.settings_frame, text="Log:", text_color=COLOR_TEXT_SECONDARY, font=("Segoe UI", 12)).pack(side="left", padx=(0,5))
        self.log_switch = ctk.CTkSwitch(self.settings_frame, text="Show", font=("Segoe UI", 12), command=self.toggle_log)
        self.log_switch.pack(side="left", padx=(0, 20))

        self.timeout_entry = ctk.CTkEntry(self.settings_frame, width=40, bg_color="transparent", border_width=0, font=("Segoe UI", 12, "bold"), fg_color=COLOR_BG)
        self.timeout_entry.insert(0, "5")
        self.timeout_entry.pack(side="left")
        ctk.CTkLabel(self.settings_frame, text="min", text_color=COLOR_TEXT_SECONDARY, font=("Segoe UI", 12)).pack(side="left", padx=5)

        self.action_btn = ctk.CTkButton(self.bottom_bar, text="Start Monitoring", fg_color=COLOR_ACCENT, hover_color="#0062CC", font=("Segoe UI", 15, "bold"), corner_radius=25, width=160, height=45, command=self.toggle_monitoring)
        self.action_btn.pack(side="right", padx=20, pady=15)
        
        self.status_bar = ctk.CTkLabel(self, text="Ready", font=("Segoe UI", 11), text_color=COLOR_TEXT_SECONDARY)
        self.status_bar.grid(row=3, column=0, pady=(0, 5))

        self.add_product_row()

    def safe_log(self, msg):
        self.after(0, lambda: self.log_msg(msg))

    def safe_status(self, text):
        self.after(0, lambda: self.status_bar.configure(text=text))

    def toggle_log(self):
        if self.log_switch.get():
            self.log_frame.place(relx=0.03, rely=0.65, relwidth=0.94, relheight=0.20)
            self.scroll_frame.grid(row=1, column=0, sticky="nsw", padx=20, pady=(0, 160))
        else:
            self.log_frame.place_forget()
            self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20)

    def log_msg(self, msg):
        if self.log_switch.get():
            ts = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert("end", f"[{ts}] {msg}\n")
            self.log_text.see("end")

    def add_product_row(self):
        card = ProductCard(self.scroll_frame, self.remove_product_row)
        card.pack(fill="x", pady=8, padx=10)
        self.rows.append(card)

    def remove_product_row(self, card):
        card.pack_forget()
        self.rows.remove(card)
        card.destroy()

    def toggle_monitoring(self):
        if not self.monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        active_items = []
        for card in self.rows:
            data = card.get_data()
            if data["url"]:
                active_items.append({"card": card, "url": data["url"], "size": data["size"]})
        
        if not active_items:
            self.status_bar.configure(text="Please enter at least one URL.")
            return

        mode = self.mode_var.get()
        use_api = (mode == "API")

        self.monitoring = True
        self.action_btn.configure(text="Stop Monitoring", fg_color=COLOR_DANGER)
        self.add_btn.configure(state="disabled")
        self.timeout_entry.configure(state="disabled")
        self.mode_switch.configure(state="disabled")
        
        for card in self.rows: card.set_active(True)
            
        self.status_bar.configure(text=f"Initializing {mode} mode...")
        self.log_msg(f"Starting {mode} mode...")
        
        self.monitor_thread = threading.Thread(target=self.monitor_loop, args=(active_items, float(self.timeout_entry.get()), use_api))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        self.status_bar.configure(text="Stopping...")
        self.log_msg("Stopping monitoring...")
        self.action_btn.configure(text="Start Monitoring", fg_color=COLOR_ACCENT)
        self.add_btn.configure(state="normal")
        self.timeout_entry.configure(state="normal")
        self.mode_switch.configure(state="normal")
        for card in self.rows: card.set_active(False)

    def monitor_loop(self, items, interval_minutes, use_api):
        # Phase 1: Metadata
        if use_api:
            for item in items:
                if not self.monitoring: return
                card = item["card"]
                if not card.meta_fetched:
                    card.safe_set_status("Initializing...", COLOR_WARNING)
                    self.safe_log(f"Fetching metadata for {item['url']}...")
                    
                    # Blocking call, fine here
                    meta = fetch_product_metadata(item["url"])
                    
                    if meta:
                        card.meta_product_id = meta["product_id"]
                        card.size_map = meta["size_map"]
                        card.meta_fetched = True
                        card.safe_set_status("Meta OK", COLOR_SUCCESS) # Temporary
                        
                        target_size = item["size"].upper()
                        if target_size and target_size in card.size_map:
                            card.meta_sku = card.size_map[target_size]
                    else:
                        card.safe_set_status("Init Failed", COLOR_DANGER)
                        self.safe_log("Failed to fetch size metadata.")

        # Phase 2: Loop
        while self.monitoring:
            for item in items:
                if not self.monitoring: break
                card = item["card"]
                url = item["url"]
                size = item["size"]
                
                card.safe_set_status("Checking...", COLOR_WARNING)
                
                if use_api:
                    if card.meta_fetched and card.meta_product_id:
                        in_stock, msg, details = check_stock_api(card.meta_product_id, card.meta_sku, card.size_map)
                        self.safe_log(f"API Check: {details}")
                    else:
                        in_stock, msg = False, "Meta Missing"
                else:
                    in_stock, msg, screenshot = check_stock_browser(url, size)
                    self.safe_log(f"Browser Check: {msg}")
                
                if in_stock:
                    card.safe_set_status(msg, COLOR_SUCCESS)
                    play_alert_sound()
                else:
                    # Show specific error or status if not just "Out of Stock"
                    color = COLOR_TEXT_SECONDARY if msg == "Out of Stock" else COLOR_DANGER
                    # Truncate long error messages for the pill
                    pill_text = msg if len(msg) < 15 else "Error"
                    card.safe_set_status(pill_text, color)
            
            sleep_s = int(interval_minutes * 60)
            for i in range(sleep_s):
                if not self.monitoring: break
                
                # Update status bar safely
                if i % 5 == 0:
                   self.safe_status(f"Next check in {sleep_s - i}s")
                time.sleep(1)

if __name__ == "__main__":
    app = ZaraStockCheckerApp()
    app.mainloop()

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import ctypes
from config import *
from translator import POTask
import sys

import sys
import os

def resource_path(relative_path):
    """ Отримує шлях до ресурсів всередині EXE """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# У конструкторі класу TranslatorApp використовуй так:
icon_path = resource_path(os.path.join("media", "icon.ico"))



try:
    myappid = 'zefso.linguist_ai.translator.v1' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.stop_event = threading.Event()
        
        # Початкова тема
        self.current_theme = "dark"
        ctk.set_appearance_mode(self.current_theme)

        # Завантаження іконки вікна
        icon_path = os.path.join("media", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except:
                pass

        self.setup_ui()

    def setup_ui(self):
        # --- ВЕРХНЯ ПАНЕЛЬ ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(side="top", fill="x", padx=10, pady=5)
        
        # Кнопка-перемикач (тепер з текстом для стабільності)
        self.theme_btn = ctk.CTkButton(
            self.top_bar, 
            text="NIGHT", # Початковий текст
            width=70, 
            height=30,
            fg_color=("gray75", "gray25"), # Світла кнопка вдень, темна вночі
            text_color=("black", "white"),
            hover_color=("gray70", "gray30"),
            font=("Segoe UI", 11, "bold"),
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="right", padx=10)

        # Header
        self.header = ctk.CTkLabel(self, text=APP_NAME, font=("Segoe UI", 28, "bold"), text_color="#3B8ED0")
        self.header.pack(pady=(0, 5))
        # File Area
        self.f_frame = ctk.CTkFrame(self)
        self.f_frame.pack(padx=20, pady=10, fill="x")
        self.path_entry = ctk.CTkEntry(self.f_frame, placeholder_text="Path to .po file...")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        self.btn_browse = ctk.CTkButton(self.f_frame, text="Browse", width=100)
        self.btn_browse.pack(side="right", padx=10)
        self.btn_browse.bind("<ButtonRelease-1>", lambda e: self.browse())

        # Settings Frame
        self.s_frame = ctk.CTkFrame(self)
        self.s_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(self.s_frame, text="Target Language:").pack(side="left", padx=10)
        self.lang_var = ctk.StringVar(value="English")
        self.lang_menu = ctk.CTkOptionMenu(self.s_frame, values=list(LANGUAGES.keys()), variable=self.lang_var)
        self.lang_menu.pack(side="left", padx=10)

        # Smart Switch
        self.smart_var = ctk.BooleanVar(value=True)
        self.smart_sw = ctk.CTkSwitch(self.s_frame, text="Smart Update", variable=self.smart_var)
        self.smart_sw.pack(side="right", padx=20)
        self.smart_sw.bind("<Enter>", self.show_smart_tip)
        self.smart_sw.bind("<Leave>", self.hide_smart_tip)

        # Progress
        self.prog = ctk.CTkProgressBar(self)
        self.prog.pack(padx=20, pady=20, fill="x")
        self.prog.set(0)

        # Status & Logs Header
        self.log_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.log_header_frame.pack(padx=20, fill="x")
        
        self.status_label = ctk.CTkLabel(self.log_header_frame, text="Ready", font=("Segoe UI", 12, "italic"), text_color="gray")
        self.status_label.pack(side="left")
        
        self.btn_clear = ctk.CTkButton(self.log_header_frame, text="Clear Logs", width=80, height=20, fg_color="gray30")
        self.btn_clear.pack(side="right")
        self.btn_clear.bind("<ButtonRelease-1>", lambda e: self.clear_logs())

        # Logs Textbox
        self.logs = ctk.CTkTextbox(self, height=250, font=("Consolas", 12), wrap="word")
        self.logs.pack(padx=20, pady=(5, 10), fill="both", expand=True)

        # Control Buttons
        self.b_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.b_frame.pack(pady=20)
        self.btn_start = ctk.CTkButton(self.b_frame, text="START", fg_color="#2ecc71", width=140)
        self.btn_start.pack(side="left", padx=10)
        self.btn_start.bind("<ButtonRelease-1>", lambda e: self.start())
        
        self.btn_stop = ctk.CTkButton(self.b_frame, text="STOP", fg_color="#e74c3c", width=140)
        self.btn_stop.pack(side="left", padx=10)
        self.btn_stop.bind("<ButtonRelease-1>", lambda e: self.stop())

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.theme_btn.configure(text="Dark")
            self.log("🎨 Switched to Light Mode")
        else:
            self.current_theme = "dark"
            self.theme_btn.configure(text="Light")
            self.log("🎨 Switched to Dark Mode")
        
        ctk.set_appearance_mode(self.current_theme)

    def show_smart_tip(self, event):
        self.status_label.configure(
            text="💡 Smart Update: Skips correct translations, updates only empty or wrong language strings.",
            text_color="#3B8ED0"
        )

    def hide_smart_tip(self, event):
        self.status_label.configure(text="Ready", text_color="gray")

    def clear_logs(self): self.logs.delete("1.0", "end")

    def log(self, text):
        self.logs.insert("end", f"{text}\n")
        self.logs.see("end")

    def browse(self):
        p = filedialog.askopenfilename(filetypes=[("PO files", "*.po")])
        if p:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, p)
            self.log(f"📁 Selected: {os.path.basename(p)}")

    def stop(self):
        if not self.stop_event.is_set() and self.btn_start.cget("state") == "disabled":
            self.stop_event.set()
            self.btn_stop.configure(state="disabled", text="Stopping...")

    def start(self):
        if self.btn_start.cget("state") == "disabled": return
        file = self.path_entry.get()
        if not file or not os.path.exists(file): return messagebox.showwarning("Error", "File not found!")
        self.clear_logs()
        self.stop_event.clear()
        self.btn_start.configure(state="disabled", text="Running...")
        task = POTask(file, LANGUAGES[self.lang_var.get()], self.log, self.prog.set, self.stop_event)
        threading.Thread(target=lambda: self.run_task(task), daemon=True).start()

    def run_task(self, task):
        task.run(smart_mode=self.smart_var.get())
        self.btn_start.configure(state="normal", text="START")
        self.btn_stop.configure(state="normal", text="STOP")
        self.prog.set(0)
        messagebox.showinfo(APP_NAME, "Finished!")
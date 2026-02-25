import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from config import *
from translator import POTask

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.stop_event = threading.Event()
        
        # Установка темы
        ctk.set_appearance_mode("dark") 
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        self.header = ctk.CTkLabel(self, text=APP_NAME, font=("Segoe UI", 28, "bold"), text_color="#3B8ED0")
        self.header.pack(pady=(20, 5))
        
        # File Area
        self.f_frame = ctk.CTkFrame(self)
        self.f_frame.pack(padx=20, pady=10, fill="x")
        self.path_entry = ctk.CTkEntry(self.f_frame, placeholder_text="Path to .po file...")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # Кнопка Browse срабатывает при отпускании (ButtonRelease)
        self.btn_browse = ctk.CTkButton(self.f_frame, text="Browse", width=100)
        self.btn_browse.pack(side="right", padx=10)
        self.btn_browse.bind("<ButtonRelease-1>", lambda e: self.browse())

        # Settings
        self.s_frame = ctk.CTkFrame(self)
        self.s_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(self.s_frame, text="Target Language:").pack(side="left", padx=10)
        self.lang_var = ctk.StringVar(value="English")
        self.lang_menu = ctk.CTkOptionMenu(self.s_frame, values=list(LANGUAGES.keys()), variable=self.lang_var)
        self.lang_menu.pack(side="left", padx=10)

        self.smart_var = ctk.BooleanVar(value=True)
        self.smart_sw = ctk.CTkSwitch(self.s_frame, text="Smart Update", variable=self.smart_var)
        self.smart_sw.pack(side="right", padx=10)

        # Progress
        self.prog = ctk.CTkProgressBar(self)
        self.prog.pack(padx=20, pady=20, fill="x")
        self.prog.set(0)

        # Logs Label and Clear Button
        self.log_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.log_header_frame.pack(padx=20, fill="x")
        ctk.CTkLabel(self.log_header_frame, text="Translation Activity:", font=("Segoe UI", 12, "italic")).pack(side="left")
        
        self.btn_clear = ctk.CTkButton(self.log_header_frame, text="Clear Logs", width=80, height=20, fg_color="gray30")
        self.btn_clear.pack(side="right")
        self.btn_clear.bind("<ButtonRelease-1>", lambda e: self.clear_logs())

        # Logs Textbox
        self.logs = ctk.CTkTextbox(self, height=250, font=("Consolas", 12))
        self.logs.pack(padx=20, pady=(5, 10), fill="both", expand=True)

        # Control Buttons
        self.b_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.b_frame.pack(pady=20)
        
        self.btn_start = ctk.CTkButton(self.b_frame, text="START", fg_color="#2ecc71", hover_color="#27ae60", width=140)
        self.btn_start.pack(side="left", padx=10)
        self.btn_start.bind("<ButtonRelease-1>", lambda e: self.start())
        
        self.btn_stop = ctk.CTkButton(self.b_frame, text="STOP", fg_color="#e74c3c", hover_color="#c0392b", width=140)
        self.btn_stop.pack(side="left", padx=10)
        self.btn_stop.bind("<ButtonRelease-1>", lambda e: self.stop())

    def clear_logs(self):
        self.logs.delete("1.0", "end")

    def browse(self):
        p = filedialog.askopenfilename(filetypes=[("PO files", "*.po")])
        if p:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, p)
            self.log(f"📁 Selected file: {os.path.basename(p)}")

    def log(self, text):
        self.logs.insert("end", f"{text}\n")
        self.logs.see("end")

    def stop(self):
        if not self.stop_event.is_set() and self.btn_start.cget("state") == "disabled":
            self.stop_event.set()
            self.btn_stop.configure(state="disabled", text="Stopping...")
            self.log("\n⚠️ Stop signal sent. Please wait for the current line to finish...")

    def start(self):
        if self.btn_start.cget("state") == "disabled":
            return
        
        file = self.path_entry.get()
        if not file or not os.path.exists(file):
            return messagebox.showwarning("Error", "Valid .po file required!")
        
        # Подготовка интерфейса
        self.clear_logs()
        self.log(f"🚀 Initializing {APP_NAME}...")
        self.stop_event.clear()
        self.btn_start.configure(state="disabled", text="Running...")
        self.btn_stop.configure(state="normal", text="STOP")
        
        target_code = LANGUAGES[self.lang_var.get()]
        
        # Создаем задачу и запускаем в отдельном потоке
        task = POTask(file, target_code, self.log, self.prog.set, self.stop_event)
        threading.Thread(target=lambda: self.run_task(task), daemon=True).start()

    def run_task(self, task):
        # Передаем режим Smart Update из чекбокса
        task.run(smart_mode=self.smart_var.get())
        
        # Возвращаем интерфейс в норму
        self.btn_start.configure(state="normal", text="START")
        self.btn_stop.configure(state="normal", text="STOP")
        self.prog.set(0) # Сброс прогресс-бара
        messagebox.showinfo(APP_NAME, "Translation process finished!")
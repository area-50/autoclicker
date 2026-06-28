import threading
import time
import customtkinter as ctk
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key

class AutoClicker:
    def __init__(self, delay=0.1, button=Button.left, max_clicks=0):
        self.delay = delay
        self.button = button
        self.max_clicks = max_clicks
        self.current_clicks = 0
        self.running = False
        self.program_running = True
        self.mouse = Controller()
        self.on_stop_callback = None

    def start_clicking(self):
        self.current_clicks = 0
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        while self.program_running:
            while self.running:
                if self.max_clicks > 0 and self.current_clicks >= self.max_clicks:
                    self.running = False
                    if self.on_stop_callback:
                        self.on_stop_callback()
                    break
                
                self.mouse.click(self.button)
                self.current_clicks += 1
                time.sleep(self.delay)
            time.sleep(0.01)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurações da Janela
        self.title("bigodeautoclicker - Brainstorm Tecnologia")
        self.geometry("450x420")
        self.configure(fg_color="#0b132b") # Fundo azul escuro
        
        # Aparência do App
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Backend do Clicker
        self.clicker = AutoClicker()
        self.clicker.on_stop_callback = self.handle_auto_stop
        
        # Thread para o clicker rodar em segundo plano
        self.click_thread = threading.Thread(target=self.clicker.run, daemon=True)
        self.click_thread.start()
        
        # Listener para a tecla de atalho (F8)
        self.toggle_key = Key.f8
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

        # Interface de Usuário
        self.title_label = ctk.CTkLabel(self, text="bigodeautoclicker", font=ctk.CTkFont(size=28, weight="bold"), text_color="#00e5ff")
        self.title_label.pack(pady=(25, 2))
        
        self.subtitle_label = ctk.CTkLabel(self, text="by Brainstorm Tecnologia", font=ctk.CTkFont(size=12, slant="italic"), text_color="#7a8eb1")
        self.subtitle_label.pack(pady=(0, 15))
        
        # Frame de Controles
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.pack(pady=10, padx=30, fill="x")
        self.control_frame.grid_columnconfigure(1, weight=1)

        # 1. Botão do Mouse
        self.btn_label = ctk.CTkLabel(self.control_frame, text="Botão do Mouse:", text_color="#e0e0e0", font=ctk.CTkFont(size=14))
        self.btn_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
        self.btn_combo = ctk.CTkComboBox(self.control_frame, values=["Esquerdo", "Direito", "Meio"], command=self.update_button,
                                         border_color="#00e5ff", button_color="#00e5ff", 
                                         dropdown_fg_color="#0b132b", dropdown_text_color="#00e5ff")
        self.btn_combo.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

        # 2. Tempo de Clique (Input)
        self.time_label = ctk.CTkLabel(self.control_frame, text="Tempo (segundos):", text_color="#e0e0e0", font=ctk.CTkFont(size=14))
        self.time_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")
        
        self.time_entry = ctk.CTkEntry(self.control_frame, border_color="#00e5ff", text_color="#00e5ff")
        self.time_entry.insert(0, "0.1")
        self.time_entry.grid(row=1, column=1, pady=10, padx=10, sticky="ew")
        self.time_entry.bind("<KeyRelease>", self.update_delay)

        # 3. Quantidade de Cliques
        self.clicks_label = ctk.CTkLabel(self.control_frame, text="Qtd. Cliques (0=Livre):", text_color="#e0e0e0", font=ctk.CTkFont(size=14))
        self.clicks_label.grid(row=2, column=0, pady=10, padx=10, sticky="w")
        
        self.clicks_entry = ctk.CTkEntry(self.control_frame, border_color="#00e5ff", text_color="#00e5ff")
        self.clicks_entry.insert(0, "0")
        self.clicks_entry.grid(row=2, column=1, pady=10, padx=10, sticky="ew")
        self.clicks_entry.bind("<KeyRelease>", self.update_max_clicks)

        # Informação de Status
        self.status_label = ctk.CTkLabel(self, text="Status: Parado (Pressione F8 para iniciar)", text_color="#7a8eb1", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(pady=15)

        # Lidar com o fechamento da janela
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_button(self, choice):
        if choice == "Esquerdo":
            self.clicker.button = Button.left
        elif choice == "Direito":
            self.clicker.button = Button.right
        elif choice == "Meio":
            self.clicker.button = Button.middle

    def update_delay(self, event=None):
        try:
            val = float(self.time_entry.get().replace(',', '.'))
            if val >= 0:
                self.clicker.delay = val
        except ValueError:
            pass

    def update_max_clicks(self, event=None):
        try:
            val = int(self.clicks_entry.get())
            if val >= 0:
                self.clicker.max_clicks = val
        except ValueError:
            pass

    def handle_auto_stop(self):
        # Chamado pela thread quando atinge o limite de cliques
        self.after(0, self.update_status, False)

    def on_press(self, key):
        if key == self.toggle_key:
            if self.clicker.running:
                self.clicker.stop_clicking()
                self.after(0, self.update_status, False)
            else:
                # Atualiza os valores antes de iniciar só para garantir
                self.update_delay()
                self.update_max_clicks()
                self.clicker.start_clicking()
                self.after(0, self.update_status, True)

    def update_status(self, is_running):
        if is_running:
            self.status_label.configure(text="Status: Ativo (Pressione F8 para parar)", text_color="#00e5ff")
        else:
            self.status_label.configure(text="Status: Parado (Pressione F8 para iniciar)", text_color="#7a8eb1")

    def on_closing(self):
        self.clicker.exit()
        self.listener.stop()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()

import tkinter as tk
from core.policy_loader import load_policies
from ui.main_window import MainWindow

if __name__ == "__main__":
    # Загрузка конфигурации
    config = load_policies("config.yml")
    
    # Инициализация интерфейса
    root = tk.Tk()
    app = MainWindow(root, config)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox

class SimplePolicyEditor(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Новая простая политика")
        self.result = None
        self._setup_ui()
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Шапка политики
        ttk.Label(main_frame, text="Display Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=2)
        
        ttk.Label(main_frame, text="Ключ (окончание):").grid(row=1, column=0, sticky="w", pady=2)
        self.key_suffix = ttk.Entry(main_frame, width=40)
        self.key_suffix.insert(0, "Control")  # Значение по умолчанию
        self.key_suffix.grid(row=1, column=1, sticky="ew", pady=2)
        
        ttk.Label(main_frame, text="Категория:").grid(row=2, column=0, sticky="w", pady=2)
        self.category_combo = ttk.Combobox(main_frame, values=[
            "ALT_System", "ALT_Security", "ALT_Services",
            "ALT_SSHD", "ALT_Systemd", "ALT_Network",
            "ALT_Hardware", "ALT_Virtualization"
        ])
        self.category_combo.grid(row=2, column=1, sticky="ew", pady=2)
        self.category_combo.set("ALT_Security")  # Значение по умолчанию
        
        ttk.Label(main_frame, text="Версия ALT:").grid(row=3, column=0, sticky="w", pady=2)
        self.alt_version = ttk.Combobox(main_frame, values=["P10", "P11"])
        self.alt_version.grid(row=3, column=1, sticky="ew", pady=2)
        self.alt_version.set("P10")  # Значение по умолчанию
        
        # Тип значений
        ttk.Label(main_frame, text="Тип значений:").grid(row=4, column=0, sticky="w", pady=2)
        self.value_type = tk.StringVar(value="string")
        ttk.Radiobutton(main_frame, text="Строковые (enabled/disabled)", 
                       variable=self.value_type, value="string").grid(row=4, column=1, sticky="w")
        ttk.Radiobutton(main_frame, text="Числовые (1/0)", 
                       variable=self.value_type, value="decimal").grid(row=5, column=1, sticky="w")
        
        # Описания для ADML
        ttk.Label(main_frame, text="Имя политики (ADML):").grid(row=6, column=0, sticky="w", pady=2)
        self.display_name = ttk.Entry(main_frame, width=40)
        self.display_name.grid(row=6, column=1, sticky="ew", pady=2)
        
        ttk.Label(main_frame, text="Описание политики (ADML):").grid(row=7, column=0, sticky="nw", pady=2)
        self.description = tk.Text(main_frame, width=40, height=8, wrap=tk.WORD)
        self.description.grid(row=7, column=1, sticky="ew", pady=2)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=8, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сохранить", command=self._save).pack(side=tk.RIGHT, padx=5)
        
        # Привязка событий для авто-заполнения
        self.name_entry.bind("<KeyRelease>", self._auto_fill)
    
    def _auto_fill(self, event):
        """Автозаполнение Display Name если поле пустое"""
        if not self.display_name.get():
            self.display_name.insert(0, self.name_entry.get())
    
    def _save(self):
        """Собирает данные политики"""
        if not self.name_entry.get():
            messagebox.showerror("Ошибка", "Укажите имя политики!")
            return
            
        if not self.key_suffix.get():
            messagebox.showerror("Ошибка", "Укажите окончание ключа!")
            return
            
        self.result = {
            "name": self.name_entry.get(),
            "class": "Machine",
            "type": "simple",
            "key": f"Software\\BaseALT\\Policies\\{self.key_suffix.get()}",
            "valueName": self.name_entry.get(),
            "valueType": self.value_type.get(),
            "category": self.category_combo.get(),
            "altVersion": self.alt_version.get(),
            "displayName": self.display_name.get(),
            "description": self.description.get("1.0", tk.END).strip()
        }
        
        self.destroy()
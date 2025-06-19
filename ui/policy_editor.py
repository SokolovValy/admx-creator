import tkinter as tk
from tkinter import ttk, messagebox

class SimplePolicyEditor(tk.Toplevel):
    def __init__(self, parent, policy_data=None):
        super().__init__(parent)
        self.policy_data = policy_data
        self.result = None
        
        self.title("Редактор простой политики" if policy_data else "Новая простая политика")
        self._setup_ui()
        
        if policy_data:
            self._load_policy_data()
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Основные параметры политики
        ttk.Label(main_frame, text="Display Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=2)
        
        ttk.Label(main_frame, text="Класс политики:").grid(row=1, column=0, sticky="w", pady=2)
        self.policy_class = ttk.Combobox(main_frame, values=["Machine", "User"], state="readonly")
        self.policy_class.grid(row=1, column=1, sticky="ew", pady=2)
        self.policy_class.set("Machine")
        
        ttk.Label(main_frame, text="Ключ (окончание):").grid(row=2, column=0, sticky="w", pady=2)
        self.key_suffix = ttk.Entry(main_frame, width=40)
        self.key_suffix.insert(0, "Control")
        self.key_suffix.grid(row=2, column=1, sticky="ew", pady=2)
        
        ttk.Label(main_frame, text="ValueName:").grid(row=3, column=0, sticky="w", pady=2)
        self.value_name_entry = ttk.Entry(main_frame, width=40)
        self.value_name_entry.grid(row=3, column=1, sticky="ew", pady=2)
        
        ttk.Label(main_frame, text="Категория:").grid(row=4, column=0, sticky="w", pady=2)
        self.category_combo = ttk.Combobox(main_frame, values=[
            "ALT_System", "ALT_Security", "ALT_Services",
            "ALT_SSHD", "ALT_Systemd", "ALT_Network",
            "ALT_Hardware", "ALT_Virtualization"
        ], state="readonly")
        self.category_combo.grid(row=4, column=1, sticky="ew", pady=2)
        self.category_combo.set("ALT_Security")
        
        ttk.Label(main_frame, text="Версия ALT:").grid(row=5, column=0, sticky="w", pady=2)
        self.alt_version = ttk.Combobox(main_frame, values=["P10", "P11"], state="readonly")
        self.alt_version.grid(row=5, column=1, sticky="ew", pady=2)
        self.alt_version.set("P10")
        
        # Тип значений (строка/число)
        ttk.Label(main_frame, text="Тип значений:").grid(row=6, column=0, sticky="w", pady=2)
        self.value_type = tk.StringVar(value="string")
        ttk.Radiobutton(main_frame, text="Строковые (enabled/disabled)", 
                       variable=self.value_type, value="string").grid(row=6, column=1, sticky="w")
        ttk.Radiobutton(main_frame, text="Числовые (1/0)", 
                       variable=self.value_type, value="decimal").grid(row=7, column=1, sticky="w")
        
        # Описания для ADML
        ttk.Label(main_frame, text="Имя политики (ADML):").grid(row=8, column=0, sticky="w", pady=2)
        self.display_name = ttk.Entry(main_frame, width=40)
        self.display_name.grid(row=8, column=1, sticky="ew", pady=2)
        
        ttk.Label(main_frame, text="Описание политики (ADML):").grid(row=9, column=0, sticky="nw", pady=2)
        self.description = tk.Text(main_frame, width=40, height=8, wrap=tk.WORD)
        self.description.grid(row=9, column=1, sticky="ew", pady=2)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=10, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сохранить", command=self._save_policy).pack(side=tk.RIGHT, padx=5)
        
        # Автозаполнение только Display Name
        self.name_entry.bind("<KeyRelease>", lambda e: self._auto_fill_display_name())
    
    def _load_policy_data(self):
        """Загрузка данных существующей политики"""
        self.name_entry.insert(0, self.policy_data.get("name", ""))
        self.policy_class.set(self.policy_data.get("class", "Machine"))
        
        key_parts = self.policy_data.get("key", "").split("\\")
        if len(key_parts) > 3:
            self.key_suffix.delete(0, tk.END)
            self.key_suffix.insert(0, "\\".join(key_parts[3:]))
        
        self.value_name_entry.insert(0, self.policy_data.get("valueName", ""))
        self.category_combo.set(self.policy_data.get("category", "ALT_Security"))
        self.alt_version.set(self.policy_data.get("altVersion", "P10"))
        self.value_type.set(self.policy_data.get("valueType", "string"))
        self.display_name.insert(0, self.policy_data.get("displayName", ""))
        self.description.insert("1.0", self.policy_data.get("description", ""))
    
    def _auto_fill_display_name(self):
        """Автозаполнение только Display Name"""
        if not self.display_name.get():
            self.display_name.delete(0, tk.END)
            self.display_name.insert(0, self.name_entry.get())
    
    def _save_policy(self):
        """Сохранение политики"""
        if not self._validate_inputs():
            return
            
        self.result = {
            "name": self.name_entry.get(),
            "class": self.policy_class.get(),
            "type": "simple",
            "key": f"Software\\BaseALT\\Policies\\{self.key_suffix.get()}",
            "valueName": self.value_name_entry.get(),
            "valueType": self.value_type.get(),
            "category": self.category_combo.get(),
            "altVersion": self.alt_version.get(),
            "displayName": self.display_name.get(),
            "description": self.description.get("1.0", tk.END).strip()
        }
        
        self.destroy()
    
    def _validate_inputs(self):
        """Проверка введённых данных"""
        errors = []
        
        if not self.name_entry.get():
            errors.append("Не указано имя политики")
            
        if not self.policy_class.get():
            errors.append("Не указан класс политики")
        
        if not self.key_suffix.get():
            errors.append("Не указано окончание ключа")
            
        if not self.value_name_entry.get():
            errors.append("Не указано valueName (должно заполняться вручную)")
        
        if not self.display_name.get():
            errors.append("Не указано отображаемое имя (ADML)")
        
        if not self.description.get("1.0", tk.END).strip():
            errors.append("Не указано описание политики (ADML)")
        
        if errors:
            messagebox.showerror("Ошибки ввода", "\n".join(errors))
            return False
        
        return True

class DropdownPolicyEditor(tk.Toplevel):
    def __init__(self, parent, policy_data=None):
        super().__init__(parent)
        self.policy_data = policy_data
        self.result = None
        self.items = []

        self.title("Редактор политики с выпадающим списком" if policy_data else "Новая политика с выпадающим списком")
        self._setup_ui()

        if policy_data:
            self._load_policy_data()

    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Основные параметры политики
        ttk.Label(main_frame, text="Display Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(main_frame, text="Класс политики:").grid(row=1, column=0, sticky="w", pady=2)
        self.policy_class = ttk.Combobox(main_frame, values=["Machine", "User"], state="readonly")
        self.policy_class.grid(row=1, column=1, sticky="ew", pady=2)
        self.policy_class.set("Machine")

        ttk.Label(main_frame, text="Ключ (окончание):").grid(row=2, column=0, sticky="w", pady=2)
        self.key_suffix = ttk.Entry(main_frame, width=40)
        self.key_suffix.insert(0, "Control")
        self.key_suffix.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(main_frame, text="ValueName:").grid(row=3, column=0, sticky="w", pady=2)
        self.value_name_entry = ttk.Entry(main_frame, width=40)
        self.value_name_entry.grid(row=3, column=1, sticky="ew", pady=2)

        ttk.Label(main_frame, text="Категория:").grid(row=4, column=0, sticky="w", pady=2)
        self.category_combo = ttk.Combobox(main_frame, values=[
            "ALT_System", "ALT_Security", "ALT_Services",
            "ALT_SSHD", "ALT_Systemd", "ALT_Network",
            "ALT_Hardware", "ALT_Virtualization"
        ], state="readonly")
        self.category_combo.grid(row=4, column=1, sticky="ew", pady=2)
        self.category_combo.set("ALT_Security")

        ttk.Label(main_frame, text="Версия ALT:").grid(row=5, column=0, sticky="w", pady=2)
        self.alt_version = ttk.Combobox(main_frame, values=["P10", "P11"], state="readonly")
        self.alt_version.grid(row=5, column=1, sticky="ew", pady=2)
        self.alt_version.set("P10")

        # Параметры для dropdown
        ttk.Label(main_frame, text="Enum ID (без -setter):").grid(row=6, column=0, sticky="w", pady=2)
        self.enum_id_entry = ttk.Entry(main_frame, width=40)
        self.enum_id_entry.grid(row=6, column=1, sticky="ew", pady=2)

        ttk.Label(main_frame, text="Название списка (refId):").grid(row=7, column=0, sticky="w", pady=2)
        self.list_name_entry = ttk.Entry(main_frame, width=40)
        self.list_name_entry.grid(row=7, column=1, sticky="ew", pady=2)

        # Описание политики
        ttk.Label(main_frame, text="Описание политики:").grid(row=8, column=0, sticky="nw", pady=2)
        self.description = tk.Text(main_frame, width=40, height=5, wrap=tk.WORD)
        self.description.grid(row=8, column=1, sticky="ew", pady=2)

        # Фрейм для элементов dropdown
        self.items_frame = ttk.LabelFrame(main_frame, text="Элементы списка", padding=10)
        self.items_frame.grid(row=9, columnspan=2, sticky="ew", pady=10)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=10, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сохранить", command=self._save_policy).pack(side=tk.RIGHT, padx=5)

        # Автозаполнение
        self.name_entry.bind("<KeyRelease>", lambda e: self._auto_fill_display_name())
        self.enum_id_entry.bind("<KeyRelease>", lambda e: self._auto_fill_list_name())

    def _auto_fill_list_name(self):
        """Автозаполнение названия списка"""
        if not self.list_name_entry.get():
            self.list_name_entry.delete(0, tk.END)
            self.list_name_entry.insert(0, self.enum_id_entry.get())

    def _load_policy_data(self):
        """Загрузка данных существующей политики"""
        self.name_entry.insert(0, self.policy_data.get("name", ""))
        self.policy_class.set(self.policy_data.get("class", "Machine"))

        key_parts = self.policy_data.get("key", "").split("\\")
        if len(key_parts) > 3:
            self.key_suffix.delete(0, tk.END)
            self.key_suffix.insert(0, "\\".join(key_parts[3:]))

        self.value_name_entry.insert(0, self.policy_data.get("valueName", ""))
        self.category_combo.set(self.policy_data.get("category", "ALT_Security"))
        self.alt_version.set(self.policy_data.get("altVersion", "P10"))
        self.enum_id_entry.insert(0, self.policy_data.get("enumId", "").replace("-setter", ""))
        self.list_name_entry.insert(0, self.policy_data.get("listName", ""))
        self.description.insert("1.0", self.policy_data.get("description", ""))

        # Загрузка элементов
        for item in self.policy_data.get("items", []):
            self._add_item_frame(item["name"], item["value"])

    def _add_item_frame(self, name="", value=""):
        """Добавляет фрейм для одного элемента dropdown"""
        frame = ttk.Frame(self.items_frame)
        frame.pack(fill=tk.X, pady=2)

        # Название элемента
        ttk.Label(frame, text="Название:").pack(side=tk.LEFT, padx=5)
        name_entry = ttk.Entry(frame, width=20)
        name_entry.insert(0, name)
        name_entry.pack(side=tk.LEFT, padx=5)

        # Значение элемента
        ttk.Label(frame, text="Значение:").pack(side=tk.LEFT, padx=5)
        value_entry = ttk.Entry(frame, width=20)
        value_entry.insert(0, value)
        value_entry.pack(side=tk.LEFT, padx=5)

        self.items.append((name_entry, value_entry))

    def _save_policy(self):
        """Сохранение политики"""
        if not self._validate_inputs():
            return

        # Собираем элементы dropdown
        items = []
        for name_entry, value_entry in self.items:
            items.append({
                "name": name_entry.get(),
                "value": value_entry.get()
            })

        self.result = {
            "name": self.name_entry.get(),
            "class": self.policy_class.get(),
            "type": "dropdown",
            "key": f"Software\\BaseALT\\Policies\\{self.key_suffix.get()}",
            "valueName": self.value_name_entry.get(),
            "category": self.category_combo.get(),
            "altVersion": self.alt_version.get(),
            "displayName": self.name_entry.get(),
            "description": self.description.get("1.0", tk.END).strip(),
            "enumId": f"{self.enum_id_entry.get()}-setter",
            "listName": self.list_name_entry.get(),
            "presentation": f"{self.name_entry.get()}-pr",
            "items": items
        }

        self.destroy()

    def _validate_inputs(self):
        """Проверка введённых данных"""
        errors = []

        if not self.name_entry.get():
            errors.append("Не указано имя политики")

        if not self.policy_class.get():
            errors.append("Не указан класс политики")

        if not self.key_suffix.get():
            errors.append("Не указано окончание ключа")

        if not self.value_name_entry.get():
            errors.append("Не указано valueName")

        if not self.enum_id_entry.get():
            errors.append("Не указан Enum ID")

        if not self.list_name_entry.get():
            errors.append("Не указано название списка")

        if not self.description.get("1.0", tk.END).strip():
            errors.append("Не указано описание политики")

        if len(self.items) == 0:
            errors.append("Добавьте хотя бы один элемент в список")

        if errors:
            messagebox.showerror("Ошибки ввода", "\n".join(errors))
            return False

        return True
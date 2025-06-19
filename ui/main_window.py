import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import traceback
from .policy_editor import SimplePolicyEditor  # Изменённый импорт
from .policy_editor import DropdownPolicyEditor
from .widgets import Tooltip
from core.policy_loader import load_policies, save_policies
from core.admx_generator import generate_admx
from core.adml_generator import generate_adml
from core.validator import validate_xml

class MainWindow:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self._setup_ui()

    def _setup_ui(self):
        self.root.title("ALT Linux Policy Editor")

        # Панель инструментов
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        buttons = [
            ("+ Новая", self._add_policy, "Добавить новую политику"),
            ("Редактировать", self._edit_policy, "Редактировать выбранную"),
            ("Удалить", self._delete_policy, "Удалить выбранную"),
            ("Экспорт", self._export, "Генерация ADMX/ADML")
        ]

        for text, cmd, tip in buttons:
            btn = ttk.Button(toolbar, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=2)
            Tooltip(btn, tip)

        # Список политик
        self.policy_list = ttk.Treeview(self.root,
                                      columns=("name", "type", "class"),
                                      show="headings")
        self.policy_list.heading("name", text="Имя")
        self.policy_list.heading("type", text="Тип")
        self.policy_list.heading("class", text="Класс")
        self.policy_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._update_list()

    def _update_list(self):
        self.policy_list.delete(*self.policy_list.get_children())
        for policy in self.config["policies"]:
            self.policy_list.insert("", "end",
                                 values=(policy["name"],
                                        policy.get("type", "simple"),
                                        policy["class"]))

    def _add_policy(self):
        """Выбор типа новой политики"""
        choice = tk.Toplevel(self.root)
        choice.title("Выберите тип политики")

        ttk.Label(choice, text="Создать:", padding=10).pack()

        ttk.Button(choice, text="Простую политику (On/Off)",
                command=lambda: self._create_simple_policy(choice)).pack(fill=tk.X, padx=20, pady=5)

        ttk.Button(choice, text="Политику с выпадающим списком",
                command=lambda: self._create_dropdown_policy(choice)).pack(fill=tk.X, padx=20, pady=5)

        ttk.Button(choice, text="Отмена", command=choice.destroy).pack(fill=tk.X, padx=20, pady=10)

    def _create_dropdown_policy(self, choice_window):
        """Создание политики с выпадающим списком"""
        choice_window.destroy()

        # Запрос количества элементов
        count = self._ask_item_count()
        if count is None:  # Пользователь отменил
            return

        # Создаем редактор
        editor = DropdownPolicyEditor(self.root)

        # Добавляем указанное количество элементов
        for _ in range(count):
            editor._add_item_frame()

        self.root.wait_window(editor)

        if editor.result:
            self.config["policies"].append(editor.result)
            save_policies("config.yml", self.config)
            self._update_list()

    def _ask_item_count(self):
        """Запрашивает количество элементов в dropdown"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Количество элементов")

        ttk.Label(dialog, text="Введите количество элементов (1-8):", padding=10).pack()

        count_var = tk.IntVar(value=1)
        spinbox = ttk.Spinbox(dialog, from_=1, to=8, textvariable=count_var)
        spinbox.pack(pady=5)

        result = None

        def on_ok():
            nonlocal result
            result = count_var.get()
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=5)

        dialog.transient(self.root)
        dialog.grab_set()
        dialog.wait_window(dialog)

        return result

    def _create_simple_policy(self, choice_window):
        """Создание простой политики"""
        choice_window.destroy()
        editor = SimplePolicyEditor(self.root)
        self.root.wait_window(editor)

        if editor.result:
            self.config["policies"].append(editor.result)
            save_policies("config.yml", self.config)
            self._update_list()

    def _show_complex_notice(self, choice_window):
        """Уведомление о сложных политиках"""
        choice_window.destroy()
        messagebox.showinfo("Информация", "Редактор сложных политик будет реализован позже")

    def _edit_policy(self):
        """Редактирование существующей политики"""
        selection = self.policy_list.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите политику!")
            return

        selected_name = self.policy_list.item(selection[0])["values"][0]
        policy = next(p for p in self.config["policies"] if p["name"] == selected_name)

        # Проверяем тип политики для выбора редактора
        if policy.get("type") == "simple":
            editor = SimplePolicyEditor(self.root, policy_data=policy)  # Передаем данные
        else:
            self._show_complex_notice()
            return

        self.root.wait_window(editor)

        if editor.result:
            idx = self.config["policies"].index(policy)
            self.config["policies"][idx] = editor.result
            save_policies("config.yml", self.config)
            self._update_list()

    def _delete_policy(self):
        """Удаление политики"""
        selection = self.policy_list.selection()
        if not selection:
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную политику?"):
            selected_name = self.policy_list.item(selection[0])["values"][0]
            self.config["policies"] = [p for p in self.config["policies"]
                                     if p["name"] != selected_name]
            save_policies("config.yml", self.config)
            self._update_list()

    def _export(self):
        """Экспорт политик в файлы"""
        export_dir = filedialog.askdirectory(title="Выберите папку для экспорта")
        if not export_dir:
            return

        try:
            # Создаем директории
            Path(export_dir).mkdir(exist_ok=True)
            adml_dir = Path(export_dir) / "ru-RU"
            adml_dir.mkdir(exist_ok=True)

            # Генерация файлов
            generate_admx(self.config, Path(export_dir) / "policies.admx")
            generate_adml(self.config, "ru-RU", adml_dir / "policies.adml")

            # Валидация
            if validate_xml(Path(export_dir) / "policies.admx"):
                messagebox.showinfo("Экспорт", f"Файлы успешно экспортированы в:\n{export_dir}")
            else:
                messagebox.showwarning("Предупреждение",
                    "Файлы созданы, но есть проблемы с валидацией XML")

        except Exception as e:
            messagebox.showerror("Ошибка экспорта",
                f"Не удалось экспортировать политики:\n{str(e)}")
            print(f"Подробности ошибки экспорта: {traceback.format_exc()}")
import tkinter as tk
from tkinter import scrolledtext
from logic import CalculatorLogic

class ScientificCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Calc Note")
        self.root.geometry("") # コンテンツに合わせて自動調整
        self.root.configure(bg="#2d2d2d")

        self.logic = CalculatorLogic()
        self.result_var = tk.StringVar(value="0")
        self.show_funcs = False # 関数ボタンの表示状態

        self._setup_ui()
        self._bind_keys()
        self.text_area.focus_set()

    def _setup_ui(self):
        # メインフレーム
        self.main_frame = tk.Frame(self.root, bg="#2d2d2d")
        self.main_frame.pack(expand=True, fill="both", pady=5)

        # 式入力欄 (5行分程度の高さ、リサイズで広がるように設定)
        self.text_area = scrolledtext.ScrolledText(
            self.main_frame, 
            bg="#2d2d2d", 
            fg="#ffffff", 
            insertbackground="white",
            font=("Consolas", 14),
            undo=True,
            bd=0,
            height=5, # 初期行数
            highlightthickness=1,
            highlightbackground="#4d4d4d",
            highlightcolor="#00aaff",
        )
        self.text_area.pack(expand=True, fill="both", padx=15, pady=5)
        self.text_area.insert(tk.END, "# 計算ノート\na = 10\nsin(a) + π")

        # 結果表示欄 (固定高さ)
        self.result_entry = tk.Entry(
            self.main_frame, 
            textvariable=self.result_var, 
            justify="right", 
            bg="#1e1e1e", 
            fg="#4cd964",
            font=("Arial", 24, "bold"),
            bd=0,
            readonlybackground="#1e1e1e",
            state="readonly"
        )
        self.result_entry.pack(expand=False, fill="x", padx=15, pady=10, ipady=5)

        # アクションボタン（AC, Calculate, Toggle Functions）
        btn_frame = tk.Frame(self.main_frame, bg="#2d2d2d")
        btn_frame.pack(fill="x", padx=15, pady=5)

        self.calc_btn = tk.Button(
            btn_frame, text="Calculate (Ctrl+Enter)", command=self._on_equal,
            font=("Arial", 11, "bold"), bg="#4cd964", fg="white", bd=0, pady=8
        )
        self.calc_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.ac_btn = tk.Button(
            btn_frame, text="AC", command=self._on_ac,
            font=("Arial", 11, "bold"), bg="#ff3b30", fg="white", bd=0, pady=8, width=5
        )
        self.ac_btn.pack(side="left", padx=5)

        self.toggle_btn = tk.Button(
            btn_frame, text="Functions ▼", command=self._toggle_functions,
            font=("Arial", 11), bg="#3a3a3a", fg="#00aaff", bd=0, pady=8
        )
        self.toggle_btn.pack(side="left", padx=(5, 0))

        # 関数ボタンエリア (初期は非表示)
        self.func_frame = tk.Frame(self.main_frame, bg="#2d2d2d")
        # .pack() は _toggle_functions で制御

        funcs = [
            ('sin', 'cos', 'tan', '^'),
            ('log', 'ln', 'sqrt', 'π'),
            ('(', ')', 'e', 'DEL')
        ]

        for r, row_funcs in enumerate(funcs):
            for c, f in enumerate(row_funcs):
                btn = tk.Button(
                    self.func_frame, text=f, command=lambda x=f: self._on_func_click(x),
                    font=("Arial", 10), bg="#3a3a3a", fg="white", bd=0, width=8, pady=5
                )
                btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
        
        for i in range(4):
            self.func_frame.grid_columnconfigure(i, weight=1)

    def _bind_keys(self):
        self.root.bind("<Control-Return>", lambda e: self._on_equal())
        self.root.bind("<Escape>", lambda e: self._on_ac())

    def _toggle_functions(self):
        self.show_funcs = not self.show_funcs
        if self.show_funcs:
            self.func_frame.pack(fill="x", padx=15, pady=(0, 10))
            self.toggle_btn.config(text="Functions ▲")
        else:
            self.func_frame.pack_forget()
            self.toggle_btn.config(text="Functions ▼")

        # 画面サイズをコンテンツに合わせる
        self.root.geometry("")


    def _on_func_click(self, func):
        if func == 'DEL':
            # 1文字削除
            try:
                self.text_area.delete("insert-1c", "insert")
            except: pass
        elif func in self.logic.functions:
            self.text_area.insert(tk.INSERT, f"{func}(")
        else:
            self.text_area.insert(tk.INSERT, func)
        self.text_area.focus_set()

    def _on_ac(self):
        self.text_area.delete("1.0", tk.END)
        self.result_var.set("0")

    def _on_equal(self):
        content = self.text_area.get("1.0", tk.END).strip()
        if not content: return
        
        # コメント除去
        clean_lines = [line.split('#')[0].strip() for line in content.split('\n') if line.split('#')[0].strip()]
        
        result = self.logic.calculate("\n".join(clean_lines))
        self.result_var.set(str(result))
        self.text_area.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScientificCalculatorApp(root)
    root.mainloop()

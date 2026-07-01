import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def create_main_window(root):
    root.title("Mail Visualizer")
    root.geometry("820x520")
    root.configure(bg="#f4f6f8")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Yu Gothic UI", 10), padding=6)
    style.configure("TCheckbutton", font=("Yu Gothic UI", 10), background="#f4f6f8")
    style.configure("TLabel", font=("Yu Gothic UI", 10), background="#f4f6f8")
    style.configure("Title.TLabel", font=("Yu Gothic UI", 24, "bold"), background="#f4f6f8")
    style.configure("Main.TButton", font=("Yu Gothic UI", 13, "bold"), padding=10)

    input_path = tk.StringVar()
    output_path = tk.StringVar()

    ttk.Label(root, text="Mail Visualizer", style="Title.TLabel").pack(pady=(28, 8))
    ttk.Label(root, text="メールデータを読み込み、Excel・HTML・本文txtに変換します").pack(pady=(0, 22))

    card = tk.Frame(root, bg="white", padx=28, pady=24)
    card.pack(fill="x", padx=40)

    def select_input_file():
        path = filedialog.askopenfilename(
            title="メールファイルを選択",
            filetypes=[("Mail/Text files", "*.txt *.mbox *.eml"), ("All files", "*.*")]
        )
        if path:
            input_path.set(path)

    def select_output_folder():
        path = filedialog.askdirectory(title="出力先フォルダを選択")
        if path:
            output_path.set(path)

    tk.Label(card, text="入力ファイル", bg="white", font=("Yu Gothic UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=10)
    ttk.Entry(card, textvariable=input_path, width=72).grid(row=0, column=1, padx=12)
    ttk.Button(card, text="参照", command=select_input_file).grid(row=0, column=2)

    tk.Label(card, text="出力フォルダ", bg="white", font=("Yu Gothic UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
    ttk.Entry(card, textvariable=output_path, width=72).grid(row=1, column=1, padx=12)
    ttk.Button(card, text="参照", command=select_output_folder).grid(row=1, column=2)

    excel_var = tk.BooleanVar(value=True)
    html_var = tk.BooleanVar(value=True)
    txt_var = tk.BooleanVar(value=True)

    option_frame = tk.Frame(card, bg="white")
    option_frame.grid(row=2, column=1, sticky="w", pady=(18, 6))

    tk.Checkbutton(option_frame, text="Excel一覧を作る", variable=excel_var, bg="white").pack(anchor="w", pady=3)
    tk.Checkbutton(option_frame, text="HTMLビューアを作る", variable=html_var, bg="white").pack(anchor="w", pady=3)
    tk.Checkbutton(option_frame, text="本文txtを分割保存する", variable=txt_var, bg="white").pack(anchor="w", pady=3)

    status = ttk.Label(root, text="準備完了")
    status.pack(pady=18)

    def start_convert():
        if not input_path.get():
            messagebox.showwarning("確認", "入力ファイルを選択してください。")
            return
        if not output_path.get():
            messagebox.showwarning("確認", "出力フォルダを選択してください。")
            return
        status.config(text="次はここに変換処理を接続します。")
        messagebox.showinfo("確認", "画面は完成。次に解析処理をつなげます。")

    ttk.Button(root, text="変換開始", style="Main.TButton", width=28, command=start_convert).pack(pady=4)
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from services.mail_service import MailService


def create_main_window(root):
    root.title("Mail Visualizer")
    root.geometry("900x560")
    root.configure(bg="#f4f6f8")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Yu Gothic UI", 10), padding=6)
    style.configure("Main.TButton", font=("Yu Gothic UI", 13, "bold"), padding=10)
    style.configure("TLabel", font=("Yu Gothic UI", 10), background="#f4f6f8")
    style.configure("Title.TLabel", font=("Yu Gothic UI", 26, "bold"), background="#f4f6f8")

    input_path = tk.StringVar()
    output_path = tk.StringVar()

    excel_var = tk.BooleanVar(value=True)
    html_var = tk.BooleanVar(value=True)
    txt_var = tk.BooleanVar(value=True)

    ttk.Label(root, text="Mail Visualizer", style="Title.TLabel").pack(pady=(28, 8))
    ttk.Label(root, text="メールデータを読み込み、Excel・HTML・本文txtに変換します").pack(pady=(0, 22))

    card = tk.Frame(root, bg="white", padx=32, pady=26)
    card.pack(fill="x", padx=42)

    def select_input_file():
        path = filedialog.askopenfilename(
            title="メールファイルを選択",
            filetypes=[
                ("Mail/Text files", "*.txt *.mbox *.eml"),
                ("All files", "*.*"),
            ],
        )
        if path:
            input_path.set(path)

    def select_output_folder():
        path = filedialog.askdirectory(title="出力先フォルダを選択")
        if path:
            output_path.set(path)

    tk.Label(card, text="入力ファイル", bg="white", font=("Yu Gothic UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=12)
    ttk.Entry(card, textvariable=input_path, width=78).grid(row=0, column=1, padx=12)
    ttk.Button(card, text="参照", command=select_input_file).grid(row=0, column=2)

    tk.Label(card, text="出力フォルダ", bg="white", font=("Yu Gothic UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=12)
    ttk.Entry(card, textvariable=output_path, width=78).grid(row=1, column=1, padx=12)
    ttk.Button(card, text="参照", command=select_output_folder).grid(row=1, column=2)

    option_frame = tk.Frame(card, bg="white")
    option_frame.grid(row=2, column=1, sticky="w", pady=(18, 6))

    tk.Checkbutton(option_frame, text="Excel一覧を作る", variable=excel_var, bg="white").pack(anchor="w", pady=4)
    tk.Checkbutton(option_frame, text="HTMLビューアを作る", variable=html_var, bg="white").pack(anchor="w", pady=4)
    tk.Checkbutton(option_frame, text="本文txtを分割保存する", variable=txt_var, bg="white").pack(anchor="w", pady=4)

    status = ttk.Label(root, text="準備完了")
    status.pack(pady=20)

    def start_convert():
        if not input_path.get():
            messagebox.showwarning("確認", "入力ファイルを選択してください。")
            return

        if not output_path.get():
            messagebox.showwarning("確認", "出力フォルダを選択してください。")
            return

        try:
            status.config(text="変換中...")
            root.update()

            os.makedirs(output_path.get(), exist_ok=True)

            service = MailService()

            mails = service.convert(
                input_file=input_path.get(),
                output_folder=output_path.get(),
                excel=excel_var.get(),
                html=html_var.get(),
                txt=txt_var.get(),
            )

            status.config(text=f"完了：{len(mails)}件")
            messagebox.showinfo("完了", f"{len(mails)}件のメールを変換しました。")

        except Exception as e:
            status.config(text="エラー発生")
            messagebox.showerror("エラー", str(e))

    ttk.Button(
        root,
        text="変換開始",
        style="Main.TButton",
        width=30,
        command=start_convert,
    ).pack(pady=8)
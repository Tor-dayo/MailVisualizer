import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from services.mail_service import MailService

try:
    from tkinterdnd2 import DND_FILES
except ImportError:
    DND_FILES = None


COLORS = {
    "navy": "#142C44",
    "navy_light": "#1D3B57",
    "blue": "#2F80ED",
    "blue_hover": "#246AC2",
    "background": "#F2F5F8",
    "surface": "#FFFFFF",
    "border": "#D8E1E8",
    "text": "#17212B",
    "muted": "#66788A",
    "success": "#18794E",
    "success_bg": "#EAF7F0",
    "danger": "#B42318",
    "danger_bg": "#FDECEC",
}


def create_main_window(root):
    root.title("Mail Visualizer v0.3.1")
    root.geometry("1000x720")
    root.minsize(860, 650)
    root.configure(bg=COLORS["background"])

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Modern.TEntry",
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        padding=10,
    )
    style.configure(
        "Primary.TButton",
        font=("Yu Gothic UI", 11, "bold"),
        foreground="white",
        background=COLORS["blue"],
        bordercolor=COLORS["blue"],
        padding=(22, 11),
    )
    style.map("Primary.TButton", background=[("active", COLORS["blue_hover"]), ("disabled", "#AAB8C5")])
    style.configure(
        "Secondary.TButton",
        font=("Yu Gothic UI", 10, "bold"),
        foreground=COLORS["navy"],
        background=COLORS["surface"],
        bordercolor=COLORS["border"],
        padding=(14, 9),
    )
    style.map("Secondary.TButton", background=[("active", "#EAF1F7")])
    style.configure(
        "Accent.Horizontal.TProgressbar",
        troughcolor="#DDE6ED",
        background=COLORS["blue"],
        bordercolor="#DDE6ED",
        lightcolor=COLORS["blue"],
        darkcolor=COLORS["blue"],
    )

    input_path = tk.StringVar()
    output_path = tk.StringVar()
    excel_var = tk.BooleanVar(value=True)
    html_var = tk.BooleanVar(value=True)
    print_var = tk.BooleanVar(value=True)
    txt_var = tk.BooleanVar(value=True)
    status_var = tk.StringVar(value="ファイルを選択して変換を開始してください")

    header = tk.Frame(root, bg=COLORS["navy"], height=106)
    header.pack(fill="x")
    header.pack_propagate(False)
    header_inner = tk.Frame(header, bg=COLORS["navy"])
    header_inner.pack(fill="both", expand=True, padx=38, pady=20)

    brand = tk.Frame(header_inner, bg=COLORS["navy"])
    brand.pack(side="left")
    icon = tk.Label(
        brand,
        text="M",
        width=3,
        height=1,
        bg=COLORS["blue"],
        fg="white",
        font=("Yu Gothic UI", 18, "bold"),
    )
    icon.pack(side="left", padx=(0, 14))
    titles = tk.Frame(brand, bg=COLORS["navy"])
    titles.pack(side="left")
    tk.Label(titles, text="Mail Visualizer", bg=COLORS["navy"], fg="white", font=("Yu Gothic UI", 22, "bold")).pack(anchor="w")
    tk.Label(titles, text="Mbox・EML 精査／可視化ツール", bg=COLORS["navy"], fg="#BFD0DF", font=("Yu Gothic UI", 9)).pack(anchor="w")
    tk.Label(header_inner, text="VERSION 0.3.1", bg=COLORS["navy_light"], fg="#DCE8F2", font=("Yu Gothic UI", 8, "bold"), padx=10, pady=5).pack(side="right", anchor="n")

    content = tk.Frame(root, bg=COLORS["background"])
    content.pack(fill="both", expand=True, padx=38, pady=24)
    content.grid_columnconfigure(0, weight=1)

    def card(parent, row, title, subtitle=None):
        frame = tk.Frame(parent, bg=COLORS["surface"], highlightbackground=COLORS["border"], highlightthickness=1)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 14))
        frame.grid_columnconfigure(0, weight=1)
        heading = tk.Frame(frame, bg=COLORS["surface"])
        heading.grid(row=0, column=0, sticky="ew", padx=22, pady=(17, 10))
        tk.Label(heading, text=title, bg=COLORS["surface"], fg=COLORS["text"], font=("Yu Gothic UI", 11, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(heading, text=subtitle, bg=COLORS["surface"], fg=COLORS["muted"], font=("Yu Gothic UI", 8)).pack(anchor="w", pady=(2, 0))
        return frame

    input_card = card(content, 0, "01  入力メールファイル", "Mbox・EML・メール形式のTXTに対応")
    input_row = tk.Frame(input_card, bg=COLORS["surface"])
    input_row.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 18))
    input_row.grid_columnconfigure(0, weight=1)
    input_entry = ttk.Entry(input_row, textvariable=input_path, style="Modern.TEntry", font=("Yu Gothic UI", 10))
    input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

    def select_input_file():
        path = filedialog.askopenfilename(
            title="メールファイルを選択",
            filetypes=[("Mail files", "*.mbox *.eml *.txt"), ("All files", "*.*")],
        )
        if path:
            set_input_path(path)

    ttk.Button(input_row, text="ファイルを選択", style="Secondary.TButton", command=select_input_file).grid(row=0, column=1)
    drop_hint = tk.Label(input_card, text="ここへファイルをドラッグ＆ドロップできます", bg="#F5F9FC", fg=COLORS["blue"], font=("Yu Gothic UI", 9, "bold"), pady=8)
    drop_hint.grid(row=2, column=0, sticky="ew")

    output_card = card(content, 1, "02  出力先フォルダ")
    output_row = tk.Frame(output_card, bg=COLORS["surface"])
    output_row.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 18))
    output_row.grid_columnconfigure(0, weight=1)
    ttk.Entry(output_row, textvariable=output_path, style="Modern.TEntry", font=("Yu Gothic UI", 10)).grid(row=0, column=0, sticky="ew", padx=(0, 10))

    def select_output_folder():
        path = filedialog.askdirectory(title="出力先フォルダを選択")
        if path:
            output_path.set(path)

    ttk.Button(output_row, text="フォルダを選択", style="Secondary.TButton", command=select_output_folder).grid(row=0, column=1)

    option_card = card(content, 2, "03  作成するファイル", "必要な出力形式を選択してください")
    options = tk.Frame(option_card, bg=COLORS["surface"])
    options.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 17))
    for column in range(4):
        options.grid_columnconfigure(column, weight=1, uniform="option")

    option_items = [
        ("Excel一覧", "検索・集計用", excel_var),
        ("HTMLビューア", "精査・重要チェック", html_var),
        ("印刷レポート", "A4・PDF保存", print_var),
        ("本文TXT", "メール別に保存", txt_var),
    ]
    for column, (title, description, variable) in enumerate(option_items):
        option = tk.Frame(options, bg="#F7F9FB", highlightbackground=COLORS["border"], highlightthickness=1)
        option.grid(row=0, column=column, sticky="nsew", padx=4)
        check = tk.Checkbutton(option, text=title, variable=variable, bg="#F7F9FB", activebackground="#F7F9FB", fg=COLORS["text"], selectcolor="white", font=("Yu Gothic UI", 9, "bold"), anchor="w")
        check.pack(fill="x", padx=10, pady=(9, 0))
        tk.Label(option, text=description, bg="#F7F9FB", fg=COLORS["muted"], font=("Yu Gothic UI", 8)).pack(anchor="w", padx=13, pady=(1, 9))

    footer = tk.Frame(content, bg=COLORS["background"])
    footer.grid(row=3, column=0, sticky="ew", pady=(2, 0))
    footer.grid_columnconfigure(0, weight=1)
    status_panel = tk.Frame(footer, bg=COLORS["background"])
    status_panel.grid(row=0, column=0, sticky="ew", padx=(0, 20))
    status_label = tk.Label(status_panel, textvariable=status_var, bg=COLORS["background"], fg=COLORS["muted"], font=("Yu Gothic UI", 9), anchor="w")
    status_label.pack(fill="x")
    progress = ttk.Progressbar(status_panel, mode="indeterminate", style="Accent.Horizontal.TProgressbar")
    progress.pack(fill="x", pady=(8, 0))

    button_panel = tk.Frame(footer, bg=COLORS["background"])
    button_panel.grid(row=0, column=1, sticky="e")

    def open_output_folder():
        path = output_path.get()
        if path and os.path.isdir(path):
            os.startfile(path)
        else:
            messagebox.showwarning("確認", "開ける出力フォルダがありません。")

    open_button = ttk.Button(button_panel, text="出力先を開く", style="Secondary.TButton", command=open_output_folder, state="disabled")
    open_button.pack(side="left", padx=(0, 8))

    def set_input_path(path):
        path = os.path.normpath(path)
        if not os.path.isfile(path):
            messagebox.showwarning("確認", "ドロップされた項目はファイルではありません。")
            return
        input_path.set(path)
        if not output_path.get():
            output_path.set(str(Path(path).parent / "MailVisualizer_output"))
        status_var.set(f"選択済み：{Path(path).name}")
        status_label.configure(fg=COLORS["muted"])

    def on_drop(event):
        try:
            paths = root.tk.splitlist(event.data)
        except tk.TclError:
            paths = [event.data.strip("{}")]
        if paths:
            set_input_path(paths[0])

    if DND_FILES:
        for widget in (input_card, input_entry, drop_hint):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", on_drop)
    else:
        drop_hint.configure(text="ドラッグ＆ドロップ機能を利用するにはアプリ版をお使いください", fg=COLORS["muted"])

    def finish_convert(mails):
        progress.stop()
        convert_button.configure(state="normal", text="変換を開始")
        open_button.configure(state="normal")
        status_var.set(f"変換完了：{len(mails)}件のメールを出力しました")
        status_label.configure(fg=COLORS["success"])
        messagebox.showinfo("変換完了", f"{len(mails)}件のメールを変換しました。\n\n出力先：\n{output_path.get()}")

    def fail_convert(error):
        progress.stop()
        convert_button.configure(state="normal", text="変換を開始")
        status_var.set("変換中にエラーが発生しました")
        status_label.configure(fg=COLORS["danger"])
        messagebox.showerror("変換エラー", str(error))

    def run_convert(options):
        try:
            service = MailService()
            mails = service.convert(
                input_file=options["input_file"],
                output_folder=options["output_folder"],
                excel=options["excel"],
                html=options["html"],
                print_report=options["print_report"],
                txt=options["txt"],
            )
            root.after(0, finish_convert, mails)
        except Exception as error:
            root.after(0, fail_convert, error)

    def start_convert():
        if not input_path.get() or not os.path.isfile(input_path.get()):
            messagebox.showwarning("入力ファイル", "変換するメールファイルを選択してください。")
            return
        if not output_path.get():
            messagebox.showwarning("出力先", "出力先フォルダを選択してください。")
            return
        if not any((excel_var.get(), html_var.get(), print_var.get(), txt_var.get())):
            messagebox.showwarning("出力形式", "作成するファイルを1つ以上選択してください。")
            return

        os.makedirs(output_path.get(), exist_ok=True)
        convert_button.configure(state="disabled", text="変換しています…")
        open_button.configure(state="disabled")
        status_var.set("メールを解析して出力しています…")
        status_label.configure(fg=COLORS["blue"])
        progress.start(12)
        options = {
            "input_file": input_path.get(),
            "output_folder": output_path.get(),
            "excel": excel_var.get(),
            "html": html_var.get(),
            "print_report": print_var.get(),
            "txt": txt_var.get(),
        }
        threading.Thread(target=run_convert, args=(options,), daemon=True).start()

    convert_button = ttk.Button(button_panel, text="変換を開始", style="Primary.TButton", command=start_convert)
    convert_button.pack(side="left")

    root.bind("<Control-o>", lambda _event: select_input_file())

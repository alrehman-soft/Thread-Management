import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import get_connection, get_available_stock
from send_dyeing_list import open_send_dyeing_list
from tkcalendar import DateEntry

# ================= BATCH ID =================
def generate_batch_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM send_dyeing")
    result = cursor.fetchone()
    conn.close()
    count = result["total"] + 1 if result else 1
    return f"DYE-{count:04d}"


# ================= THREAD =================
def get_threads():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT thread_name FROM stock_in")
    rows = cursor.fetchall()
    conn.close()
    return [r["thread_name"] for r in rows]


# ================= SIZE =================
def get_sizes(thread):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT size FROM stock_in WHERE thread_name=%s", (thread,))
    rows = cursor.fetchall()
    conn.close()
    return [r["size"] for r in rows]


# ================= STOCK ID =================
def get_stock_in_id(thread, size):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM stock_in
        WHERE thread_name=%s AND size=%s LIMIT 1
    """, (thread, size))
    row = cursor.fetchone()
    conn.close()
    return row["id"] if row else None

# ================= MAIN PAGE =================
def open_send_dyeing(win,back_callback=None):
    for w in win.winfo_children():
        w.destroy()

    win.config(bg="#f4f6f9")

    # ================= SCROLL =================
    container = tk.Frame(win)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg="#f4f6f9", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    scroll_frame = tk.Frame(canvas, bg="#f4f6f9")

    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def resize(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", resize)

    # Mouse scroll
    def mousewheel_scroll(event):
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)),"units")
        except tk.TclError:
            pass

    canvas.bind_all("<MouseWheel>", mousewheel_scroll)

    # ================= VARIABLES =================
    date_var = tk.StringVar(master=win,value=datetime.now().strftime("%Y-%m-%d"))
    batch_var = tk.StringVar(master=win,value=generate_batch_id())
    expected_var = tk.StringVar(master=win)
    thread_var = tk.StringVar(master=win)
    size_var = tk.StringVar(master=win)
    available_var = tk.StringVar(master=win)
    issued_var = tk.StringVar(master=win)
    dyeing_var = tk.StringVar(master=win)
    reason_var = tk.StringVar(master=win)
    sender_var = tk.StringVar(master=win)
    receiver_var = tk.StringVar(master=win)

    # ================= TITLE =================
    tk.Label(scroll_frame, text="🎨 Send to Dyeing Receipt",
             font=("Arial", 18, "bold"),
             bg="#f4f6f9").pack(pady=10)

    # ================= THREAD FRAME =================
    thread_frame = tk.LabelFrame(scroll_frame, text="Thread Details",font=("Arial", 14, "bold"),bg="#f4f6f9", padx=20, pady=10)
    thread_frame.pack(padx=20, pady=10, fill="x")

    tk.Label(thread_frame, text="Thread", bg="#f4f6f9").grid(row=0, column=0)
    tk.Label(thread_frame, text="Size", bg="#f4f6f9").grid(row=0, column=2)

    thread_cb = ttk.Combobox(thread_frame, textvariable=thread_var,
                             values=get_threads(), state="readonly", width=25)
    thread_cb.grid(row=0, column=1, padx=10, pady=5)

    size_cb = ttk.Combobox(thread_frame, textvariable=size_var,
                           state="readonly", width=25)
    size_cb.grid(row=0, column=3, padx=10, pady=5)

    tk.Label(thread_frame, text="Available Qty", bg="#f4f6f9").grid(row=1, column=0)
    tk.Entry(thread_frame, textvariable=available_var,
             state="readonly", width=28).grid(row=1, column=1)

    tk.Label(thread_frame, text="Issued Qty", bg="#f4f6f9").grid(row=1, column=2)
    tk.Entry(thread_frame, textvariable=issued_var, width=28).grid(row=1, column=3)

    # ================= EVENTS =================
    def update_expected():
        try:
            d = datetime.strptime(date_var.get(), "%Y-%m-%d")
            expected_var.set((d + timedelta(days=6)).strftime("%Y-%m-%d"))
        except:
            expected_var.set("")

    def on_thread_select(e):
        size_cb["values"] = get_sizes(thread_var.get())
        size_var.set("")
        available_var.set("")
        update_expected()

    def on_size_change(*args):
        stock_id = get_stock_in_id(thread_var.get(), size_var.get())
        if stock_id:
            available_var.set(get_available_stock(stock_id))
        else:
            available_var.set(0)
        update_expected()

    thread_cb.bind("<<ComboboxSelected>>", on_thread_select)
    size_var.trace("w", on_size_change)


    # ================= TOP INFO FRAME =================
    top_info_frame = tk.LabelFrame(scroll_frame, text="Basic Info",
                font=("Arial", 14, "bold"),bg="#f4f6f9", padx=20, pady=10)
    top_info_frame.pack(padx=20, pady=10, fill="x")

    top_fields = [
        ("Date", date_var),
        ("Batch ID", batch_var),
        ("Expected Return", expected_var),
        ("Sender", sender_var),
    ]

    for i, (label, var) in enumerate(top_fields):
        row = i // 2
        col = (i % 2) * 2

        tk.Label(top_info_frame, text=label, bg="#f4f6f9").grid(row=row, column=col, sticky="w")

        # ===== Date Picker for Date =====
        if label == "Date":
            ent = DateEntry(top_info_frame, textvariable=var,date_pattern="yyyy-mm-dd", width=25)
            ent.grid(row=row, column=col+1, padx=10, pady=5)

        # ===== Date Picker for Expected Return =====
        elif label == "Expected Return":
            ent = DateEntry(top_info_frame, textvariable=var,
                            date_pattern="yyyy-mm-dd", width=25)
            ent.grid(row=row, column=col+1, padx=10, pady=5)

        # ===== Batch ID =====
        elif label == "Batch ID":
            ent = tk.Entry(top_info_frame, textvariable=var,
                        width=28, bg="#ecf0f1", state="readonly")
            ent.grid(row=row, column=col+1, padx=10, pady=5)

        # ===== Normal Entry =====
        else:
            ent = tk.Entry(top_info_frame, textvariable=var,
                        width=28, bg="#ecf0f1")
            ent.grid(row=row, column=col+1, padx=10, pady=5)

    # ================= DYEING DETAILS FRAME =================
    bottom_info_frame = tk.LabelFrame(scroll_frame, text="Dyeing Details",
                font=("Arial", 14, "bold"),bg="#f4f6f9", padx=20, pady=10)
    bottom_info_frame.pack(padx=20, pady=10, fill="x")

    # ===== Dyeing Info =====
    tk.Label(bottom_info_frame, text="Dyeing Info", bg="#f4f6f9").grid(row=0, column=0, sticky="w")

    dyeing_text = tk.Text(bottom_info_frame, height=2, width=65, fg="gray")
    dyeing_text.grid(row=0, column=1, columnspan=4, padx=10, pady=5)
    dyeing_text.insert("1.0", "Enter dyeing details here...")

    # Bind focus events for placeholder
    def on_dyeing_focus_in(event):
        if dyeing_text.get("1.0", "end-1c") == "Enter dyeing details here...":
            dyeing_text.delete("1.0", tk.END)
            dyeing_text.config(fg="black")

    def on_dyeing_focus_out(event):
        if dyeing_text.get("1.0", "end-1c").strip() == "":
            dyeing_text.insert("1.0", "Enter dyeing details here...")
            dyeing_text.config(fg="gray")

    dyeing_text.bind("<FocusIn>", on_dyeing_focus_in)
    dyeing_text.bind("<FocusOut>", on_dyeing_focus_out)

    # ===== Reason =====
    tk.Label(bottom_info_frame, text="Reason", bg="#f4f6f9").grid(row=2, column=0, sticky="w")

    reason_text = tk.Text(bottom_info_frame, height=2, width=65,fg="gray")
    reason_text.grid(row=2, column=1, columnspan=4, padx=10, pady=5)
    reason_text.insert("1.0", "Enter reason for dyeing here...")

    # Bind focus events for placeholder
    def on_reason_focus_in(event):
        if reason_text.get("1.0", "end-1c") == "Enter reason for dyeing here...":
            reason_text.delete("1.0", tk.END)
            reason_text.config(fg="black")

    def on_reason_focus_out(event):
        if reason_text.get("1.0", "end-1c").strip() == "":
            reason_text.insert("1.0", "Enter reason here...")
            reason_text.config(fg="gray")

    reason_text.bind("<FocusIn>", on_reason_focus_in)
    reason_text.bind("<FocusOut>", on_reason_focus_out)

    # ===== Receiver =====
    tk.Label(bottom_info_frame, text="Receiver", bg="#f4f6f9").grid(row=4, column=0, sticky="w")

    tk.Entry(bottom_info_frame, textvariable=receiver_var,
            width=28, bg="#ecf0f1").grid(row=4, column=1, padx=10, pady=5)

    # ================= SAVE =================
    def save_data():

        if not thread_var.get() or not size_var.get():
            messagebox.showerror("Error", "Select thread & size")
            return
        try:
            issued = int(issued_var.get())
        except:
            messagebox.showerror("Error", "Invalid quantity")
            return

        available = int(available_var.get() or 0)

        if issued > available:
            messagebox.showerror("Stock Error", f"Available: {available}")
            return

        stock_id = get_stock_in_id(thread_var.get(), size_var.get())

        # Get text from Text widgets
        dyeing_text_content = dyeing_text.get("1.0", tk.END).strip()
        reason_text_content = reason_text.get("1.0", tk.END).strip()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO send_dyeing
            (batch_id, date, expected_return_date, stock_in_id,
             thread_name, size, issued_quantity,
             dyeing_info, reason_for_issue,
             sender, receiver)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            batch_var.get(),
            date_var.get(),
            expected_var.get(),
            stock_id,
            thread_var.get(),
            size_var.get(),
            issued,
            dyeing_text_content,
            reason_text_content,
            sender_var.get(),
            receiver_var.get()
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Saved Successfully")
        clear_form()

    # ================= CLEAR =================
    def clear_form():
        thread_var.set("")
        size_var.set("")
        issued_var.set("")
        dyeing_var.set("")
        reason_var.set("")
        sender_var.set("")
        receiver_var.set("")
        batch_var.set(generate_batch_id())
        expected_var.set("")
        
        # Clear Text widgets (Dyeing Info & Reason)
        dyeing_text.delete("1.0", tk.END)
        reason_text.delete("1.0", tk.END)

    def back_to_previous():
        if back_callback:
            back_callback()

    # ================= BUTTONS =================
    btn_frame = tk.Frame(scroll_frame, bg="#f4f6f9")
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="💾\nSave", command=save_data,font=("Segoe UI",12,"bold"),
              bg="#146c34", fg="#ffffff", width=8, height=2).grid(row=0, column=0, padx=20)

    tk.Button(btn_frame, text="🧹\nClear", command=clear_form,font=("Segoe UI",12,"bold"),
              bg="#c9660c", fg="#ffffff", width=8, height=2).grid(row=0, column=1, padx=20)

    tk.Button(btn_frame, text="📋\nView List",
              command=lambda: open_send_dyeing_list(win, lambda: open_send_dyeing(win, back_callback)),font=("Segoe UI",12,"bold"),
              bg="#1b4fbf", fg="#ffffff", width=8, height=2).grid(row=0, column=2, padx=20)

    tk.Button(btn_frame,text="⬅ Back",command=back_to_previous,bg="#34495e",
            fg="white",font=("Segoe UI", 12, "bold"),width=8,height=2,relief="flat",
            cursor="hand2").grid(row=0, column=3, padx=10)
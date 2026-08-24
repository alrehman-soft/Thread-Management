import tkinter as tk
from tkinter import messagebox
from database import get_connection
from datetime import datetime
from stock_in_list import open_stock_in_list

# ================= AUTO PO NUMBER =================
def generate_po_number():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM stock_in")
        result = cursor.fetchone()

        count = result["total"] + 1 if result else 1
        return f"PO-{count:04d}"
    finally:
        conn.close()

def open_stock_in(prefill_thread=None, prefill_size=None):
    win = tk.Toplevel()
    win.title("Stock In")
    win.geometry("800x600")
    win.config(bg="#f4f6f9")

    tk.Label(win, text="➕ Add New Thread", font=("Arial", 18, "bold"),
             bg="#f4f6f9").pack(pady=10)

    # VARIABLES
    po = tk.StringVar(value=generate_po_number())
    date = tk.StringVar()
    supplier = tk.StringVar()
    phone = tk.StringVar()
    email = tk.StringVar()
    cnic = tk.StringVar()
    company = tk.StringVar()
    thread = tk.StringVar(value=prefill_thread or "")
    size = tk.StringVar(value=prefill_size or "")
    qty = tk.IntVar()
    price = tk.DoubleVar()
    total = tk.DoubleVar()
    paid = tk.DoubleVar()
    balance = tk.DoubleVar()

    date.set(datetime.today().strftime("%Y-%m-%d"))

    # AUTO CALCULATE TOTAL & BALANCE
    def update_total(*args):
        try:
            t = qty.get() * price.get()
            total.set(round(t,2))
            balance.set(round(total.get() - paid.get(),2))
        except:
            total.set(0)
            balance.set(0)

    def update_balance(*args):
        try:
            balance.set(round(total.get() - paid.get(),2))
        except:
            balance.set(0)

    qty.trace("w", update_total)
    price.trace("w", update_total)
    paid.trace("w", update_balance)

    # =========================
    # SUPPLIER DETAILS SECTION
    # =========================
    supplier_frame = tk.LabelFrame(win, text="Supplier Details", font=("Arial",14,"bold"),
                                   bg="#f4f6f9", padx=20, pady=10)
    supplier_frame.pack(padx=20, pady=10, fill="x")

    s_fields = [
        ("PO #", po),
        ("Date", date),
        ("Supplier Name", supplier),
        ("Phone", phone),
        ("Email", email),
        ("CNIC", cnic),
        ("Company Name", company),
    ]

    # 2–3 columns layout
    for i, (label, var) in enumerate(s_fields):
        row = i // 3
        col = i % 3 * 2  # leave space for entry
        tk.Label(supplier_frame, text=label, bg="#f4f6f9").grid(row=row, column=col, sticky="w", pady=5)

        if label == "PO #":
            ent = tk.Entry(supplier_frame,textvariable=var,width=25,bg="#ecf0f1",state="readonly")
        else:
            ent = tk.Entry(supplier_frame,textvariable=var,width=25,bg="#ecf0f1")
        ent.grid(row=row, column=col+1, pady=5, padx=5)

        # Hover effect
        def on_enter(e, w=ent): w.config(bg="#d1f0ff")
        def on_leave(e, w=ent): w.config(bg="#ecf0f1")
        ent.bind("<Enter>", on_enter)
        ent.bind("<Leave>", on_leave)

    # THREAD DETAILS SECTION
    thread_frame = tk.LabelFrame(win, text="Thread Details", font=("Arial",14,"bold"),
                                 bg="#f4f6f9", padx=20, pady=10)
    thread_frame.pack(padx=20, pady=10, fill="x")

    t_fields = [
        ("Thread Name", thread),
        ("Size", size),
        ("Bundle Quantity", qty),
        ("Bundle Price", price),
        ("Total Price", total),
        ("Paid Amount", paid),
        ("Balance", balance),
    ]

    for i, (label, var) in enumerate(t_fields):
        row = i // 3
        col = i % 3 * 2
        tk.Label(thread_frame, text=label, bg="#f4f6f9").grid(row=row, column=col, sticky="w", pady=5)
        ent = tk.Entry(thread_frame, textvariable=var, width=25, bg="#ecf0f1")
        ent.grid(row=row, column=col+1, pady=5, padx=5)

        # Hover effect
        def on_enter(e, w=ent): w.config(bg="#d1f0ff")
        def on_leave(e, w=ent): w.config(bg="#ecf0f1")
        ent.bind("<Enter>", on_enter)
        ent.bind("<Leave>", on_leave)

        if label in ["Total Price","Balance"]:
            ent.config(state="readonly")

    # BUTTONS SECTION
    btn_frame = tk.Frame(win, bg="#f4f6f9")
    btn_frame.pack(pady=20)

    def save_data():
        if not po.get():
            messagebox.showerror("Error", "PO Number required")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM stock_in WHERE po_number=%s", (po.get(),))
            if cursor.fetchone():
                messagebox.showerror("Error", "PO already exists")
                return
            cursor.execute("""
                INSERT INTO stock_in (
                    po_number, date, supplier_name, phone, email, supplier_cnic,
                    company_name, thread_name, size, bundle_quantity,
                    bundle_price, paid_amount
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                po.get(), date.get(), supplier.get(), phone.get(), email.get(),
                cnic.get(), company.get(), thread.get(), size.get(),
                qty.get(), price.get(), paid.get()
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Thread Saved Successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form():
        po.set(generate_po_number())
        date.set(datetime.today().strftime("%Y-%m-%d"))
        supplier.set("")
        phone.set("")
        email.set("")
        cnic.set("")
        company.set("")
        thread.set("")
        size.set("")
        qty.set(0)
        price.set(0)
        paid.set(0)
        total.set(0)
        balance.set(0)

    buttons = [
        ("💾","Save",save_data,"#064B23"),
        ("🧹","Clear",clear_form,"#c0392b"),
        ("📋","Stock List",open_stock_in_list,"#2980b9")    ]

    for i, (icon,text,cmd,color) in enumerate(buttons):
        btn = tk.Button(
            btn_frame,
            text=f"{icon}\n{text}",
            command=cmd,
            font=("Arial",12,"bold italic"),
            fg="white",
            bg=color,
            activebackground="#34495e",
            activeforeground="white",
            width=8,
            height=3,
            relief="raised",
            bd=3,
            compound="top"
        )
        btn.grid(row=0,column=i,padx=20)
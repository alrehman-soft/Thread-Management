import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
import win32api, win32print

def open_supplier_detail():
    win = tk.Toplevel()
    win.title("Supplier Details")
    win.geometry("800x500")
    win.config(bg="#f4f6f9")

    tk.Label(win, text="📋 Supplier Details", font=("Arial", 18, "bold"),
             bg="#f4f6f9").pack(pady=10)

    # TREEVIEW
    columns = ("Supplier Name", "Phone", "Email", "CNIC", "Company Name")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # FETCH DATA FUNCTION
    def load_data():
        for row in tree.get_children():
            tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT supplier_name, phone, email, supplier_cnic, company_name
                FROM stock_in
            """)
            for supplier in cursor.fetchall():
                tree.insert("", "end", values=(
                    supplier['supplier_name'],
                    supplier['phone'],
                    supplier['email'],
                    supplier['supplier_cnic'],
                    supplier['company_name']
                ))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # BUTTONS
    btn_frame = tk.Frame(win, bg="#f4f6f9")
    btn_frame.pack(pady=10)

    def print_tree():
        slip = "===== SUPPLIER LIST =====\n\n"
        for row_id in tree.get_children():
            row = tree.item(row_id)['values']
            slip += f"Name: {row[0]}, Phone: {row[1]}, Email: {row[2]}, CNIC: {row[3]}, Company: {row[4]}\n"
        slip += "\n========================="

        preview = tk.Toplevel(win)
        preview.title("Print Preview")

        text = tk.Text(preview, width=100, height=30)
        text.pack()
        text.insert("1.0", slip)

        # Optional: send to printer
        try:
            filename = "supplier.txt"
            with open(filename, "w") as f:
                f.write(slip)
            win32api.ShellExecute(0,"print",filename,f'/d:"{win32print.GetDefaultPrinter()}"',".",0)
        except:
            pass 

    tk.Button(btn_frame, text="Refresh", command=load_data,bg="#1b4fbf",fg="white",
            font=("Segoe UI", 12, "bold"),width=9,height=1).grid(row=0, column=0, padx=10)

    tk.Button(btn_frame, text="Print", command=print_tree,bg="#c9660c",fg="white",
            font=("Segoe UI", 12, "bold"),width=9,height=1).grid(row=0, column=1, padx=10)

    load_data()
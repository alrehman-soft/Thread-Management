import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection, generate_so_number
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# CNIC Validation check
def validate_cnic(cnic):
    return len(cnic.strip()) == 13 and cnic.strip().isdigit()

def open_stock_out(win, back_command=None):
    for w in win.winfo_children():
        w.destroy()

    win.config(bg="#f4f6f9")

    header_frame = tk.Frame(win,bg="#f4f6f9")
    header_frame.pack(fill="x",pady=8)

    tk.Button(header_frame,text="← Back",command=back_command,bg="#34495e",fg="white",font=("Arial", 10, "bold"),width=10,height=2,relief="flat",cursor="hand2").pack(side="left",padx=20)

    tk.Label(header_frame,text="Add Stock Out Details",font=("Arial", 20, "bold"),bg="#f4f6f9",fg="#2c3e50").pack(side="left",padx=10)

    form_frame = tk.LabelFrame(win, text="Stock Out", font=("Arial", 12, "bold"),
                               bg="#f4f6f9", fg="#2c3e50")
    form_frame.pack(fill="x", padx=25, pady=5)

    so_number = tk.StringVar(master=win, value=generate_so_number())
    date = tk.StringVar(master=win, value=datetime.now().strftime("%Y-%m-%d"))
    customer_name = tk.StringVar(master=win)
    phone = tk.StringVar(master=win)
    email = tk.StringVar(master=win)
    customer_cnic = tk.StringVar(master=win)
    company_name = tk.StringVar(master=win)
    thread_name = tk.StringVar(master=win)
    size = tk.StringVar(master=win)
    color = tk.StringVar(master=win)
    bundle_quantity = tk.StringVar(master=win)
    available_quantity = tk.StringVar(master=win, value="0")
    issued_by = tk.StringVar(master=win)
    bundle_price = tk.StringVar(master=win)
    total_price = tk.StringVar(master=win,value="0.00")
    discount = tk.StringVar(master=win, value="0")
    final_total = tk.StringVar(master=win, value="0.00")

    fields = [
        ("SO Number:", so_number), ("Date:", date), ("Customer Name:", customer_name),
        ("Phone:", phone), ("Email:", email), ("Customer CNIC:", customer_cnic),
        ("Company Name:", company_name), ("Thread Name:", thread_name),
        ("Size:", size), ("Color:", color), ("Bundle Quantity:", bundle_quantity),
        ("Available Qty:", available_quantity), ("Issued By:", issued_by),
        ("Bundle Price:", bundle_price), ("Total Price:", total_price),
        ("Discount:", discount), ("Final Total:", final_total)
    ]

    entries = {}

    for i, (label, var) in enumerate(fields):
        row = i // 3
        col = (i % 3) * 2

        tk.Label(form_frame, text=label, bg="#f4f6f9",
                 font=("Arial", 10, "bold")).grid(
                     row=row, column=col, padx=(20, 8), pady=7, sticky="w"
                 )

        entry = tk.Entry(form_frame, textvariable=var, width=24, font=("Arial", 10))
        entry.grid(row=row, column=col + 1, padx=(0, 20), pady=7, sticky="w")
        entries[label] = entry

    for field in ["SO Number:", "Date:", "Available Qty:", "Total Price:", "Final Total:"]:
        entries[field].config(state="readonly")

    def get_available_quantity(thread, selected_size, selected_color, exclude_id=None):
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COALESCE(SUM(return_quantity), 0) AS returned
                FROM return_dyeing
                WHERE thread_name=%s AND size=%s AND color=%s
            """, (thread, selected_size, selected_color))

            returned = cursor.fetchone()["returned"] or 0

            if exclude_id:
                cursor.execute("""
                    SELECT COALESCE(SUM(bundle_quantity), 0) AS sold
                    FROM stock_out
                    WHERE thread_name=%s AND size=%s AND color=%s AND id != %s
                """, (thread, selected_size, selected_color, exclude_id))
            else:
                cursor.execute("""
                    SELECT COALESCE(SUM(bundle_quantity), 0) AS sold
                    FROM stock_out
                    WHERE thread_name=%s AND size=%s AND color=%s
                """, (thread, selected_size, selected_color))

            sold = cursor.fetchone()["sold"] or 0
            return max(0, returned - sold)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return 0
        finally:
            if conn:
                conn.close()

    def load_threads():
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT thread_name
                FROM return_dyeing
                WHERE thread_name IS NOT NULL AND thread_name != ''
                ORDER BY thread_name
            """)
            records = cursor.fetchall()
            thread_combo["values"] = [r["thread_name"] for r in records]
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def load_sizes(event=None):
        selected_thread = thread_name.get()

        size_combo["values"] = []
        color_combo["values"] = []
        size.set("")
        color.set("")
        available_quantity.set("0")

        if not selected_thread:
            return

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT size
                FROM return_dyeing
                WHERE thread_name=%s
                AND size IS NOT NULL
                AND size != ''
                ORDER BY size
            """, (selected_thread,))

            records = cursor.fetchall()
            size_combo["values"] = [r["size"] for r in records]

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def load_colors(event=None):
        selected_thread = thread_name.get()
        selected_size = size.get()

        color_combo["values"] = []
        color.set("")
        available_quantity.set("0")

        if not selected_thread or not selected_size:
            return

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT color
                FROM return_dyeing
                WHERE thread_name=%s
                AND size=%s
                AND color IS NOT NULL
                AND color != ''
                ORDER BY color
            """, (selected_thread, selected_size))

            records = cursor.fetchall()
            color_combo["values"] = [r["color"] for r in records]

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def update_available(event=None):
        if thread_name.get() and size.get() and color.get():
            qty = get_available_quantity(
                thread_name.get(),
                size.get(),
                color.get()
            )
            available_quantity.set(str(qty))
        else:
            available_quantity.set("0")

    thread_combo = ttk.Combobox(
        form_frame, textvariable=thread_name, width=21, state="readonly"
    )
    thread_combo.grid(row=2, column=3, padx=(0, 20), pady=7, sticky="w")
    entries["Thread Name:"].destroy()

    size_combo = ttk.Combobox(
        form_frame, textvariable=size, width=21, state="readonly"
    )
    size_combo.grid(row=2, column=5, padx=(0, 20), pady=7, sticky="w")
    entries["Size:"].destroy()

    color_combo = ttk.Combobox(
        form_frame, textvariable=color, width=21, state="readonly"
    )
    color_combo.grid(row=3, column=1, padx=(0, 20), pady=7, sticky="w")
    entries["Color:"].destroy()

    thread_combo.bind("<<ComboboxSelected>>", load_sizes)
    size_combo.bind("<<ComboboxSelected>>", load_colors)
    color_combo.bind("<<ComboboxSelected>>", update_available)

    def calculate_total(*args):
        try:
            qty = float(bundle_quantity.get() or 0)
            price = float(bundle_price.get() or 0)
            disc = float(discount.get() or 0)

            total = qty * price
            final = total - disc

            total_price.set(f"{total:.2f}")
            final_total.set(f"{max(0, final):.2f}")
        except ValueError:
            total_price.set("0.00")
            final_total.set("0.00")

    bundle_quantity.trace_add("write", calculate_total)
    bundle_price.trace_add("write", calculate_total)
    discount.trace_add("write", calculate_total)

    def clear_form():
        so_number.set(generate_so_number())
        date.set(datetime.now().strftime("%Y-%m-%d"))
        customer_name.set("")
        phone.set("")
        email.set("")
        customer_cnic.set("")
        company_name.set("")
        thread_name.set("")
        size.set("")
        color.set("")
        bundle_quantity.set("")
        available_quantity.set("0")
        issued_by.set("")
        bundle_price.set("")
        total_price.set("0.00")
        discount.set("0")
        final_total.set("0.00")
        size_combo["values"] = []
        color_combo["values"] = []
        load_threads()

    def save_record():
        try:
            qty = int(bundle_quantity.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Bundle Quantity must be a valid number."
            )
            return

        if not customer_name.get().strip():
            messagebox.showwarning("Required", "Please enter Customer Name.")
            return

        # === CNIC CHECK YAHAN ===
        cnic = customer_cnic.get().strip()
        if cnic and not validate_cnic(cnic):
            messagebox.showerror("Invalid CNIC", "CNIC must be exactly 13 digits.")
            return

        if not thread_name.get():
            messagebox.showwarning("Required", "Please select Thread Name.")
            return

        if not size.get():
            messagebox.showwarning("Required", "Please select Size.")
            return

        if not color.get():
            messagebox.showwarning("Required", "Please select Color.")
            return

        available = get_available_quantity(
            thread_name.get(),
            size.get(),
            color.get()
        )

        available_quantity.set(str(available))

        if qty > available:
            messagebox.showerror(
                "Stock Error",
                f"Available Quantity: {available}\n\nYou cannot issue {qty} bundles."
            )
            return

        try:
            price = float(bundle_price.get() or 0)
            disc = float(discount.get() or 0)

            if price < 0 or disc < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Amount",
                "Price and Discount must be valid numbers."
            )
            return

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO stock_out (
                    so_number, date, customer_name, phone, email,
                    customer_cnic, company_name, thread_name, size, color,
                    bundle_quantity, issued_by, bundle_price, discount
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                so_number.get(),
                date.get(),
                customer_name.get().strip(),
                phone.get().strip(),
                email.get().strip(),
                customer_cnic.get().strip(),
                company_name.get().strip(),
                thread_name.get(),
                size.get(),
                color.get(),
                qty,
                issued_by.get().strip(),
                price,
                disc
            ))

            conn.commit()
            messagebox.showinfo("Success", "Stock Out Saved Successfully ✅")
            load_records()
            clear_form()

        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    button_frame = tk.Frame(form_frame, bg="#f4f6f9")
    button_frame.grid(row=6, column=0, columnspan=6, pady=12, sticky="n", padx=170)

    tk.Button(
        button_frame, text="💾 Save Record", command=save_record,
        bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"),
        width=14, height=1, cursor="hand2").pack(side="left", padx=8)

    tk.Button(
        button_frame, text="🧹 Clear", command=clear_form,
        bg="#f99d09", fg="white", font=("Segoe UI", 11, "bold"),
        width=12, height=1, cursor="hand2").pack(side="left", padx=8)


    # Bottom Record Frame
    list_frame = tk.LabelFrame(win, text="Stock Out Records", font=("Arial", 12, "bold"),bg="#f4f6f9", fg="#2c3e50")
    list_frame.pack(fill="both", expand=True, padx=25, pady=5)

    action_frame = tk.Frame(list_frame, bg="#f4f6f9")
    action_frame.pack(fill="x", pady=8)

    tree_frame = tk.Frame(list_frame, bg="#f4f6f9")
    tree_frame.pack(fill="both", expand=True, padx=8, pady=8)

    cols = (
        "SO Number", "Date", "Customer", "Company", "Thread",
        "Size", "Color", "Qty", "Issued By", "Price",
        "Total", "Discount", "Final Total"
    )

    tree = ttk.Treeview(tree_frame, columns=cols, show="headings")

    widths = {
        "SO Number": 90, "Date": 90, "Customer": 130,
        "Company": 120, "Thread": 100, "Size": 70,
        "Color": 90, "Qty": 60, "Issued By": 100,
        "Price": 80, "Total": 90, "Discount": 80,
        "Final Total": 100
    }

    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=widths[col], anchor="center", minwidth=60)

    v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)

    tree.configure(
        yscrollcommand=v_scroll.set,
        xscrollcommand=h_scroll.set
    )

    tree.grid(row=0, column=0, sticky="nsew")
    v_scroll.grid(row=0, column=1, sticky="ns")
    h_scroll.grid(row=1, column=0, sticky="ew")

    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    def load_records():
        for item in tree.get_children():
            tree.delete(item)

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, so_number, date, customer_name, company_name,
                thread_name, size, color, bundle_quantity, issued_by,
                bundle_price, total_bundle_price, discount,final_total_price
                FROM stock_out ORDER BY id ASC
            """)

            records = cursor.fetchall()

            for r in records:
                tree.insert(
                    "",
                    "end",
                    iid=str(r["id"]),
                    values=(
                        r["so_number"],
                        r["date"],
                        r["customer_name"] or "",
                        r["company_name"] or "",
                        r["thread_name"] or "",
                        r["size"] or "",
                        r["color"] or "",
                        r["bundle_quantity"],
                        r["issued_by"] or "",
                        r["bundle_price"],
                        r["total_bundle_price"],
                        r["discount"],
                        r["final_total_price"]
                    )
                )

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def delete_record():
        selected = tree.focus()

        if not selected:
            messagebox.showwarning("Warning", "Please select a record.")
            return

        values = tree.item(selected)["values"]
        so = values[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n\nSO Number: {so}?"
        )

        if not confirm:
            return

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stock_out WHERE id=%s", (int(selected),))
            conn.commit()

            messagebox.showinfo(
                "Success",
                "Stock Out Deleted Successfully ✅"
            )

            load_records()
            update_available()

        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Delete Error", str(e))
        finally:
            if conn:
                conn.close()

    def print_record():
        selected = tree.focus()

        if not selected:
            messagebox.showwarning("Warning", "Please select a record to print.")
            return

        rec_id = int(selected)
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stock_out WHERE id=%s", (rec_id,))
            data = cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return
        finally:
            if conn:
                conn.close()

        if not data:
            messagebox.showerror("Error", "Record not found.")
            return

        so_number = data["so_number"]
        filename = f"Stock_Out_{so_number}.pdf"
        pdf_path = os.path.abspath(filename)

        try:
            pdf = canvas.Canvas(pdf_path, pagesize=A4)
            page_width, page_height = A4

            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images/company_logo.jpeg")

            if os.path.exists(logo_path):
                try:
                    logo = ImageReader(logo_path)
                    pdf.drawImage(logo, 40, page_height - 100, width=65, height=65, preserveAspectRatio=True, mask="auto")
                except Exception:
                    pass

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawString(120, page_height - 55, "RASHID BROTHERS")

            pdf.setFont("Helvetica", 10)
            pdf.drawString(120, page_height - 73, "Manufacturer Of Leather & Leather Goods")
            pdf.setFillColorRGB(0, 0, 0)

            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawRightString(page_width - 40, page_height - 50, "+92-21-35116818")
            pdf.drawRightString(page_width - 40, page_height - 65, "rashidbrothers371@gmail.com")
            pdf.drawRightString(page_width - 40, page_height - 80, "Karachi, Pakistan")

            pdf.setFillColorRGB(0, 0, 0)
            pdf.setLineWidth(1)
            pdf.line(40, page_height - 115, page_width - 40, page_height - 115)

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 18)
            pdf.drawCentredString(page_width / 2, page_height - 155, "STOCK OUT INVOICE")
            pdf.setFillColorRGB(0,0,0)

            y = page_height - 195

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(40, y, "SO Number:")
            pdf.setFillColorRGB(0,0,0)
            pdf.setFont("Helvetica", 11)
            pdf.drawString(125, y, str(data["so_number"]))

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(430, y, "Date:")
            pdf.setFillColorRGB(0,0,0)
            pdf.setFont("Helvetica", 11)
            pdf.drawString(470, y, str(data["date"]))

            y -= 40
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(40, y, "Customer Details")
            pdf.setFillColorRGB(0,0,0)

            y -= 20

            customer_details = [
                ("Customer Name:", data["customer_name"]),
                ("Company Name:", data["company_name"]),
                ("Phone:", data["phone"]),
                ("Email:", data["email"]),
                ("Customer CNIC:", data["customer_cnic"])
            ]

            box_top = y + 15
            box_bottom = y - (len(customer_details) * 22 + 10)

            pdf.rect(40, box_bottom, page_width - 80, box_top - box_bottom)

            y -= 5

            for label, value in customer_details:
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(55, y, label)
                pdf.setFont("Helvetica", 10)
                pdf.drawString(155, y, str(value or "N/A"))
                y -= 22

            y = box_bottom - 30
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(40, y, "Stock Out Details")
            pdf.setFillColorRGB(0,0,0)
            y -= 25

            table_top = y + 15
            table_bottom = y - 90

            pdf.rect(40, table_bottom, page_width - 80, table_top - table_bottom)

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(55, y, "Thread")
            pdf.drawString(155, y, "Size")
            pdf.drawString(220, y, "Color")
            pdf.drawString(295, y, "Bundle Qty")
            pdf.drawString(375, y, "Bundle Price")
            pdf.drawString(465, y, "Total Price")
            pdf.setFillColorRGB(0,0,0)

            pdf.line(50, y - 10, page_width - 50, y - 10)

            y -= 30

            pdf.setFont("Helvetica", 10)
            pdf.drawString(55, y, str(data["thread_name"] or "N/A"))
            pdf.drawString(155, y, str(data["size"] or "N/A"))
            pdf.drawString(220, y, str(data["color"] or "N/A"))
            pdf.drawString(295, y, str(data["bundle_quantity"] or "0"))
            pdf.drawString(375, y, f'{float(data["bundle_price"] or 0):.2f}')
            pdf.drawString(465, y, f'{float(data["total_bundle_price"] or 0):.2f}')

            y -= 35
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(55, y, "Discount:")
            pdf.setFillColorRGB(0,0,0)

            pdf.setFont("Helvetica", 10)
            pdf.drawString(155, y, f'{float(data["discount"] or 0):.2f}')

            y = table_bottom - 25

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawRightString(page_width - 160, y, "FINAL TOTAL:")
            pdf.setFillColorRGB(0,0,0)

            pdf.drawRightString(page_width - 55, y, f'{float(data["final_total_price"] or 0):.2f}')

            y -= 45

            # ISSUED BY + SIGNATURE
            pdf.setFont("Helvetica-Bold", 10)

            # Footer se thora sa upar
            signature_y = 105

            # Issued By - LEFT
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.drawString(40, signature_y, "Issued By:")
            pdf.setFillColorRGB(0,0,0)

            pdf.setFont("Helvetica", 10)
            pdf.drawString(105, signature_y, str(data["issued_by"] or "N/A"))

            # Signature - RIGHT
            pdf.setFont("Helvetica-Bold", 10)
            pdf.setLineWidth(1)
            pdf.line(page_width - 150,signature_y + 12,page_width - 45,signature_y + 12)

            # Signature text BELOW the line
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawCentredString(page_width - 97,signature_y - 5,"Signature")
            pdf.setFillColorRGB(0,0,0)

            # FOOTER
            pdf.line(40, 80, page_width - 40, 80)

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawCentredString(page_width / 2, 60, "RASHID BROTHERS")

            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawCentredString(page_width / 2, 45, "Plot # ST-371 SECTOR 7/A, Korangi Industrial Area, Karachi")
            pdf.save()

            messagebox.showinfo("PDF Created", f"Stock Out Invoice created successfully.\n\n{pdf_path}")
            os.startfile(pdf_path)

        except Exception as e:
            messagebox.showerror("Print Error", str(e))

    # EDIT FUNCTION
    def edit_record():
        selected = tree.focus()

        if not selected:
            messagebox.showwarning("Warning", "Please select a record.")
            return

        rec_id = int(selected)
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stock_out WHERE id=%s", (rec_id,))
            data = cursor.fetchone()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return
        finally:
            if conn:
                conn.close()

        if not data:
            messagebox.showerror("Error", "Record not found.")
            return

        edit_win = tk.Toplevel(win)
        edit_win.title("Edit Stock Out")
        edit_win.geometry("650x700")
        edit_win.config(bg="#f4f6f9")

        variables = {}

        edit_fields = [
            ("SO Number", data["so_number"]),
            ("Date", data["date"]),
            ("Customer Name", data["customer_name"] or ""),
            ("Phone", data["phone"] or ""),
            ("Email", data["email"] or ""),
            ("Customer CNIC", data["customer_cnic"] or ""),
            ("Company Name", data["company_name"] or ""),
            ("Thread Name", data["thread_name"] or ""),
            ("Size", data["size"] or ""),
            ("Color", data["color"] or ""),
            ("Bundle Quantity", data["bundle_quantity"]),
            ("Issued By", data["issued_by"] or ""),
            ("Bundle Price", data["bundle_price"]),
            ("Discount", data["discount"])
        ]

        for i, (label, value) in enumerate(edit_fields):
            var = tk.StringVar(value=str(value))
            variables[label] = var

            tk.Label(
                edit_win,
                text=label + ":",
                bg="#f4f6f9",
                font=("Arial", 10, "bold")
            ).grid(row=i, column=0, padx=20, pady=7, sticky="w")

            entry = tk.Entry(edit_win,textvariable=var,width=40)
            entry.grid(row=i, column=1, padx=20, pady=7)

            if label in ["SO Number", "Date"]:
                entry.config(state="readonly")

        def update_record():
            try:
                new_qty = int(variables["Bundle Quantity"].get())

                if new_qty <= 0:
                    raise ValueError

                new_price = float(variables["Bundle Price"].get() or 0)
                new_discount = float(variables["Discount"].get() or 0)

                if new_price < 0 or new_discount < 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror("Invalid Data","Quantity, Price and Discount must be valid.")
                return

            if not variables["Customer Name"].get().strip():
                messagebox.showwarning("Required","Please enter Customer Name.")
                return

            cnic = variables["Customer CNIC"].get().strip()
            if cnic and not validate_cnic(cnic):
                messagebox.showerror("Invalid CNIC", "CNIC must be exactly 13 digits.")
                return

            if not variables["Thread Name"].get().strip():
                messagebox.showwarning("Required","Please enter Thread Name.")
                return

            if not variables["Size"].get().strip():
                messagebox.showwarning("Required","Please enter Size.")
                return

            if not variables["Color"].get().strip():
                messagebox.showwarning("Required","Please enter Color.")
                return

            conn = None

            try:
                conn = get_connection()
                cursor = conn.cursor()

                available = get_available_quantity(
                    variables["Thread Name"].get().strip(),
                    variables["Size"].get().strip(),
                    variables["Color"].get().strip(),
                    rec_id
                )

                if new_qty > available:
                    messagebox.showerror(
                        "Stock Error",
                        f"Available Quantity: {available}\n\n"
                        f"You cannot issue {new_qty} bundles."
                    )
                    return

                cursor.execute("""
                    UPDATE stock_out
                    SET customer_name=%s,
                        phone=%s,
                        email=%s,
                        customer_cnic=%s,
                        company_name=%s,
                        thread_name=%s,
                        size=%s,
                        color=%s,
                        bundle_quantity=%s,
                        issued_by=%s,
                        bundle_price=%s,
                        discount=%s
                    WHERE id=%s
                """, (
                    variables["Customer Name"].get().strip(),
                    variables["Phone"].get().strip(),
                    variables["Email"].get().strip(),
                    variables["Customer CNIC"].get().strip(),
                    variables["Company Name"].get().strip(),
                    variables["Thread Name"].get().strip(),
                    variables["Size"].get().strip(),
                    variables["Color"].get().strip(),
                    new_qty,
                    variables["Issued By"].get().strip(),
                    new_price,
                    new_discount,
                    rec_id
                ))

                conn.commit()

                messagebox.showinfo(
                    "Success",
                    "Stock Out Updated Successfully ✅"
                )

                edit_win.destroy()
                load_records()
                update_available()

            except Exception as e:
                if conn:
                    conn.rollback()
                messagebox.showerror("Update Error", str(e))
            finally:
                if conn:
                    conn.close()

        # Buttons in edit window
        tk.Button(edit_win,text="💾 Update",command=update_record,bg="#27ae60",
            fg="white",font=("Arial", 10, "bold"),width=15,height=2,cursor="hand2"
            ).grid(row=len(edit_fields) + 1, column=0, pady=20)

        tk.Button(edit_win,text="❌ Cancel",command=edit_win.destroy,bg="#c0392b",
            fg="white",font=("Arial", 10, "bold"),width=15,height=2,cursor="hand2"
            ).grid(row=len(edit_fields) + 1, column=1, pady=20)

    
    # Stock Out Records Buttons
    tk.Button(action_frame,text="Edit",command=edit_record,bg="#e68e00",
        fg="white",font=("Segoe UI", 11, "bold"),width=10,height=1,cursor="hand2").pack(side="left", padx=8)

    tk.Button(action_frame,text="Delete",command=delete_record,bg="#c0392b",
        fg="white",font=("Segoe UI", 11, "bold"),width=10,height=1,cursor="hand2").pack(side="left", padx=8)

    tk.Button(action_frame,text="Refresh",command=load_records,bg="#2980b9",fg="white",
        font=("Segoe UI", 11, "bold"),width=10,height=1,cursor="hand2").pack(side="left", padx=8)

    tk.Button(action_frame,text="Print",command=print_record,bg="#0c0a41",
    fg="white",font=("Segoe UI", 11, "bold"),width=10,height=1,relief="flat",
    cursor="hand2").pack(side="left",padx=8)

    load_threads()
    load_records()
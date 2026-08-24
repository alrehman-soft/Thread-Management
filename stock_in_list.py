import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def open_stock_in_list():
    win = tk.Toplevel()
    win.title("Stock In Records")
    win.geometry("1250x600")
    win.config(bg="#f4f6f9")

    tk.Label(win, text="📋 Stock In Records", font=("Arial", 18, "bold"),
             bg="#f4f6f9").pack(pady=10)

    # BUTTONS AT TOP
    btn_frame = tk.Frame(win, bg="#f4f6f9")
    btn_frame.pack(side="top", fill="x", pady=10)

    # TREEVIEW FRAME
    tree_frame = tk.Frame(win)
    tree_frame.pack(side="top", fill="both", expand=True, padx=20, pady=10)

    columns = [
        "po_number","date","supplier_name","phone","email","cnic","company_name",
        "thread_name","size","bundle_quantity","bundle_price","total_price","paid_amount","balance"
    ]

    # Treeview ko grid me rakhen
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")  # sticky se expand hoga

    # Vertical & horizontal scrollbars
    v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)

    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    # Scrollbars ko grid me place karen
    v_scroll.grid(row=0, column=1, sticky="ns")
    h_scroll.grid(row=1, column=0, sticky="ew")

    # Grid configure for expansion
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    # Headings
    headings = [
        "PO #","Date","Supplier","Phone","Email","CNIC","Company",
        "Thread","Size","Qty","Price","Total","Paid","Balance"
    ]
    for col, hd in zip(columns, headings):
        tree.heading(col, text=hd)
        tree.column(col, width=90, anchor="center")

    # FUNCTIONS
    def load_data():
        for item in tree.get_children():
            tree.delete(item)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stock_in ORDER BY po_number ASC")
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", "end", values=(
                    row["po_number"], row["date"], row["supplier_name"], row["phone"], row["email"],
                    row["supplier_cnic"], row["company_name"], row["thread_name"], row["size"],
                    row["bundle_quantity"], row["bundle_price"], row["total_price"], row["paid_amount"], row["balance"]
                ))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_selected():
        selected = tree.selection()

        if not selected:
            messagebox.showerror("Error", "Select a record to edit")
            return

        # Selected row
        item = tree.item(selected[0])["values"]
        po_number = item[0]

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM stock_in WHERE po_number=%s LIMIT 1",
                (po_number,)
            )

            full_data = cursor.fetchone()
            conn.close()

            if not full_data:
                messagebox.showerror("Error", "Record not found")
                return

            # ================= EDIT WINDOW =================
            edit_win = tk.Toplevel(win)
            edit_win.title(f"Edit PO # {full_data['po_number']}")
            edit_win.geometry("600x600")
            edit_win.config(bg="#f4f6f9")

            # ================= VARIABLES =================
            supplier = tk.StringVar(value=full_data["supplier_name"] or "")
            phone = tk.StringVar(value=full_data["phone"] or "")
            email = tk.StringVar(value=full_data["email"] or "")
            cnic = tk.StringVar(value=full_data["supplier_cnic"] or "")
            company = tk.StringVar(value=full_data["company_name"] or "")
            thread = tk.StringVar(value=full_data["thread_name"] or "")
            size = tk.StringVar(value=full_data["size"] or "")
            quantity = tk.StringVar(value=full_data["bundle_quantity"] or "")
            price = tk.StringVar(value=full_data["bundle_price"] or "")
            paid = tk.StringVar(value=full_data["paid_amount"] or "")

            fields = [
                ("Supplier Name", supplier),
                ("Phone", phone),
                ("Email", email),
                ("CNIC", cnic),
                ("Company Name", company),
                ("Thread Name", thread),
                ("Size", size),
                ("Bundle Quantity", quantity),
                ("Bundle Price", price),
                ("Paid Amount", paid)
            ]

            # ================= FORM =================
            for i, (label, var) in enumerate(fields):

                tk.Label(edit_win,text=label,bg="#f4f6f9",font=("Arial", 10, "bold")
                ).grid(row=i,column=0,sticky="w",pady=8,padx=20)

                tk.Entry(edit_win,textvariable=var,width=35,font=("Arial", 10)
                ).grid(row=i,column=1,pady=8,padx=20)

            # ================= UPDATE =================
            def update_record():
                try:
                    new_quantity = int(quantity.get())
                    new_price = float(price.get())
                    new_paid = float(paid.get())

                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute(""" UPDATE stock_in SET
                            supplier_name=%s,
                            phone=%s,
                            email=%s,
                            supplier_cnic=%s,
                            company_name=%s,
                            thread_name=%s,
                            size=%s,
                            bundle_quantity=%s,
                            bundle_price=%s,
                            paid_amount=%s
                        WHERE po_number=%s
                    """, (
                        supplier.get(),
                        phone.get(),
                        email.get(),
                        cnic.get(),
                        company.get(),
                        thread.get(),
                        size.get(),
                        new_quantity,
                        new_price,
                        new_paid,
                        po_number
                    ))

                    conn.commit()
                    conn.close()

                    messagebox.showinfo("Success","Record updated successfully ✅")

                    edit_win.destroy()
                    load_data()

                except ValueError:messagebox.showerror("Invalid Data","Quantity, Price and Paid Amount must be numbers.")

                except Exception as e:messagebox.showerror("Error",str(e))

            # ================= BUTTON =================
            tk.Button(edit_win,text="💾 Update",command=update_record,font=("Arial", 12, "bold"),
                fg="white",bg="#27ae60",width=15).grid(row=len(fields),column=0,columnspan=2,pady=20)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected():
        selected = tree.selection()

        if not selected:
            messagebox.showerror("Error", "Select a record to delete")
            return

        item = tree.item(selected[0])["values"]

        # PO Number first column hai
        po_number = item[0]

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete PO # {po_number}?"
        ):
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # PO Number ke through record delete
            cursor.execute("DELETE FROM stock_in WHERE po_number=%s",(po_number,))

            conn.commit()

            # Check whether record actually deleted
            if cursor.rowcount == 0:
                conn.close()
                messagebox.showerror("Error","Record could not be deleted.")
                return
            conn.close()

            messagebox.showinfo("Deleted","Record deleted successfully ✅")

            load_data()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def print_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a record to print")
            return
        item = tree.item(selected[0])["values"]

        # Treeview Indexes
        po_number = item[0]
        date = item[1]
        supplier = item[2]
        phone = item[3]
        email = item[4]
        cnic = item[5]
        company = item[6]
        thread = item[7]
        size = item[8]
        quantity = item[9]
        price = item[10]
        total = item[11]
        paid = item[12]
        balance = item[13]

        # PDF FILE
        filename = f"Stock_In_{po_number}.pdf"
        pdf_path = os.path.abspath(filename)

        try:
            pdf = canvas.Canvas(pdf_path, pagesize=A4)

            page_width, page_height = A4

            # Header height
            header_height = 125

            # COMPANY LOGO
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                "images/company_logo.jpeg")

            if os.path.exists(logo_path):
                try:
                    logo = ImageReader(logo_path)
                    pdf.drawImage(logo,30,page_height - 90,width=65,height=65,
                        preserveAspectRatio=True,mask="auto")
                except Exception:
                    pass

            # COMPANY NAME
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawString(100,page_height - 58,"RASHID BROTHERS")

            pdf.setFont("Helvetica", 10)
            pdf.drawString(100,page_height - 76,"Manufacturer Of Leather & Leather Goods")

            # CONTACT DETAILS
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawRightString(page_width - 45,page_height - 50,"+92-21-35116818")

            pdf.drawRightString(page_width - 45,page_height - 65,"rashidbrothers371@gmail.com")

            pdf.drawRightString(page_width - 45,page_height - 80,"Karachi, Pakistan")

            # ================= HEADER BOTTOM LINE =================
            pdf.setLineWidth(1.5)
            pdf.setFillColorRGB(0,0,0)

            pdf.setLineWidth(1)
            pdf.line(40,page_height - 115,page_width - 40,page_height - 115)

            # DOCUMENT TITLE
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawCentredString(page_width / 2,page_height - 155,"STOCK IN RECEIPT")

            pdf.setFillColorRGB(0,0,0)

            # BASIC INFORMATION
            y = page_height - 200

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(50, y, "PO Number:")
            pdf.setFillColorRGB(0,0,0)

            pdf.setFont("Helvetica", 11)
            pdf.drawString(150, y, str(po_number))

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(420, y, "Date:")
            pdf.setFillColorRGB(0,0,0) 

            pdf.setFont("Helvetica", 11)
            pdf.drawString(470, y, str(date))

            y -= 35

            # SUPPLIER DETAILS
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(50, y, "Supplier Details")
            pdf.setFillColorRGB(0,0,0)

            y -= 25

            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(60, y, "Supplier Name:")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(160, y, str(supplier))

            y -= 22

            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(60, y, "Phone:")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(160, y, str(phone))

            y -= 22

            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(60, y, "Email:")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(160, y, str(email))

            y -= 22

            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(60, y, "CNIC:")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(160, y, str(cnic))

            y -= 22

            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(60, y, "Company:")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(160, y, str(company))

            # THREAD DETAILS BOX
            y -= 40

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 13)
            pdf.drawString(50, y, "Thread Details")
            pdf.setFillColorRGB(0,0,0)

            y -= 25

            # Box
            box_top = y + 15
            box_bottom = y - 125

            pdf.rect(45,box_bottom,page_width - 90,box_top - box_bottom)

            # Headers
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 10)

            pdf.drawString(60, y, "Thread")
            pdf.drawString(180, y, "Size")
            pdf.drawString(250, y, "Quantity")
            pdf.drawString(340, y, "Price")
            pdf.drawString(430, y, "Total")
            pdf.setFillColorRGB(0,0,0)

            y -= 20
            
            pdf.setFont("Helvetica", 10)
            pdf.drawString(60, y, str(thread))
            pdf.drawString(180, y, str(size))
            pdf.drawString(250, y, str(quantity))
            pdf.drawString(340, y, str(price))
            pdf.drawString(430, y, str(total))

            # Horizontal line
            pdf.line(55, y - 10, page_width - 55, y - 10)

            y -= 40
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(60, y, "Total Amount:")
            pdf.setFillColorRGB(0,0,0)

            pdf.setFont("Helvetica", 10)
            pdf.drawString(180, y, str(total))

            y -= 25

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(60, y, "Paid Amount:")
            pdf.setFillColorRGB(0,0,0)

            pdf.setFont("Helvetica", 10)
            pdf.drawString(180, y, str(paid))

            y -= 25

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(60, y, "Balance:")
            pdf.setFillColorRGB(0,0,0)

            pdf.setFont("Helvetica", 10)
            pdf.drawString(180, y, str(balance))

            # FOOTER
            pdf.line(40,80,page_width - 40,80)

            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawCentredString(page_width / 2,60,"RASHID BROTHERS")

            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawCentredString(page_width / 2,45,"Plot # ST-371 SECTOR 7/A, Korangi Industrial Area, Karachi")
            pdf.setFillColorRGB(0,0,0)

            # SAVE PDF
            pdf.save()

            messagebox.showinfo("PDF Created",
                f"Supplier Detail created successfully.\n\n{pdf_path}")

            # Open PDF
            os.startfile(pdf_path)

        except Exception as e:
            messagebox.showerror("Print Error",str(e))

    # BUTTONS
    tk.Button(btn_frame, text="Edit", command=edit_selected,
              font=("Segoe UI",12,"bold"), fg="white", bg="#15984c", width=7, height=1).grid(row=0,column=0,padx=10)

    tk.Button(btn_frame, text="Delete", command=delete_selected,
              font=("Segoe UI",12,"bold"), fg="white", bg="#c0392b", width=7, height=1).grid(row=0,column=1,padx=10)

    tk.Button(btn_frame, text="Print", command=print_selected,
              font=("Segoe UI",12,"bold"), fg="white", bg="#2980b9",
              width=7, height=1,justify="center").grid(row=0,column=2,padx=10)

    tk.Button(btn_frame, text="Refresh", command=load_data,
          font=("Segoe UI",11,"bold"), fg="white", bg="#0b0b0a", width=7, height=1).grid(row=0,column=3,padx=10)

    # =========================
    # Load data initially
    # =========================
    load_data()
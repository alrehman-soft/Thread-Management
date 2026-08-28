import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os


def open_send_dyeing_list(win, back_callback=None):
    # CLEAR OLD PAGE
    for w in win.winfo_children():
        w.destroy()
    win.config(bg="#f4f6f9")

    # TITLE
    tk.Label(win,text="📋 Send Dyeing Records",font=("Segoe UI", 18, "bold"),
             bg="#f4f6f9",fg="#2c3e50").pack(pady=9)

    # TABLE FRAME
    frame = tk.Frame(win,bg="#f4f6f9")

    frame.pack(fill="both",expand=True,padx=20,pady=10)

    # TREEVIEW COLUMNS
    cols = ("Batch","Date","Expected Return","Thread","Size","Qty","Dyeing Info","Reason","Sender","Receiver")

    tree = ttk.Treeview(frame,columns=cols,show="headings",height=15)

    # COLUMN WIDTHS
    column_widths = {
        "Batch": 100,
        "Date": 100,
        "Expected Return": 120,
        "Thread": 120,
        "Size": 60,
        "Qty": 50,
        "Dyeing Info": 180,
        "Reason": 180,
        "Sender": 100,
        "Receiver": 100
    }

    for c in cols:
        tree.heading(c,text=c)
        tree.column(c,anchor="center",width=column_widths.get(c, 100),minwidth=70)

    # VERTICAL SCROLLBAR
    v_scroll = ttk.Scrollbar(frame,orient="vertical",command=tree.yview)

    # HORIZONTAL SCROLLBAR
    h_scroll = ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)

    # Connect scrollbars
    tree.configure(yscrollcommand=v_scroll.set,xscrollcommand=h_scroll.set)

    # GRID LAYOUT
    tree.grid(row=0,column=0,sticky="nsew")
    v_scroll.grid(row=0,column=1,sticky="ns")

    h_scroll.grid(row=1,column=0,sticky="ew")

    frame.grid_rowconfigure(0,weight=1)
    frame.grid_columnconfigure(0,weight=1)

    # LOAD DATA
    def load_data():
        # Clear old rows
        for item in tree.get_children():
            tree.delete(item)
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id,batch_id,date,expected_return_date,thread_name,size,
                issued_quantity,dyeing_info,reason_for_issue,sender,receiver
                FROM send_dyeing ORDER BY batch_id ASC
            """)
            records = cursor.fetchall()

            for r in records:
                dyeing_info = r["dyeing_info"] or "N/A"
                reason = r["reason_for_issue"] or "N/A"

                # Short text for table
                if len(dyeing_info) > 25:
                    dyeing_display = dyeing_info[:25] + "..."
                else:
                    dyeing_display = dyeing_info

                if len(reason) > 25:
                    reason_display = reason[:25] + "..."
                else:
                    reason_display = reason

                tree.insert("","end",
                    # ID is NOT displayed
                    values=(
                        r["batch_id"],
                        r["date"],
                        r["expected_return_date"] or "N/A",
                        r["thread_name"],
                        r["size"],
                        r["issued_quantity"],
                        dyeing_display,
                        reason_display,
                        r["sender"] or "N/A",
                        r["receiver"] or "N/A"
                    ),
                    # Store database ID secretly
                    iid=str(r["id"])
                )

        except Exception as e:
            messagebox.showerror("Database Error",str(e))
        finally:
            if conn:
                conn.close()

    # Initial load
    load_data()

    # EDIT RECORD
    def edit_record():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning","Please select a record.")
            return

        rec_id = int(selected)
        # Fetch complete record
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(""" SELECT * FROM send_dyeing WHERE id = %s""",(rec_id,))
            full_data = cursor.fetchone()

        except Exception as e:
            messagebox.showerror("Database Error",str(e))
            return
        finally:
            if conn:
                conn.close()

        if not full_data:
            messagebox.showerror("Error","Record not found.")
            return

        # EDIT WINDOW
        edit_win = tk.Toplevel(win)
        edit_win.title("Edit Send Dyeing Record")

        edit_win.geometry("650x720")
        edit_win.config(bg="#f4f6f9")

        # SCROLLABLE EDIT WINDOW
        edit_canvas = tk.Canvas(edit_win,bg="#f4f6f9",highlightthickness=0)
        edit_scrollbar = ttk.Scrollbar(edit_win,orient="vertical",command=edit_canvas.yview)

        scrollable_frame = tk.Frame(edit_canvas,bg="#f4f6f9")

        scrollable_frame.bind("<Configure>",lambda e: edit_canvas.configure(scrollregion=edit_canvas.bbox("all")))

        edit_canvas.create_window((0, 0),window=scrollable_frame,anchor="nw")

        edit_canvas.configure(yscrollcommand=edit_scrollbar.set)
        edit_canvas.pack(side="left",fill="both",expand=True)

        edit_scrollbar.pack(side="right",fill="y")

        # VARIABLES
        batch = tk.StringVar(value=full_data["batch_id"])
        date = tk.StringVar(value=full_data["date"])
        expected_return = tk.StringVar(value=full_data["expected_return_date"] or "")
        thread = tk.StringVar(value=full_data["thread_name"])
        size = tk.StringVar(value=full_data["size"])
        qty = tk.StringVar(value=full_data["issued_quantity"])
        dyeing_info = tk.StringVar(value=full_data["dyeing_info"] or "")
        reason = tk.StringVar(value=full_data["reason_for_issue"] or "")
        sender = tk.StringVar(value=full_data["sender"] or "")
        receiver = tk.StringVar(value=full_data["receiver"] or "")

        # EDIT TITLE
        tk.Label(scrollable_frame,text="✏️ Edit Send Dyeing Record",font=("Arial", 16, "bold"),
            bg="#f4f6f9",fg="#2c3e50").grid(row=0,column=0,columnspan=2,pady=20)

        # FIELDS
        fields = [
            ("Batch ID:", batch),
            ("Date:", date),
            ("Expected Return Date:", expected_return),
            ("Thread Name:", thread),
            ("Size:", size),
            ("Issued Quantity:", qty),
            ("Dyeing Info:", dyeing_info),
            ("Reason for Issue:", reason),
            ("Sender:", sender),
            ("Receiver:", receiver)
        ]
        entries = []

        for i, (label, var) in enumerate(fields, start=1):

            tk.Label(scrollable_frame,text=label,bg="#f4f6f9",font=("Arial", 10, "bold")
            ).grid(row=i,column=0,pady=10,padx=10,sticky="w")

            if label in ["Dyeing Info:","Reason for Issue:"]:
                text_widget = tk.Text(scrollable_frame,height=4,width=45,wrap="word")

                text_widget.insert("1.0",var.get())
                text_widget.grid(row=i,column=1,pady=10,padx=10)
                entries.append((var,text_widget,"text"))
            else:
                entry = tk.Entry(scrollable_frame,textvariable=var,width=45)
                entry.grid(row=i,column=1,pady=10,padx=10)
                entries.append((var,entry,"entry"))

        # UPDATE RECORD
        def update_record():
            conn = None
            try:
                # Get Text widget values
                for var, widget, widget_type in entries:
                    if widget_type == "text":
                        var.set(widget.get("1.0","end-1c").strip())

                # Validate quantity
                try:
                    new_qty = int(qty.get())
                    if new_qty <= 0:
                        messagebox.showerror("Invalid Quantity","Issued Quantity must be greater than 0.")
                        return
                except ValueError:
                    messagebox.showerror("Invalid Quantity","Issued Quantity must be a valid number.")
                    return

                conn = get_connection()
                cursor = conn.cursor()

                # Get old quantity and stock ID
                cursor.execute("""
                    SELECT issued_quantity,stock_in_id FROM send_dyeing WHERE id=%s """,(rec_id,))
                old_data = cursor.fetchone()

                if not old_data:
                    messagebox.showerror("Error","Original record not found.")
                    return

                old_qty = old_data["issued_quantity"]
                stock_id = old_data["stock_in_id"]

                # Check available stock
                from database import get_available_stock
                available = get_available_stock(stock_id)

                # Add old quantity back
                effective_available = (available + old_qty)
                if new_qty > effective_available:
                    messagebox.showerror("Stock Error",
                    f"Available Quantity: {effective_available}\n\n"
                    f"You cannot issue more than this quantity.")
                    return

                # UPDATE
                cursor.execute("""
                    UPDATE send_dyeing SET
                        batch_id=%s,
                        date=%s,
                        expected_return_date=%s,
                        thread_name=%s,
                        size=%s,
                        issued_quantity=%s,
                        dyeing_info=%s,
                        reason_for_issue=%s,
                        sender=%s,
                        receiver=%s
                    WHERE id=%s
                    """,(
                        batch.get().strip(),
                        date.get().strip(),
                        expected_return.get().strip() or None,
                        thread.get().strip(),
                        size.get().strip(),
                        new_qty,
                        dyeing_info.get().strip(),
                        reason.get().strip(),
                        sender.get().strip(),
                        receiver.get().strip(),
                        rec_id
                    )
                )
                conn.commit()
                messagebox.showinfo("Success","Record Updated Successfully ✅")
                edit_win.destroy()
                load_data()
            except Exception as e:
                if conn:
                    conn.rollback()
                messagebox.showerror("Error",str(e))
            finally:
                if conn:
                    conn.close()

        # EDIT BUTTONS
        btn_frame = tk.Frame(scrollable_frame,bg="#f4f6f9")
        btn_frame.grid(row=len(fields) + 2,column=0,columnspan=2,pady=25)

        tk.Button(btn_frame,text="💾 Update",command=update_record,bg="#27ae60",fg="white",
            font=("Arial", 10, "bold"),width=15,height=2).pack(side="left",padx=10)

        tk.Button(btn_frame,text="❌ Cancel",command=edit_win.destroy,bg="#e74c3c",
            fg="white",font=("Arial", 10, "bold"),width=15,height=2).pack(side="left",padx=10)

    # DELETE RECORD
    def delete_record():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning","Please select a record.")
            return
        rec_id = int(selected)

        # Get batch for confirmation
        values = tree.item(selected)["values"]
        batch_id = values[0]

        confirm = messagebox.askyesno("Confirm Delete",f"Are you sure you want to delete:\n\n"f"Batch ID: {batch_id}?")

        if not confirm:
            return
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""DELETE FROM send_dyeing WHERE id=%s""",(rec_id,))
            conn.commit()

            messagebox.showinfo("Success","Record Deleted Successfully ✅")
            load_data()

        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Delete Error",str(e))
        finally:
            if conn:
                conn.close()

    # REFRESH
    def refresh():
        load_data()
    # PRINT
    def print_record():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning","Please select a record to print.")
            return
        # Hidden database ID
        rec_id = int(selected)
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(""" SELECT * FROM send_dyeing WHERE id = %s """,(rec_id,))
            data = cursor.fetchone()

        except Exception as e:
            messagebox.showerror("Database Error",str(e))
            return
        finally:
            if conn:
                conn.close()
        if not data:
            messagebox.showerror("Error","Record not found.")
            return

        batch_id = data["batch_id"]
        filename = f"Send_Dyeing_{batch_id}.pdf"
        pdf_path = os.path.abspath(filename)

        try:
            pdf = canvas.Canvas(pdf_path,pagesize=A4)
            page_width, page_height = A4

            header_height = 125
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images/company_logo.jpeg")

            if os.path.exists(logo_path):
                try:
                    logo = ImageReader(logo_path)
                    pdf.drawImage(logo,30,page_height - 90,width=65,height=65,preserveAspectRatio=True,mask="auto")
                except Exception:
                    pass

            # Company Name
            pdf.setFillColorRGB(0,0,0)
            pdf.setFont("Helvetica-Bold",20)
            pdf.drawString(100,page_height - 58,"RASHID BROTHERS")
            pdf.setFont("Helvetica",10)

            pdf.drawString(100,page_height - 76,"Manufacturer Of Leather & Leather Goods")
            pdf.setFillColorRGB(0.05,0.20,0.45)

            # CONTACT DETAILS
            pdf.setFont("Helvetica-Bold",9)
            pdf.drawRightString(page_width - 45,page_height - 50,"+92-21-35116818")
            pdf.drawRightString(page_width - 45,page_height - 65,"rashidbrothers371@gmail.com")
            pdf.drawRightString(page_width - 45,page_height - 80,"Karachi, Pakistan")

            # HEADER BOTTOM LINE
            pdf.setFillColorRGB(0,0,0)
            pdf.setLineWidth(1)
            pdf.line(40,page_height - 115,page_width - 40,page_height - 115)

            # DOCUMENT TITLE
            pdf.setFillColorRGB(0.05,0.20,0.45)
            pdf.setFont("Helvetica-Bold",16)
            pdf.drawCentredString(page_width / 2,page_height - 155,"SEND TO DYEING RECEIPT")
            pdf.setFillColorRGB(0,0,0)

            # BASIC INFORMATION
            y = page_height - 200

            # Batch ID
            pdf.setFillColorRGB(0.05,0.20,0.45)
            pdf.setFont("Helvetica-Bold",11)

            pdf.drawString(50,y,"Batch ID:")
            pdf.setFillColorRGB(0,0,0)
            pdf.setFont("Helvetica",11)
            pdf.drawString(150,y,str(data["batch_id"]))

            # Date
            pdf.setFillColorRGB(0.05,0.20,0.45)
            pdf.setFont("Helvetica-Bold",11)
            pdf.drawString(420,y,"Date:")

            pdf.setFillColorRGB(0,0,0)
            pdf.setFont("Helvetica",11)
            pdf.drawString(470,y,str(data["date"]))

            # Expected Return
            y -= 35
            pdf.setFillColorRGB(0.05,0.20,0.45)
            pdf.setFont("Helvetica-Bold",11)

            pdf.drawString(50,y,"Expected Return:")
            pdf.setFillColorRGB(0,0,0)
            pdf.setFont("Helvetica",11)

            expected_return = (data["expected_return_date"]
                if data["expected_return_date"]
                else "Not Specified")
            pdf.drawString(150,y,str(expected_return))

            # DYEING DETAILS
            y -= 40

            pdf.setFillColorRGB(0.05,0.20,0.45)
            pdf.setFont("Helvetica-Bold",13)
            pdf.drawString(50,y,"Dyeing Details")
            pdf.setFillColorRGB(0,0,0)

            y -= 25

            # DETAILS BOX
            box_top = y + 15
            box_bottom = y - 130

            pdf.rect(45,box_bottom,page_width - 90,box_top - box_bottom)

            # TABLE HEADERS
            pdf.setFillColorRGB(0.05,0.20,0.45)
            pdf.setFont("Helvetica-Bold",10)
            pdf.drawString(60,y,"Thread")
            pdf.drawString(180,y,"Size")
            pdf.drawString(250,y,"Quantity")
            pdf.drawString(340,y,"Sender")
            pdf.drawString(450,y,"Receiver")
            pdf.setFillColorRGB(0,0,0)

            # RECORD VALUES
            y -= 20

            pdf.setFont("Helvetica",10)
            pdf.drawString(60,y,str(data["thread_name"] or "N/A"))
            pdf.drawString(180,y,str(data["size"] or "N/A"))
            pdf.drawString(250,y,str(data["issued_quantity"] or "0"))
            pdf.drawString(340,y,str(data["sender"] or "N/A"))
            pdf.drawString(450,y,str(data["receiver"] or "N/A"))

            # HORIZONTAL LINE
            pdf.line(55,y - 10,page_width - 55,y - 10)

            # DYEING INFORMATION
            y -= 40

            pdf.setFillColorRGB(0.05,0.20,0.45)
            pdf.setFont("Helvetica-Bold",10)
            pdf.drawString(60,y,"Dyeing Information:")
            pdf.setFillColorRGB(0,0,0)

            pdf.setFont("Helvetica",10)
            dyeing_info = (data["dyeing_info"]
                if data["dyeing_info"]
                else "N/A")

            # Limit long text
            dyeing_info = str(dyeing_info)
            if len(dyeing_info) > 75:
                dyeing_info = dyeing_info[:75] + "..."

            pdf.drawString(180,y,dyeing_info)

            # REASON FOR ISSUE
            y -= 25

            pdf.setFillColorRGB(0.05,0.20,0.45)
            pdf.setFont("Helvetica-Bold",10)
            pdf.drawString(60,y,"Reason for Issue:")
            pdf.setFillColorRGB(0,0,0)
            pdf.setFont("Helvetica",10)

            reason = (data["reason_for_issue"]
                if data["reason_for_issue"]
                else "N/A")
            
            reason = str(reason)

            if len(reason) > 75:
                reason = reason[:75] + "..."

            pdf.drawString(180,y,reason)

            # INCHARGE SIGNATURE FIELD
            pdf.setFillColorRGB(0, 0, 0)
            # Signature line
            pdf.line(page_width - 190,125,page_width - 45,125)

            # Signature label
            pdf.setFont("Helvetica-Bold",9)
            pdf.drawCentredString(page_width - 117,112,"Incharge Signature")

            # FOOTER
            pdf.line(40,80,page_width - 40,80)
            pdf.setFillColorRGB(0.05,0.20,0.45)
            pdf.setFont("Helvetica-Bold",12)
            pdf.drawCentredString(page_width / 2,60,"RASHID BROTHERS")
            pdf.setFont("Helvetica-Bold",9)
            pdf.drawCentredString(page_width / 2,45,"Plot # ST-371 SECTOR 7/A, Korangi Industrial Area, Karachi")
            pdf.setFillColorRGB(0,0,0)

            # SAVE PDF
            pdf.save()
            messagebox.showinfo("PDF Created", f"Send Dyeing Receipt created successfully.\n\n" f"{pdf_path}")

            os.startfile(pdf_path)
        except Exception as e:
            messagebox.showerror("Print Error",str(e))

    def back_to_send_dyeing():
        if back_callback:
            back_callback()

    # BUTTON FRAME
    btn_frame = tk.Frame(win,bg="#f4f6f9")
    btn_frame.pack(pady=15)

    # BUTTONS
    buttons = [("Edit",edit_record,"#f0a62e"),
            ("Delete",delete_record,"#c0392b"),
            ("Refresh",refresh,"#000000"),
            ("Print",print_record,"#1b4fbf"),
            ("Back",back_to_send_dyeing,"#34495e")]

    for i, (text, cmd, color) in enumerate(buttons):
        tk.Button(btn_frame,text=f"{text}",font=("Arial", 11, "bold"),command=cmd,
                    bg=color,fg="white",activebackground=color,activeforeground="white",
                    width=9,height=2,relief="flat",cursor="hand2").grid(row=0,column=i,padx=10)
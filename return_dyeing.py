import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from datetime import datetime

def open_return_dyeing(win, back_command=None):
    for widget in win.winfo_children():
        widget.destroy()
    win.config(bg="#f4f6f9")

    header_frame = tk.Frame(win,bg="#f4f6f9")
    header_frame.pack(fill="x",pady=8)

    tk.Button(header_frame,text="← Back",command=back_command,bg="#34495e",fg="white",font=("Arial", 10, "bold"),width=10,height=2,relief="flat",cursor="hand2").place(x=20, y=0)

    tk.Label(header_frame,text="Return From Dyeing Details",font=("Segoe UI", 20, "bold"),bg="#f4f6f9",fg="#1c275a").pack()

    main_frame = tk.Frame(win, bg="#f4f6f9")
    main_frame.pack(fill="both", expand=True, padx=25, pady=5)

    form_frame = tk.LabelFrame(main_frame,text=" Return Dyeing ",font=("Arial", 12, "bold"),
        bg="#f4f6f9",fg="#2c3e50",padx=12,pady=8)
    form_frame.pack(fill="x", pady=5)

    date_var = tk.StringVar(master=win,value=datetime.now().strftime("%Y-%m-%d"))
    batch_var = tk.StringVar(master=win)
    thread_var = tk.StringVar(master=win)
    size_var = tk.StringVar(master=win)
    color_var = tk.StringVar(master=win)
    issued_var = tk.StringVar(master=win,)
    returned_var = tk.StringVar(master=win)
    remaining_var = tk.StringVar(master=win)
    return_qty_var = tk.StringVar(master=win)
    dyeing_info_var = tk.StringVar(master=win)
    sender_var = tk.StringVar(master=win)
    receiver_var = tk.StringVar(master=win)

    selected_send_id = [None]

    def load_batches():
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT sd.id, sd.batch_id, sd.issued_quantity,
                COALESCE((SELECT SUM(rd.return_quantity)
                FROM return_dyeing rd
                WHERE rd.send_dyeing_id=sd.id),0) AS total_returned
                FROM send_dyeing sd
                ORDER BY sd.id DESC
            """)
            records = cursor.fetchall()
            batches = []

            for row in records:
                issued = row["issued_quantity"] or 0
                returned = row["total_returned"] or 0

                if issued - returned > 0:
                    batches.append(row["batch_id"])

            batch_combo["values"] = batches

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def load_batch_details(event=None):
        batch_id = batch_var.get().strip()

        if not batch_id:
            return
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT sd.id, sd.batch_id, sd.thread_name, sd.size,
                sd.issued_quantity, sd.dyeing_info, sd.sender, sd.receiver,
                COALESCE((SELECT SUM(rd.return_quantity)
                FROM return_dyeing rd
                WHERE rd.send_dyeing_id=sd.id),0) AS total_returned
                FROM send_dyeing sd
                WHERE sd.batch_id=%s
                LIMIT 1
            """, (batch_id,))

            row = cursor.fetchone()

            if not row:
                messagebox.showerror("Error", "Batch record not found.")
                return

            selected_send_id[0] = row["id"]

            issued = row["issued_quantity"] or 0
            returned = row["total_returned"] or 0
            remaining = issued - returned

            thread_var.set(row["thread_name"] or "")
            size_var.set(row["size"] or "")
            issued_var.set(str(issued))
            returned_var.set(str(returned))
            remaining_var.set(str(remaining))
            dyeing_info_var.set(row["dyeing_info"] or "")
            sender_var.set(row["sender"] or "")
            receiver_var.set(row["receiver"] or "")
            return_qty_var.set("")

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            if conn:
                conn.close()

    def create_field(parent, row, column, label, variable, readonly=True, width=22):
        tk.Label(parent,text=label,font=("Arial", 10, "bold"),bg="#f4f6f9"
        ).grid(row=row, column=column, sticky="w", padx=(8, 5), pady=5)

        entry = tk.Entry(parent,textvariable=variable,width=width,font=("Arial", 10))
        entry.grid(row=row, column=column + 1, sticky="ew", padx=(0, 12), pady=5)

        if readonly:
            entry.config(state="readonly")
        return entry

    for col in range(6):
        form_frame.grid_columnconfigure(col, weight=1)
    create_field(form_frame, 0, 0, "Date:", date_var)
    
    tk.Label(form_frame,text="Batch ID:",font=("Arial", 10, "bold"),bg="#f4f6f9"
    ).grid(row=0, column=2, sticky="w", padx=(8, 5), pady=5)

    batch_combo = ttk.Combobox(form_frame,textvariable=batch_var,width=20,
                               state="readonly",font=("Arial", 10))
    batch_combo.grid(row=0, column=3, sticky="ew", padx=(0, 12), pady=5)
    batch_combo.bind("<<ComboboxSelected>>", load_batch_details)

    create_field(form_frame, 0, 4, "Thread:", thread_var)

    create_field(form_frame, 1, 0, "Size:", size_var)
    create_field(form_frame, 1, 2, "Issued Qty:", issued_var)
    create_field(form_frame, 1, 4, "Already Returned:", returned_var)

    create_field(form_frame, 2, 0, "Remaining:", remaining_var)
    create_field(form_frame, 2, 2, "Return Qty:", return_qty_var, False)
    create_field(form_frame, 2, 4, "Dyeing Info:", dyeing_info_var)

    create_field(form_frame, 3, 0, "Sender:", sender_var)
    create_field(form_frame, 3, 2, "Receiver:", receiver_var)
    create_field(form_frame, 3, 4, "Color:", color_var, False)

    def clear_form():
        date_var.set(datetime.now().strftime("%Y-%m-%d"))
        batch_combo.set("")
        thread_var.set("")
        size_var.set("")
        color_var.set("")
        issued_var.set("")
        returned_var.set("")
        remaining_var.set("")
        return_qty_var.set("")
        dyeing_info_var.set("")
        sender_var.set("")
        receiver_var.set("")
        selected_send_id[0] = None
        batch_combo.focus_set()

    def save_return():
        if not batch_var.get().strip():
            messagebox.showwarning("Warning", "Please select a Batch ID.")
            return

        if not selected_send_id[0]:
            messagebox.showerror("Error", "Invalid Batch ID.")
            return

        if not color_var.get().strip():
            messagebox.showwarning("Required", "Please enter Color.")
            return

        try:
            return_qty = int(return_qty_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Return Quantity must be a valid number.")
            return

        if return_qty <= 0:
            messagebox.showerror("Invalid Quantity", "Return Quantity must be greater than 0.")
            return

        try:
            remaining = int(remaining_var.get())
            issued = int(issued_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity data.")
            return

        if return_qty > remaining:
            messagebox.showerror(
                "Quantity Error",
                f"Remaining Quantity: {remaining}\n\nYou cannot return {return_qty}."
            )
            return
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO return_dyeing
                (date, send_dyeing_id, batch_id, thread_name, size, color,
                issued_quantity, return_quantity, dyeing_info, sender, receiver)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                date_var.get(),
                selected_send_id[0],
                batch_var.get().strip(),
                thread_var.get().strip(),
                size_var.get().strip(),
                color_var.get().strip(),
                issued,
                return_qty,
                dyeing_info_var.get().strip(),
                sender_var.get().strip(),
                receiver_var.get().strip()
            ))

            new_remaining = remaining - return_qty
            status = "returned" if new_remaining == 0 else "partial"

            cursor.execute(
                "UPDATE send_dyeing SET status=%s WHERE id=%s",
                (status, selected_send_id[0])
            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                f"Return saved successfully! ✅\n\n"
                f"Batch ID: {batch_var.get()}\n"
                f"Returned: {return_qty}\n"
                f"Remaining: {new_remaining}"
            )

            clear_form()
            load_batches()
            load_records()

        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Save Error", str(e))

        finally:
            if conn:
                conn.close()

    button_frame = tk.Frame(form_frame, bg="#f4f6f9")
    button_frame.grid(row=4, column=0, columnspan=6, pady=8)

    tk.Button(button_frame,text="💾 Save Return",command=save_return,bg="#146c34",
        fg="white",font=("Segoe UI", 12, "bold"),width=14,height=1,relief="flat",cursor="hand2"
        ).pack(side="left", padx=8)

    tk.Button(button_frame,text="Clear",command=clear_form,bg="#c9660c",
        fg="white",font=("Segoe UI", 11, "bold"),width=14,height=1,relief="flat",
        cursor="hand2").pack(side="left", padx=8)

    list_frame = tk.LabelFrame(main_frame,text=" Return Dyeing Records ",
                font=("Arial", 12, "bold"),bg="#f4f6f9",fg="#2c3e50")
    list_frame.pack(fill="both", expand=True, pady=5)

    columns = ("Date","Batch ID","Thread","Size","Color","Issued","Returned","Dyeing Info","Sender","Receiver")

    tree_frame = tk.Frame(list_frame, bg="#f4f6f9")
    tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

    tree = ttk.Treeview(tree_frame,columns=columns,show="headings")

    widths = {
        "Date": 100,
        "Batch ID": 110,
        "Thread": 110,
        "Size": 80,
        "Color": 100,
        "Issued": 80,
        "Returned": 80,
        "Dyeing Info": 250,
        "Sender": 110,
        "Receiver": 110
    }

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col,width=widths[col],minwidth=70,anchor="center")

    v_scroll = ttk.Scrollbar(tree_frame,orient="vertical",command=tree.yview)
    h_scroll = ttk.Scrollbar(tree_frame,orient="horizontal",command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set,xscrollcommand=h_scroll.set)

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
                SELECT id, date, batch_id, thread_name, size, color,issued_quantity,
                return_quantity, dyeing_info,sender, receiver
                FROM return_dyeing ORDER BY id ASC
            """)
            records = cursor.fetchall()
            for row in records:
                info = row["dyeing_info"] or "N/A"

                if len(info) > 35:
                    info = info[:35] + "..."

                tree.insert("","end",iid=str(row["id"]),
                    values=(
                        row["date"],
                        row["batch_id"],
                        row["thread_name"] or "N/A",
                        row["size"] or "N/A",
                        row["color"] or "N/A",
                        row["issued_quantity"] or 0,
                        row["return_quantity"] or 0,
                        info,
                        row["sender"] or "N/A",
                        row["receiver"] or "N/A"
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
        record_id = int(selected)
        batch_id = values[1]
        return_qty = values[6]

        confirm = messagebox.askyesno("Confirm Delete",f"Delete this return record?\n\n"
            f"Batch ID: {batch_id}\n"f"Returned Quantity: {return_qty}")
        if not confirm:
            return
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT send_dyeing_id FROM return_dyeing WHERE id=%s",(record_id,))
            row = cursor.fetchone()

            if not row:
                messagebox.showerror("Error", "Record not found.")
                return
            send_id = row["send_dyeing_id"]

            cursor.execute("DELETE FROM return_dyeing WHERE id=%s",(record_id,))

            cursor.execute("""
                SELECT sd.issued_quantity,
                COALESCE((SELECT SUM(rd.return_quantity)
                FROM return_dyeing rd
                WHERE rd.send_dyeing_id=sd.id),0) AS total_returned
                FROM send_dyeing sd
                WHERE sd.id=%s
            """, (send_id,))

            send_data = cursor.fetchone()

            if send_data:
                issued = send_data["issued_quantity"]
                returned = send_data["total_returned"]
                remaining = issued - returned

                if remaining == issued:
                    status = "sent"
                elif remaining > 0:
                    status = "partial"
                else:
                    status = "returned"

                cursor.execute("UPDATE send_dyeing SET status=%s WHERE id=%s",(status, send_id))
            conn.commit()

            messagebox.showinfo("Success","Return record deleted successfully. ✅")

            load_records()
            load_batches()

        except Exception as e:
            if conn:
                conn.rollback()

            messagebox.showerror("Delete Error", str(e))

        finally:
            if conn:
                conn.close()

    record_buttons = tk.Frame(list_frame,bg="#f4f6f9")
    record_buttons.pack(pady=6)

    tk.Button(record_buttons,text="Delete",command=delete_record,bg="#c0392b",
        fg="white",font=("Segoe UI", 11, "bold"),width=10,height=1,relief="flat",cursor="hand2"
        ).pack(side="left", padx=8)

    tk.Button(record_buttons,text="Refresh",command=load_records,bg="#1b4fbf",
        fg="white",font=("Segoe UI", 11, "bold"),width=10,height=1,relief="flat",cursor="hand2"
        ).pack(side="left", padx=8)

    load_batches()
    load_records()
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection, get_available_stock
from stock_in import open_stock_in
from send_dyeing import open_send_dyeing
from return_dyeing import open_return_dyeing
from stock_out import open_stock_out
from supplier_detail import open_supplier_detail
from customer_detail import open_customer_detail
from report import open_reports
from ai_dashboard_integration import AIDashboard
from backup import create_backup, restore_backup


LOW_STOCK_THRESHOLD = 100

# COLOR / GRADIENT HELPERS
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def draw_vertical_gradient(canvas, width, height, color_start, color_end):
    canvas.delete("gradient")
    if width <= 0 or height <= 0:
        return
    r1, g1, b1 = hex_to_rgb(color_start)
    r2, g2, b2 = hex_to_rgb(color_end)
    steps = max(int(height), 1)
    for i in range(steps):
        r = int(r1 + (r2 - r1) * i / steps)
        g = int(g1 + (g2 - g1) * i / steps)
        b = int(b1 + (b2 - b1) * i / steps)
        canvas.create_line(0, i, width, i, fill=rgb_to_hex((r, g, b)), tags="gradient")
    canvas.tag_lower("gradient")


# DATA HELPERS
def fetch_dashboard_kpis():
    data = {
        "total_stock": 0,
        "available_stock": 0,
        "issued_outstanding": 0,
        "pending_orders": 0,
        "total_customers": 0,
        "dyeing_return": 0,
        "dyeing_pending": 0,
        "total_issued": 0,
        "total_sold": 0
    }
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Total Stock (from stock_in) - Total Received
        cursor.execute("SELECT COALESCE(SUM(bundle_quantity),0) AS q FROM stock_in")
        total_stock = cursor.fetchone()["q"]
        data["total_stock"] = total_stock

        # Total Issued to Dyeing
        cursor.execute("SELECT COALESCE(SUM(issued_quantity),0) AS q FROM send_dyeing")
        data["total_issued"] = cursor.fetchone()["q"]

        # Total Return from Dyeing
        cursor.execute("SELECT COALESCE(SUM(return_quantity),0) AS q FROM return_dyeing")
        data["dyeing_return"] = cursor.fetchone()["q"]

        # ✅ Total Sold from Stock Out
        cursor.execute("SELECT COALESCE(SUM(bundle_quantity),0) AS q FROM stock_out")
        data["total_sold"] = cursor.fetchone()["q"]

        # Dyeing Pending
        data["dyeing_pending"] = max(0, data["total_issued"] - data["dyeing_return"])
        
        # Issued Outstanding 
        data["issued_outstanding"] = data["dyeing_pending"]

        # ✅ AVAILABLE STOCK
        data["available_stock"] = max(0, total_stock - data["total_issued"] + data["dyeing_return"] - data["total_sold"])

        # Pending Orders
        cursor.execute("SELECT COUNT(*) AS c FROM stock_in WHERE balance > 0")
        data["pending_orders"] = cursor.fetchone()["c"]

        # Total Customers
        cursor.execute("""
            SELECT COUNT(DISTINCT customer_name) AS c FROM stock_out
            WHERE customer_name IS NOT NULL AND customer_name != ''
        """)
        data["total_customers"] = cursor.fetchone()["c"]

    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if conn:
            conn.close()
    return data

def fetch_low_stock_items(threshold=LOW_STOCK_THRESHOLD):
    """Aggregate available stock per thread+size (reuses database.get_available_stock)."""
    items = {}
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, thread_name, size FROM stock_in")
        rows = cursor.fetchall()
        conn.close()
        conn = None

        for r in rows:
            key = (r["thread_name"] or "N/A", r["size"] or "N/A")
            available = get_available_stock(r["id"])
            items[key] = items.get(key, 0) + available

    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if conn:
            conn.close()

    low_items = [{"thread": k[0], "size": k[1], "available": v}
                 for k, v in items.items() if v < threshold]
    low_items.sort(key=lambda x: x["available"])
    return low_items


def build_header(parent):
    header_h = 100
    outer = tk.Frame(parent, height=header_h)
    outer.pack(fill="x")
    outer.pack_propagate(False)

    canvas = tk.Canvas(outer, height=header_h, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # ✅ DATE/TIME LABEL - Global variable
    date_time_label = None
    after_id = None

    def update_date_time():
        nonlocal after_id
        try:
            # Check if widget still exists
            if date_time_label and date_time_label.winfo_exists():
                from datetime import datetime
                now = datetime.now()
                date_time_label.config(text=now.strftime("%d-%m-%Y  |  %I:%M:%S %p"))
                after_id = date_time_label.after(1000, update_date_time)
            else:
                # Widget destroyed
                after_id = None
        except tk.TclError:
        # Widget destroyed, stop the loop
            after_id = None
        except:
            after_id = None

    def redraw(event=None):
        nonlocal date_time_label, after_id
        w = canvas.winfo_width()

        draw_vertical_gradient(canvas, w, header_h, "#1b4fbf", "#0b1568")
        canvas.delete("content")

        # LEFT HEADING
        canvas.create_text(85, header_h // 2, anchor="w", text="🧵 THREAD INVENTORY DASHBOARD",
            font=("Segoe UI", 19, "bold"), fill="white", tags="content")

        canvas.create_text(48, header_h // 2, anchor="w", text="🧵", font=("Segoe UI", 28),
            fill="#a9c2ff", tags="content")

        # RIGHT COMPANY NAME
        canvas.create_text(w - 38, header_h // 2 - 10, anchor="e", text="🧵",
            font=("Segoe UI", 22), fill="white", tags="content")

        canvas.create_text(w - 38, header_h // 2 + 14, anchor="e", text="RASHID BROTHERS",
            font=("Segoe UI", 14, "bold"), fill="white", tags="content")

        # ✅ DATE/TIME LABEL - Recreate if destroyed
        if not date_time_label or not date_time_label.winfo_exists():
            date_time_label = tk.Label(outer, text="", font=("Segoe UI", 11, "bold"),
                                        bg="#123a9b", fg="white")
            date_time_label.place(relx=0.60, rely=0.38, anchor="center")
            # Start the timer only once
            if after_id is None:
                update_date_time()

        # ✅ REFRESH BUTTON
        refresh_btn = tk.Button(outer, text="🔄 Refresh",
            command=lambda: [outer.winfo_toplevel().destroy(), open_dashboard()],
            bg="#123a9b", fg="white", font=("Segoe UI", 11, "bold"), relief="flat",
            cursor="hand2", padx=12, pady=4)
        refresh_btn.place(relx=0.60, rely=0.68, anchor="center")

    canvas.bind("<Configure>", redraw)

    def on_destroy(event):
        nonlocal after_id
        if after_id is not None:
            try:
                outer.after_cancel(after_id)
            except:
                pass
            after_id = None
    
    outer.bind("<Destroy>", on_destroy)
    
    # Initial call
    parent.after(100, redraw)
    return outer

# CARDS
def create_kpi_card(parent, title, value_text, color_start, color_end, width=300, height=90):
    """KPI Card - 4 cards in a row"""
    outer = tk.Frame(parent, width=width, height=height)
    outer.grid_propagate(False)

    canvas = tk.Canvas(outer, width=width, height=height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    draw_vertical_gradient(canvas, width, height, color_start, color_end)

    canvas.create_text(18, 20, anchor="w", text=title, font=("Segoe UI", 11, "bold"), fill="white")
    canvas.create_line(18, 36, width - 18, 36, fill="#ffffff")
    canvas.create_text(18, 65, anchor="w", text=value_text, font=("Segoe UI", 18, "bold"), fill="white")

    return outer


def create_menu_card(parent, icon, title, command, width=210, height=75):
    """FIXED: No more khul-band effect on hover"""
    card = tk.Frame(parent, bg="white", relief="solid", bd=1, width=width, height=height, cursor="hand2")
    card.grid_propagate(False)
    
    # Inner frame with fixed size
    inner = tk.Frame(card, bg="white", width=width, height=height)
    inner.pack(fill="both", expand=True, padx=10, pady=6)
    inner.pack_propagate(False)
    
    # Icon and Text side by side
    top_row = tk.Frame(inner, bg="white")
    top_row.pack(fill="x", expand=True)
    
    icon_lbl = tk.Label(top_row, text=icon, font=("Segoe UI", 20), bg="white")
    icon_lbl.pack(side="left", padx=(0, 10))
    
    text_lbl = tk.Label(top_row, text=title, font=("Segoe UI", 10, "bold"), bg="white",
                         fg="#12266b", justify="left")
    text_lbl.pack(side="left")
    
    # Store widgets for hover effect
    widgets = (card, inner, top_row, icon_lbl, text_lbl)
    
    def on_enter(e):
        # Only change background color, NO size change
        for w in widgets:
            try:
                w.config(bg="#eaf1ff")
            except:
                pass
    
    def on_leave(e):
        # Only change background color back, NO size change
        for w in widgets:
            try:
                w.config(bg="white")
            except:
                pass
    
    def on_click(e):
        command()
    
    # Bind events to all widgets
    for w in widgets:
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)
        w.bind("<Button-1>", on_click)
    
    return card

# SUB-PAGES
def open_current_stock_summary(win, back_callback):
    for w in win.winfo_children():
        w.destroy()
    win.config(bg="#f4f6f9")

    header = tk.Frame(win, bg="#f4f6f9")
    header.pack(fill="x", pady=10)
    tk.Button(header, text="⬅ Back", command=back_callback, bg="#34495e", fg="white",
              font=("Arial", 10, "bold"), width=10, height=2, relief="flat",
              cursor="hand2").pack(side="left", padx=20)
    tk.Label(header, text="🗄️ Current Stock Summary", font=("Segoe UI", 18, "bold"),
              bg="#f4f6f9", fg="#1c275a").pack(side="left", padx=10)

    tree_frame = tk.Frame(win, bg="#f4f6f9")
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("Thread", "Size", "Total Stock In", "Available Now")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180, anchor="center")
    tree.pack(fill="both", expand=True)
    tree.tag_configure("low", background="#fdecea")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, thread_name, size, bundle_quantity FROM stock_in")
        rows = cursor.fetchall()
        conn.close()
        conn = None

        summary = {}
        for r in rows:
            key = (r["thread_name"] or "N/A", r["size"] or "N/A")
            avail = get_available_stock(r["id"])
            if key not in summary:
                summary[key] = {"total_in": 0, "available": 0}
            summary[key]["total_in"] += r["bundle_quantity"] or 0
            summary[key]["available"] += avail

        for (thread, size), vals in sorted(summary.items()):
            tag = "low" if vals["available"] < LOW_STOCK_THRESHOLD else ""
            tree.insert("", "end", values=(thread, size, vals["total_in"], vals["available"]), tags=(tag,))

        if not summary:
            messagebox.showinfo("No Data", "No stock in records found yet.")

    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if conn:
            conn.close()


def open_color_wise_stock(win, back_callback):
    for w in win.winfo_children():
        w.destroy()
    win.config(bg="#f4f6f9")

    header = tk.Frame(win, bg="#f4f6f9")
    header.pack(fill="x", pady=10)
    tk.Button(header, text="⬅ Back", command=back_callback, bg="#34495e", fg="white",
              font=("Arial", 10, "bold"), width=10, height=2, relief="flat",
              cursor="hand2").pack(side="left", padx=20)
    tk.Label(header, text="🎨 Color Wise Stock", font=("Segoe UI", 18, "bold"),
              bg="#f4f6f9", fg="#1c275a").pack(side="left", padx=10)

    tk.Label(win, text="Note: colors are recorded at the Stock Out stage, so this shows quantities issued/sold per color.",
              font=("Arial", 9, "italic"), bg="#f4f6f9", fg="#7f8c8d").pack(pady=(0, 8))

    tree_frame = tk.Frame(win, bg="#f4f6f9")
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("Color", "Thread", "Size", "Total Qty Issued")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=170, anchor="center")
    tree.pack(fill="both", expand=True)

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT color, thread_name, size, SUM(bundle_quantity) AS qty
            FROM stock_out
            WHERE color IS NOT NULL AND color != ''
            GROUP BY color, thread_name, size
            ORDER BY color, thread_name
        """)
        rows = cursor.fetchall()
        for r in rows:
            tree.insert("", "end", values=(r["color"], r["thread_name"] or "N/A",
                                            r["size"] or "N/A", r["qty"] or 0))
        if not rows:
            messagebox.showinfo("No Data", "No color-tagged stock out records found yet.")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if conn:
            conn.close()


def open_order_history(win, back_callback):
    for w in win.winfo_children():
        w.destroy()
    win.config(bg="#f4f6f9")

    header = tk.Frame(win, bg="#f4f6f9")
    header.pack(fill="x", pady=10)
    tk.Button(header, text="⬅ Back", command=back_callback, bg="#34495e", fg="white",
              font=("Arial", 10, "bold"), width=10, height=2, relief="flat",
              cursor="hand2").pack(side="left", padx=20)
    tk.Label(header, text="📋 Sale Order History", font=("Segoe UI", 18, "bold"),
              bg="#f4f6f9", fg="#1c275a").pack(side="left", padx=10)

    tk.Button(header, text="➕ New Sale (Stock Out)",
              command=lambda: open_stock_out(win, lambda: open_order_history(win, back_callback)),
              bg="#0d4695", fg="white", font=("Arial", 10, "bold"), width=20, height=2,
              relief="flat", cursor="hand2").pack(side="right", padx=20)

    tree_frame = tk.Frame(win, bg="#f4f6f9")
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("SO#", "Date", "Customer", "Thread", "Size", "Qty", "Final Total")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor="center")
    tree.pack(fill="both", expand=True)

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT so_number, date, customer_name, thread_name, size,
                   bundle_quantity, final_total_price
            FROM stock_out ORDER BY date DESC, id DESC
        """)
        rows = cursor.fetchall()
        for r in rows:
            tree.insert("", "end", values=(
                r["so_number"], r["date"], r["customer_name"] or "N/A",
                r["thread_name"] or "N/A", r["size"] or "N/A",
                r["bundle_quantity"] or 0, f"{float(r['final_total_price'] or 0):,.2f}"
            ))
        if not rows:
            messagebox.showinfo("No Data", "No sales orders found yet.")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if conn:
            conn.close()


def open_all_low_stock(win, back_callback):
    for w in win.winfo_children():
        w.destroy()
    win.config(bg="#f4f6f9")

    header = tk.Frame(win, bg="#f4f6f9")
    header.pack(fill="x", pady=10)
    tk.Button(header, text="⬅ Back", command=back_callback, bg="#34495e", fg="white",
              font=("Arial", 10, "bold"), width=10, height=2, relief="flat",
              cursor="hand2").pack(side="left", padx=20)
    tk.Label(header, text="⚠ All Low Stock Alerts", font=("Segoe UI", 18, "bold"),
              bg="#f4f6f9", fg="#1c275a").pack(side="left", padx=10)

    container = tk.Frame(win, bg="white", relief="solid", bd=1)
    container.pack(fill="both", expand=True, padx=20, pady=10)

    col_header = tk.Frame(container, bg="#f4f6f9")
    col_header.pack(fill="x")
    header_cols = [("Thread", 25), ("Size", 15), ("Available Qty", 18), ("Action", 12)]
    for i, (h, w) in enumerate(header_cols):
        tk.Label(col_header, text=h, font=("Segoe UI", 10, "bold"), bg="#f4f6f9",
                  fg="#2c3e50", anchor="w", width=w).grid(row=0, column=i, sticky="w", padx=15, pady=8)

    items = fetch_low_stock_items()

    if not items:
        tk.Label(container, text="✅ No low stock items right now.",
                  font=("Segoe UI", 12), bg="white", fg="#27ae60").pack(pady=30)
        return

    for item in items:
        row = tk.Frame(container, bg="white")
        row.pack(fill="x")
        tk.Label(row, text=f"🧵 {item['thread']}", bg="white", anchor="w",
                  font=("Segoe UI", 10, "bold"), fg="#12266b", width=25).grid(row=0, column=0, sticky="w", padx=15, pady=8)
        tk.Label(row, text=item["size"], bg="white", anchor="w", width=15).grid(row=0, column=1, sticky="w", padx=15)
        tk.Label(row, text=f"{item['available']} bundles", bg="white", anchor="w",
                  fg="#c0392b", font=("Segoe UI", 10, "bold"), width=18).grid(row=0, column=2, sticky="w", padx=15)

        def make_reorder(thread=item["thread"], size=item["size"]):
            def action():
                open_stock_in(prefill_thread=thread, prefill_size=size)
            return action

        tk.Button(row, text="Reorder", command=make_reorder(), bg="#e8930f", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10
                  ).grid(row=0, column=3, sticky="w", padx=15, pady=6)


# MAIN DASHBOARD
def open_dashboard():
    root = tk.Tk()
    root.title("Designed By: Al-Rehman Software")
    root.geometry("1200x850")
    root.config(bg="#eef1f6")

    build_header(root)

    # Backup system
    backup_frame = tk.Frame(root, bg="#eef1f6")
    backup_frame.pack(fill="x", padx=20, pady=(5, 0))

    tk.Button(backup_frame,text="💾 Backup Data",command=create_backup,bg="#eef1f6",
            fg="#A3089C",font=("Segoe UI", 11, "bold"),width=16, height=2,
            cursor="hand2").pack(side="right", padx=5)

    tk.Button(backup_frame,text="🔄 Restore Backup",command=restore_backup,bg="#eef1f6",
            fg="#0c1568",font=("Segoe UI", 11, "bold"),width=16,height=2,
            cursor="hand2").pack(side="right", padx=5)
    
    # ---------------- SCROLLABLE CONTAINER ----------------
    container = tk.Frame(root, bg="#eef1f6")
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container, bg="#eef1f6", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    scroll_frame = tk.Frame(canvas, bg="#eef1f6")
    canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def resize_scroll(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", resize_scroll)

    def mousewheel_scroll(event):
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass
    canvas.bind_all("<MouseWheel>", mousewheel_scroll)

    # ---------------- KPI ROW (4 CARDS) ----------------
    kpi_data = fetch_dashboard_kpis()
    kpi_frame = tk.Frame(scroll_frame, bg="#eef1f6")
    kpi_frame.pack(fill="x", padx=20, pady=12)

    # 4 columns for 4 cards
    for i in range(4):
        kpi_frame.grid_columnconfigure(i, weight=1)

    # ✅ Card 1: Available Stock (Changed from Total Stock)
    create_kpi_card(kpi_frame, "Available Stock", f"{kpi_data['available_stock']:,} Bundles",
                     "#1b4fbf", "#0c1568").grid(row=0, column=0, padx=6)

    # Card 2: Issued to Dyeing
    create_kpi_card(kpi_frame, "Issued to Dyeing", f"{kpi_data['total_issued']:,} Bundles",
                     "#f2994a", "#c9660c").grid(row=0, column=1, padx=6)

    # Card 3: Dyeing Return
    create_kpi_card(kpi_frame, "🔄 Dyeing Return", f"{kpi_data['dyeing_return']:,} Bundles",
                     "#27ae60", "#146c34").grid(row=0, column=2, padx=6)

    # Card 4: Dyeing Pending (Issued - Returned)
    create_kpi_card(kpi_frame, "⏳ Dyeing Pending", f"{kpi_data['dyeing_pending']:,} Bundles",
                     "#6f53dd", "#741de4").grid(row=0, column=3, padx=6)

    # ---------------- MENU GRID (8 buttons - 2 rows x 4 columns) ----------------
    menu_frame = tk.Frame(scroll_frame, bg="#eef1f6")
    menu_frame.pack(padx=20, pady=(0, 10))

    def go_stock_in():
        open_stock_in()

    def go_issue_dyeing():
        open_send_dyeing(root, open_dashboard)

    def go_receive_dyeing():
        open_return_dyeing(root, open_dashboard)

    def go_current_stock():
        open_current_stock_summary(root, open_dashboard)

    def go_color_wise():
        open_color_wise_stock(root, open_dashboard)

    def go_supplier():
        open_supplier_detail()

    def go_order_history():
        open_order_history(root, open_dashboard)

    def go_reports():
        open_reports(root, open_dashboard)

    menu_items = [
        ("🧵", "Stock In\n New Thread", go_stock_in),
        ("🏭", "Issue to\nDyeing", go_issue_dyeing),
        ("📦", "Receive from\nDyeing", go_receive_dyeing),
        ("🗄️", "Current\nStock", go_current_stock),
        ("🎨", "Color Wise\nStock", go_color_wise),
        ("🤝", "Supplier\nManagement", go_supplier),
        ("📋", "Sale Order\nHistory", go_order_history),
        ("📊", "Reports", go_reports),
    ]

    for i, (icon, title, cmd) in enumerate(menu_items):
        r, c = divmod(i, 4)
        card = create_menu_card(menu_frame, icon, title, cmd)
        card.grid(row=r, column=c, padx=6, pady=6)

    # ===== AI PANEL =====
    ai_dashboard = AIDashboard(root)
    ai_dashboard.create_ai_panel(scroll_frame)

    # ---------------- INFO BAR ----------------
    low_stock_items = fetch_low_stock_items()

    info_frame = tk.Frame(scroll_frame, bg="white", relief="solid", bd=1)
    info_frame.pack(fill="x", padx=20, pady=(5, 10))

    tk.Label(info_frame, text=f"📅 Pending Orders: {kpi_data['pending_orders']}",
              font=("Segoe UI", 11, "bold"), bg="white", fg="#12266b").pack(side="left", padx=15, pady=8)
    tk.Label(info_frame, text=f"⚠ Low Stock Alerts: {len(low_stock_items)}",
              font=("Segoe UI", 11, "bold"), bg="white", fg="#c0392b").pack(side="left", padx=15)

    tk.Button(info_frame, text=f"👥 Total Customers: {kpi_data['total_customers']}",
              command=open_customer_detail, font=("Segoe UI", 11, "bold"), bg="white",
              fg="#12266b", relief="flat", cursor="hand2").pack(side="left", padx=15)

    tk.Button(info_frame, text="📁 View All Alerts",
              command=lambda: open_all_low_stock(root, open_dashboard),
              font=("Segoe UI", 10, "bold"), bg="white", fg="#2980b9",
              relief="flat", cursor="hand2").pack(side="right", padx=15)

    # ---------------- LOW STOCK ALERTS TABLE ----------------
    alerts_frame = tk.Frame(scroll_frame, bg="white", relief="solid", bd=1)
    alerts_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    alerts_header = tk.Frame(alerts_frame, bg="#0c1568")
    alerts_header.pack(fill="x")
    tk.Label(alerts_header, text="Low Stock Alerts", font=("Segoe UI", 13, "bold"),
              bg="#0c1568", fg="white").pack(side="left", padx=15, pady=6)

    columns_frame = tk.Frame(alerts_frame, bg="#f4f6f9")
    columns_frame.pack(fill="x")
    header_cols = [("Thread", 25), ("Size", 15), ("Available Qty", 18), ("Action", 12)]
    for i, (h, w) in enumerate(header_cols):
        tk.Label(columns_frame, text=h, font=("Segoe UI", 10, "bold"), bg="#f4f6f9",
                  fg="#2c3e50", anchor="w", width=w).grid(row=0, column=i, sticky="w", padx=15, pady=6)

    rows_container = tk.Frame(alerts_frame, bg="white")
    rows_container.pack(fill="both", expand=True)

    display_items = low_stock_items[:5]

    if not display_items:
        tk.Label(rows_container, text="✅ No low stock items right now.",
                  font=("Segoe UI", 11), bg="white", fg="#27ae60").pack(pady=18)
    else:
        for item in display_items:
            row = tk.Frame(rows_container, bg="white")
            row.pack(fill="x")
            tk.Label(row, text=f"🧵 {item['thread']}", bg="white", anchor="w",
                      font=("Segoe UI", 10, "bold"), fg="#12266b", width=25).grid(row=0, column=0, sticky="w", padx=15, pady=6)
            tk.Label(row, text=item["size"], bg="white", anchor="w", width=15).grid(row=0, column=1, sticky="w", padx=15)
            tk.Label(row, text=f"{item['available']} bundles", bg="white", anchor="w",
                      fg="#c0392b", font=("Segoe UI", 10, "bold"), width=18).grid(row=0, column=2, sticky="w", padx=15)

            def make_reorder(thread=item["thread"], size=item["size"]):
                def action():
                    open_stock_in(prefill_thread=thread, prefill_size=size)
                return action

            tk.Button(row, text="Reorder", command=make_reorder(), bg="#e8930f", fg="white",
                      font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10
                      ).grid(row=0, column=3, sticky="w", padx=15, pady=4)

        if len(low_stock_items) > 5:
            tk.Button(rows_container, text=f"View All {len(low_stock_items)} Alerts →",
                      command=lambda: open_all_low_stock(root, open_dashboard),
                      font=("Segoe UI", 10, "bold"), bg="white", fg="#2980b9",
                      relief="flat", cursor="hand2").pack(anchor="w", padx=15, pady=6)

    footer = tk.Label(scroll_frame, text="© 2026 Thread Inventory System — Al-Rehman Software\nContact # 0333-3988781", 
                    font=("Segoe UI", 10, "bold"),bg="#eef1f6", fg="#12266b")
    footer.pack(side="bottom", pady=6)

    root.mainloop()

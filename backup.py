import os
import json
import subprocess
import threading
import time
import math
from datetime import datetime
from tkinter import filedialog, messagebox, ttk, Toplevel, Label, Frame

from config import DB_CONFIG


SETTINGS_FILE = "backup_settings.json"


def get_backup_folder():
    folder = os.path.join(os.getcwd(), "Backups")
    os.makedirs(folder, exist_ok=True)
    return folder


def load_location():
    try:
        with open(SETTINGS_FILE, "r") as f:
            folder = json.load(f).get("backup_location")
            if folder and os.path.exists(folder):
                return folder
    except:
        pass
    return get_backup_folder()


def save_location(folder):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"backup_location": folder}, f)


def find_mysqldump():
    paths = [
        r"C:\Program Files\MySQL\MySQL Server 8.1\bin\mysqldump.exe",
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
        r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe",
        r"C:\xampp\mysql\bin\mysqldump.exe"
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return "mysqldump"


def find_mysql():
    paths = [
        r"C:\Program Files\MySQL\MySQL Server 8.1\bin\mysql.exe",
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
        r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe",
        r"C:\xampp\mysql\bin\mysql.exe"
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return "mysql"


def create_backup(show_message=True):
    try:
        folder = filedialog.askdirectory(title="Select Backup Location")
        if not folder:
            return False
        save_location(folder)
        date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = os.path.join(folder, f"Thread_ERP_Backup_{date_time}.sql")
        command = [
            find_mysqldump(),
            "-h", DB_CONFIG["host"],
            "-u", DB_CONFIG["user"],
            f"-p{DB_CONFIG['password']}",
            DB_CONFIG["database"]
        ]
        with open(backup_file, "w", encoding="utf-8") as f:
            result = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            if show_message:
                messagebox.showinfo("Backup Successful", f"Backup created successfully.\n\n{backup_file}")
            return True
        if os.path.exists(backup_file):
            os.remove(backup_file)
        if show_message:
            messagebox.showerror("Backup Error", result.stderr)
        return False
    except Exception as e:
        if show_message:
            messagebox.showerror("Backup Error", str(e))
        return False


def automatic_daily_backup():
    try:
        folder = load_location()
        date = datetime.now().strftime("%Y-%m-%d")
        today_backup = False
        for name in os.listdir(folder):
            if name.startswith(f"Thread_ERP_Backup_{date}") and name.endswith(".sql"):
                today_backup = True
                break
        if today_backup:
            return
        date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = os.path.join(folder, f"Thread_ERP_Backup_{date_time}.sql")
        command = [
            find_mysqldump(),
            "-h", DB_CONFIG["host"],
            "-u", DB_CONFIG["user"],
            f"-p{DB_CONFIG['password']}",
            DB_CONFIG["database"]
        ]
        with open(backup_file, "w", encoding="utf-8") as f:
            result = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0 and os.path.exists(backup_file):
            os.remove(backup_file)
    except:
        pass


# ============================================================
# ✅ RESTORE BACKUP WITH PROGRESS BAR
# ============================================================

def restore_backup(restart_callback=None):
    try:
        backup_file = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("SQL Backup", "*.sql")]
        )
        if not backup_file:
            return False

        confirm = messagebox.askyesno("Restore Backup",
            "This will replace the current database data.\n\n"
            "Are you sure you want to restore this backup?"
        )
        if not confirm:
            return False

        # ===== PROGRESS WINDOW =====
        progress_win = Toplevel()
        progress_win.title("Restoring Backup")
        progress_win.geometry("420x180")
        progress_win.resizable(False, False)
        progress_win.config(bg="#f4f6f9")
        
        # Center the window
        progress_win.transient(progress_win.master)
        progress_win.grab_set()
        
        # Title
        Label(progress_win, text="🔄 Restoring Database Backup", 
              font=("Segoe UI", 14, "bold"), bg="#f4f6f9", fg="#1b4fbf").pack(pady=(15, 5))
        
        # Subtitle
        Label(progress_win, text="Please wait while your data is being restored...", 
              font=("Segoe UI", 10), bg="#f4f6f9", fg="#555").pack()
        
        # Progress Bar
        progress_bar = ttk.Progressbar(progress_win, length=350, mode='indeterminate')
        progress_bar.pack(pady=15)
        progress_bar.start(10)
        
        # Status Label
        status_label = Label(progress_win, text="⏳ Restoring data...", 
                             font=("Segoe UI", 10, "bold"), bg="#f4f6f9", fg="#2980b9")
        status_label.pack(pady=5)
        
        # Percentage Label
        percent_label = Label(progress_win, text="0%", 
                              font=("Segoe UI", 12, "bold"), bg="#f4f6f9", fg="#1b4fbf")
        percent_label.pack(pady=5)
        
        # Force update
        progress_win.update()
        
        # ===== ACTUAL RESTORE IN THREAD =====
        restore_success = False
        error_message = ""
        
        def do_restore():
            nonlocal restore_success, error_message
            try:
                mysql = find_mysql()
                command = [
                    mysql,
                    "-h", DB_CONFIG["host"],
                    "-u", DB_CONFIG["user"],
                    f"-p{DB_CONFIG['password']}",
                    DB_CONFIG["database"]
                ]
                
                # Get file size for progress
                file_size = os.path.getsize(backup_file)
                processed = 0
                
                with open(backup_file, "r", encoding="utf-8") as f:
                    chunk_size = 8192
                    total_chunks = max(1, math.ceil(file_size / chunk_size))
                    processed_chunks = 0
                    
                    # Start subprocess
                    process = subprocess.Popen(
                        command,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        try:
                            process.stdin.write(chunk)
                            process.stdin.flush()
                        except:
                            break
                        
                        processed_chunks += 1
                        percent = min(99, int((processed_chunks / total_chunks) * 100))
                        
                        # Update UI
                        progress_win.after(0, lambda p=percent: update_progress(p))
                    
                    process.stdin.close()
                    process.wait()
                    
                    if process.returncode == 0:
                        restore_success = True
                        progress_win.after(0, lambda: update_progress(100))
                    else:
                        error_message = process.stderr.read() if process.stderr else "Unknown error"
                        
            except Exception as e:
                error_message = str(e)
            finally:
                progress_win.after(0, close_progress)
        
        def update_progress(value):
            try:
                percent_label.config(text=f"{value}%")
                if value < 30:
                    status_label.config(text="⏳ Dropping old tables...", fg="#2980b9")
                elif value < 60:
                    status_label.config(text="⏳ Importing data...", fg="#f39c12")
                elif value < 90:
                    status_label.config(text="⏳ Verifying data...", fg="#27ae60")
                else:
                    status_label.config(text="✅ Almost done!", fg="#27ae60")
                progress_win.update()
            except:
                pass
        
        def close_progress():
            try:
                progress_bar.stop()
                progress_win.destroy()
            except:
                pass
            
            if restore_success:
                messagebox.showinfo("Restore Successful",
                    "✅ Backup restored successfully!\n\n"
                    "Software will restart automatically.")
                if restart_callback:
                    restart_callback()
            else:
                messagebox.showerror("Restore Error", 
                    f"❌ Restore failed!\n\n{error_message}")
        
        # Start restore thread
        threading.Thread(target=do_restore, daemon=True).start()
        
        return True
        
    except Exception as e:
        messagebox.showerror("Restore Error", str(e))
        return False
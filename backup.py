import os
import json
import subprocess
from datetime import datetime
from tkinter import filedialog, messagebox

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
        folder = filedialog.askdirectory(
            title="Select Backup Location"
        )

        if not folder:
            return False

        save_location(folder)

        date_time = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        backup_file = os.path.join(
            folder,
            f"Thread_ERP_Backup_{date_time}.sql"
        )

        command = [
            find_mysqldump(),
            "-h", DB_CONFIG["host"],
            "-u", DB_CONFIG["user"],
            f"-p{DB_CONFIG['password']}",
            DB_CONFIG["database"]
        ]

        with open(backup_file, "w", encoding="utf-8") as f:

            result = subprocess.run(
                command,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )

        if result.returncode == 0:

            if show_message:
                messagebox.showinfo(
                    "Backup Successful",
                    f"Backup created successfully.\n\n"
                    f"{backup_file}"
                )

            return True

        if os.path.exists(backup_file):
            os.remove(backup_file)

        if show_message:
            messagebox.showerror(
                "Backup Error",
                result.stderr
            )

        return False

    except Exception as e:

        if show_message:
            messagebox.showerror(
                "Backup Error",
                str(e)
            )

        return False


def automatic_daily_backup():
    try:

        folder = load_location()

        date = datetime.now().strftime(
            "%Y-%m-%d"
        )

        # Check whether today's backup already exists
        today_backup = False

        for name in os.listdir(folder):

            if (
                name.startswith(f"Thread_ERP_Backup_{date}")
                and name.endswith(".sql")
            ):
                today_backup = True
                break

        if today_backup:
            return

        date_time = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        backup_file = os.path.join(
            folder,
            f"Thread_ERP_Backup_{date_time}.sql"
        )

        command = [
            find_mysqldump(),
            "-h", DB_CONFIG["host"],
            "-u", DB_CONFIG["user"],
            f"-p{DB_CONFIG['password']}",
            DB_CONFIG["database"]
        ]

        with open(backup_file, "w", encoding="utf-8") as f:

            result = subprocess.run(
                command,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )

        if result.returncode != 0:

            if os.path.exists(backup_file):
                os.remove(backup_file)

    except:
        pass


def restore_backup(restart_callback=None):

    try:

        backup_file = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[
                ("SQL Backup", "*.sql")
            ]
        )

        if not backup_file:
            return False

        confirm = messagebox.askyesno("Restore Backup",
            "This will replace the current database data.\n\n"
            "Are you sure you want to restore this backup?"
        )

        if not confirm:
            return False

        mysql = find_mysql()

        command = [
            mysql,
            "-h", DB_CONFIG["host"],
            "-u", DB_CONFIG["user"],
            f"-p{DB_CONFIG['password']}",
            DB_CONFIG["database"]
        ]

        with open(backup_file,"r",encoding="utf-8") as f:
            result = subprocess.run(command,stdin=f,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

        if result.returncode == 0:
            messagebox.showinfo("Restore Successful",
                "Backup restored successfully.\n\n"
                "Software will restart automatically.")

            if restart_callback:
                restart_callback()
            return True
        messagebox.showerror("Restore Error",result.stderr)
        return False

    except Exception as e:
        messagebox.showerror("Restore Error",str(e))
        return False


# import os
# import json
# import subprocess
# from datetime import datetime
# from tkinter import filedialog, messagebox
# from config import DB_CONFIG

# SETTINGS_FILE = "backup_settings.json"


# def get_backup_folder():
#     folder = os.path.join(os.getcwd(), "Backups")
#     os.makedirs(folder, exist_ok=True)
#     return folder


# def load_location():
#     try:
#         with open(SETTINGS_FILE, "r") as f:
#             folder = json.load(f).get("backup_location")
#             if folder and os.path.exists(folder):
#                 return folder
#     except:
#         pass
#     return get_backup_folder()


# def save_location(folder):
#     with open(SETTINGS_FILE, "w") as f:
#         json.dump({"backup_location": folder}, f)


# def find_mysqldump():
#     paths = [
#         r"C:\Program Files\MySQL\MySQL Server 8.1\bin\mysqldump.exe",
#         r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
#         r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe",
#         r"C:\xampp\mysql\bin\mysqldump.exe"
#     ]

#     for path in paths:
#         if os.path.exists(path):
#             return path

#     return "mysqldump"


# def find_mysql():
#     paths = [
#         r"C:\Program Files\MySQL\MySQL Server 8.1\bin\mysql.exe",
#         r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
#         r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe",
#         r"C:\xampp\mysql\bin\mysql.exe"
#     ]

#     for path in paths:
#         if os.path.exists(path):
#             return path

#     return "mysql"


# def delete_old_backups():
#     folder = load_location()
#     now = datetime.now()

#     try:
#         for name in os.listdir(folder):
#             if name.startswith("Thread_ERP_Backup_") and name.endswith(".sql"):
#                 path = os.path.join(folder, name)
#                 age = (now - datetime.fromtimestamp(
#                     os.path.getmtime(path)
#                 )).days

#                 if age > 30:
#                     os.remove(path)
#     except:
#         pass


# def create_backup(show_message=True):
#     try:
#         folder = filedialog.askdirectory(title="Select Backup Location")

#         if not folder:
#             return False

#         save_location(folder)

#         date = datetime.now().strftime("%Y-%m-%d")
#         backup_file = os.path.join(
#             folder,
#             f"Thread_ERP_Backup_{date}.sql"
#         )

#         if os.path.exists(backup_file):
#             if show_message:
#                 messagebox.showinfo(
#                     "Backup",
#                     "Today's backup already exists."
#                 )
#             return True

#         command = [
#             find_mysqldump(),
#             "-h", DB_CONFIG["host"],
#             "-u", DB_CONFIG["user"],
#             f"-p{DB_CONFIG['password']}",
#             DB_CONFIG["database"]
#         ]

#         with open(backup_file, "w", encoding="utf-8") as f:
#             result = subprocess.run(
#                 command,
#                 stdout=f,
#                 stderr=subprocess.PIPE,
#                 text=True
#             )

#         if result.returncode == 0:
#             delete_old_backups()

#             if show_message:
#                 messagebox.showinfo(
#                     "Backup",
#                     f"Backup created successfully.\n\n{backup_file}"
#                 )

#             return True

#         if os.path.exists(backup_file):
#             os.remove(backup_file)

#         if show_message:
#             messagebox.showerror(
#                 "Backup Error",
#                 result.stderr
#             )

#         return False

#     except Exception as e:
#         if show_message:
#             messagebox.showerror(
#                 "Backup Error",
#                 str(e)
#             )
#         return False


# def automatic_daily_backup():
#     try:
#         folder = load_location()
#         date = datetime.now().strftime("%Y-%m-%d")

#         backup_file = os.path.join(
#             folder,
#             f"Thread_ERP_Backup_{date}.sql"
#         )

#         if not os.path.exists(backup_file):

#             command = [
#                 find_mysqldump(),
#                 "-h", DB_CONFIG["host"],
#                 "-u", DB_CONFIG["user"],
#                 f"-p{DB_CONFIG['password']}",
#                 DB_CONFIG["database"]
#             ]

#             with open(backup_file, "w", encoding="utf-8") as f:
#                 result = subprocess.run(
#                     command,
#                     stdout=f,
#                     stderr=subprocess.PIPE,
#                     text=True
#                 )

#             if result.returncode != 0 and os.path.exists(backup_file):
#                 os.remove(backup_file)

#         delete_old_backups()

#     except:
#         pass


# def restore_backup():
#     try:
#         backup_file = filedialog.askopenfilename(
#             title="Select Backup File",
#             filetypes=[("SQL Backup", "*.sql")]
#         )

#         if not backup_file:
#             return False

#         confirm = messagebox.askyesno(
#             "Restore Backup",
#             "This will replace the current database data.\n\n"
#             "Are you sure you want to restore this backup?"
#         )

#         if not confirm:
#             return False

#         mysql = find_mysql()

#         command = [
#             mysql,
#             "-h", DB_CONFIG["host"],
#             "-u", DB_CONFIG["user"],
#             f"-p{DB_CONFIG['password']}",
#             DB_CONFIG["database"]
#         ]

#         with open(backup_file, "r", encoding="utf-8") as f:
#             result = subprocess.run(
#                 command,
#                 stdin=f,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 text=True
#             )

#         if result.returncode == 0:
#             messagebox.showinfo(
#                 "Restore Successful",
#                 "Backup restored successfully.\n\n"
#                 "Please restart the software."
#             )
#             return True

#         messagebox.showerror(
#             "Restore Error",
#             result.stderr
#         )
#         return False

#     except Exception as e:
#         messagebox.showerror(
#             "Restore Error",
#             str(e)
#         )
#         return False
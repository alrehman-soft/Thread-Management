from dashboard import open_dashboard
from backup import automatic_daily_backup

if __name__ == "__main__":
    automatic_daily_backup()
    open_dashboard()
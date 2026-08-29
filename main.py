from dashboard import open_dashboard
from backup import automatic_daily_backup
from database import init_database

if __name__ == "__main__":
    init_database()
    automatic_daily_backup()
    open_dashboard()
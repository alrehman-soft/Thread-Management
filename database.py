import pymysql
import pymysql.cursors
from config import DB_CONFIG

# CONNECTION
def get_connection():
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor
    )

# AUTO GENERATORS
def generate_so_number():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM stock_out")
    count = cursor.fetchone()['total'] + 1

    cursor.close()
    conn.close()

    return f"SO-{count:04d}"

def generate_batch_id():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM send_dyeing")
    count = cursor.fetchone()['total'] + 1

    cursor.close()
    conn.close()

    return f"BATCH-{count:04d}"


# DATABASE INIT
def init_database():
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()

        # Create DB
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        # STOCK IN
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_in (
                id INT AUTO_INCREMENT PRIMARY KEY,
                po_number VARCHAR(50) UNIQUE,
                date DATE NOT NULL,
                supplier_name VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                supplier_cnic VARCHAR(20),
                company_name VARCHAR(100),
                thread_name VARCHAR(100),
                size VARCHAR(50),
                bundle_quantity INT,
                bundle_price DECIMAL(10,2),
                total_price DECIMAL(10,2) GENERATED ALWAYS AS (bundle_quantity * bundle_price) STORED,
                paid_amount DECIMAL(10,2) DEFAULT 0,
                balance DECIMAL(10,2) GENERATED ALWAYS AS ((bundle_quantity * bundle_price) - paid_amount) STORED,
                status ENUM('pending','partial','completed') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        # SEND TO DYEING
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS send_dyeing (
                id INT AUTO_INCREMENT PRIMARY KEY,
                batch_id VARCHAR(50) NOT NULL,
                date DATE NOT NULL,
                stock_in_id INT,
                thread_name VARCHAR(100),
                size VARCHAR(50),
                issued_quantity INT,
                dyeing_info TEXT,
                reason_for_issue TEXT,
                sender VARCHAR(100),
                receiver VARCHAR(100),
                status ENUM('sent','partial','returned') DEFAULT 'sent',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (stock_in_id) REFERENCES stock_in(id) ON DELETE CASCADE
            )
        """)
        try:
            cursor.execute("""
                ALTER TABLE send_dyeing 
                ADD COLUMN expected_return_date DATE
            """)
        except:
            pass

       # RETURN FROM DYEING
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS return_dyeing (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            send_dyeing_id INT NOT NULL,
            batch_id VARCHAR(50) NOT NULL,
            thread_name VARCHAR(100),
            size VARCHAR(50),
            issued_quantity INT,
            return_quantity INT NOT NULL,
            dyeing_info TEXT,
            sender VARCHAR(100),
            receiver VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (send_dyeing_id)
                REFERENCES send_dyeing(id)
                ON DELETE CASCADE
            )
        """)

        # STOCK OUT
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_out (
                id INT AUTO_INCREMENT PRIMARY KEY,
                so_number VARCHAR(50) UNIQUE,
                date DATE NOT NULL,
                customer_name VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                customer_cnic VARCHAR(20),
                company_name VARCHAR(100),
                thread_name VARCHAR(100),
                size VARCHAR(50),
                color VARCHAR(50),
                bundle_quantity INT,
                issued_by VARCHAR(100),
                bundle_price DECIMAL(10,2),
                total_bundle_price DECIMAL(10,2) GENERATED ALWAYS AS (bundle_quantity * bundle_price) STORED,
                discount DECIMAL(10,2) DEFAULT 0,
                final_total_price DECIMAL(10,2) GENERATED ALWAYS AS ((bundle_quantity * bundle_price) - discount) STORED,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()

        # print("✅ Advanced Database Ready!")
        return True

    except Exception as e:
        print("❌ Error:", e)
        return False

# STOCK CALCULATION
def get_available_stock(stock_in_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Total Stock In
    cursor.execute("SELECT bundle_quantity FROM stock_in WHERE id=%s", (stock_in_id,))
    stock = cursor.fetchone()
    total_stock = stock['bundle_quantity'] if stock else 0

    # Total Issued to Dyeing for this stock_in_id
    cursor.execute("SELECT SUM(issued_quantity) as issued FROM send_dyeing WHERE stock_in_id=%s", (stock_in_id,))
    issued = cursor.fetchone()['issued'] or 0

    # Total Returned for this stock_in_id
    cursor.execute("""
        SELECT SUM(return_quantity) as returned 
        FROM return_dyeing 
        WHERE send_dyeing_id IN (
            SELECT id FROM send_dyeing WHERE stock_in_id=%s
        )
    """, (stock_in_id,))
    returned = cursor.fetchone()['returned'] or 0

    # ✅ Total Sold from Stock Out for this thread+size
    # Get thread_name and size from stock_in
    cursor.execute("SELECT thread_name, size FROM stock_in WHERE id=%s", (stock_in_id,))
    row = cursor.fetchone()
    if row:
        thread = row['thread_name']
        size = row['size']
        cursor.execute("""
            SELECT SUM(bundle_quantity) as sold 
            FROM stock_out 
            WHERE thread_name=%s AND size=%s
        """, (thread, size))
        sold = cursor.fetchone()['sold'] or 0
    else:
        sold = 0

    cursor.close()
    conn.close()

    # Available = Total - Issued + Returned - Sold
    return total_stock - issued + returned - sold

if __name__ == "__main__":
    init_database()
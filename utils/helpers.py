import random
from datetime import datetime
from database import get_connection

def generate_batch_id():
    """Generate unique Batch ID for dyeing"""
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = random.randint(1000, 9999)
    batch_id = f"DYE-{date_part}-{random_part}"
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT batch_id FROM send_dyeing WHERE batch_id = %s", (batch_id,))
        if cursor.fetchone():
            return generate_batch_id()
        cursor.close()
        conn.close()
    except:
        pass
    
    return batch_id

def generate_so_number():
    """Generate Sales Order Number"""
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = random.randint(1, 999)
    so_number = f"SO-{date_part}-{random_part:03d}"
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT so_number FROM stock_out WHERE so_number = %s", (so_number,))
        if cursor.fetchone():
            return generate_so_number()
        cursor.close()
        conn.close()
    except:
        pass
    
    return so_number
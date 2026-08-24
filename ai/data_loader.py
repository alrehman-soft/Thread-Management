import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class DataLoader:
    """Load and prepare data from database for AI models"""
    
    def __init__(self):
        self.conn = None
        self.stock_data = None
        self.sales_data = None
        self.dyeing_sent = None
        self.dyeing_returned = None
        self.supplier_data = None
        self.customer_data = None
        self._debug = False
    
    def debug_print(self, msg):
        if self._debug:
            print(f"[DEBUG] {msg}")
    
    def load_all_data(self):
        """Load all required data from database"""
        # self.debug_print("Loading all data from database...")
        self.load_stock_in()
        self.load_stock_out()
        self.load_send_dyeing()
        self.load_return_dyeing()
        self.load_suppliers()
        self.load_customers()
        
        self.debug_print(f"Stock In: {len(self.stock_data) if self.stock_data is not None else 0} records")
        self.debug_print(f"Sales: {len(self.sales_data) if self.sales_data is not None else 0} records")
        self.debug_print(f"Customers: {len(self.customer_data) if self.customer_data is not None else 0} records")
        self.debug_print(f"Suppliers: {len(self.supplier_data) if self.supplier_data is not None else 0} records")
        
        return self
    
    def load_stock_in(self):
        """Load stock_in data using direct cursor"""
        try:
            self.debug_print("Loading stock_in...")
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, po_number, date, supplier_name,
                    phone, email, supplier_cnic, company_name,
                    thread_name, size, bundle_quantity, 
                    bundle_price, total_price, paid_amount, balance,
                    status, created_at
                FROM stock_in
                ORDER BY date
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                data = []
                for row in rows:
                    data.append({
                        'id': row['id'],
                        'po_number': row['po_number'],
                        'date': row['date'],
                        'supplier_name': row['supplier_name'],
                        'phone': row['phone'],
                        'email': row['email'],
                        'supplier_cnic': row['supplier_cnic'],
                        'company_name': row['company_name'],
                        'thread_name': row['thread_name'],
                        'size': row['size'],
                        'bundle_quantity': row['bundle_quantity'],
                        'bundle_price': row['bundle_price'],
                        'total_price': row['total_price'],
                        'paid_amount': row['paid_amount'],
                        'balance': row['balance'],
                        'status': row['status'],
                        'created_at': row['created_at']
                    })
                
                self.stock_data = pd.DataFrame(data)
                self.debug_print(f"Raw stock_in records: {len(self.stock_data)}")
                self.stock_data['date'] = pd.to_datetime(self.stock_data['date'])
                self.debug_print(f"Stock_in after date parse: {len(self.stock_data)}")
                
                if len(self.stock_data) > 0:
                    self.debug_print(f"Sample: {self.stock_data.iloc[0].to_dict()}")
            else:
                self.debug_print("No stock_in records found!")
                self.stock_data = pd.DataFrame()
            
        except Exception as e:
            print(f"Error loading stock_in: {e}")
            import traceback
            traceback.print_exc()
            self.stock_data = pd.DataFrame()
    
    def load_stock_out(self):
        """Load stock_out data using direct cursor"""
        try:
            self.debug_print("Loading stock_out...")
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, so_number, date, customer_name,
                    thread_name, size, color, bundle_quantity,
                    bundle_price, total_bundle_price, discount,
                    final_total_price, issued_by, created_at
                FROM stock_out
                ORDER BY date
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                data = []
                for row in rows:
                    data.append({
                        'id': row['id'],
                        'so_number': row['so_number'],
                        'date': row['date'],
                        'customer_name': row['customer_name'],
                        'thread_name': row['thread_name'],
                        'size': row['size'],
                        'color': row['color'],
                        'bundle_quantity': row['bundle_quantity'],
                        'bundle_price': row['bundle_price'],
                        'total_bundle_price': row['total_bundle_price'],
                        'discount': row['discount'],
                        'final_total_price': row['final_total_price'],
                        'issued_by': row['issued_by'],
                        'created_at': row['created_at']
                    })
                
                self.sales_data = pd.DataFrame(data)
                self.debug_print(f"Raw sales records: {len(self.sales_data)}")
                
                # Parse dates
                self.sales_data['date'] = pd.to_datetime(self.sales_data['date'])
                self.debug_print(f"Sales after date parse: {len(self.sales_data)}")
                
                if len(self.sales_data) > 0:
                    self.debug_print(f"Sample: {self.sales_data.iloc[0].to_dict()}")
            else:
                self.debug_print("No sales records found!")
                self.sales_data = pd.DataFrame()
            
        except Exception as e:
            print(f"Error loading stock_out: {e}")
            import traceback
            traceback.print_exc()
            self.sales_data = pd.DataFrame()
    
    def load_send_dyeing(self):
        """Load send_dyeing data"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, batch_id, date, stock_in_id,
                    thread_name, size, issued_quantity,
                    dyeing_info, sender, receiver, status,
                    created_at
                FROM send_dyeing
                ORDER BY date
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                data = []
                for row in rows:
                    data.append({
                        'id': row['id'],
                        'batch_id': row['batch_id'],
                        'date': row['date'],
                        'stock_in_id': row['stock_in_id'],
                        'thread_name': row['thread_name'],
                        'size': row['size'],
                        'issued_quantity': row['issued_quantity'],
                        'dyeing_info': row['dyeing_info'],
                        'sender': row['sender'],
                        'receiver': row['receiver'],
                        'status': row['status'],
                        'created_at': row['created_at']
                    })
                
                self.dyeing_sent = pd.DataFrame(data)
                self.dyeing_sent['date'] = pd.to_datetime(self.dyeing_sent['date'])
            else:
                self.dyeing_sent = pd.DataFrame()
            
        except Exception as e:
            print(f"Error loading send_dyeing: {e}")
            self.dyeing_sent = pd.DataFrame()
    
    def load_return_dyeing(self):
        """Load return_dyeing data"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, date, send_dyeing_id, batch_id,
                    thread_name, size, color, issued_quantity,
                    return_quantity, dyeing_info, sender, receiver,
                    created_at
                FROM return_dyeing
                ORDER BY date
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                data = []
                for row in rows:
                    data.append({
                        'id': row['id'],
                        'date': row['date'],
                        'send_dyeing_id': row['send_dyeing_id'],
                        'batch_id': row['batch_id'],
                        'thread_name': row['thread_name'],
                        'size': row['size'],
                        'color': row['color'],
                        'issued_quantity': row['issued_quantity'],
                        'return_quantity': row['return_quantity'],
                        'dyeing_info': row['dyeing_info'],
                        'sender': row['sender'],
                        'receiver': row['receiver'],
                        'created_at': row['created_at']
                    })
                
                self.dyeing_returned = pd.DataFrame(data)
                self.dyeing_returned['date'] = pd.to_datetime(self.dyeing_returned['date'])
            else:
                self.dyeing_returned = pd.DataFrame()
            
        except Exception as e:
            print(f"Error loading return_dyeing: {e}")
            self.dyeing_returned = pd.DataFrame()
    
    def load_suppliers(self):
        """Load unique suppliers from stock_in"""
        if self.stock_data is not None and not self.stock_data.empty:
            # All columns now exist in stock_in
            columns_needed = ['supplier_name', 'phone', 'email', 'company_name']
            available_cols = [col for col in columns_needed if col in self.stock_data.columns]
            
            if available_cols:
                self.supplier_data = self.stock_data[available_cols].drop_duplicates()
                self.debug_print(f"Suppliers loaded: {len(self.supplier_data)}")
            else:
                self.supplier_data = pd.DataFrame()
                self.debug_print("No supplier columns found in stock_data")
        else:
            self.supplier_data = pd.DataFrame()
            self.debug_print("No stock data to load suppliers")
    
    def load_customers(self):
        """Load unique customers from stock_out"""
        if self.sales_data is not None and not self.sales_data.empty:
            if 'customer_name' in self.sales_data.columns:
                self.customer_data = self.sales_data[['customer_name']].drop_duplicates()
                self.debug_print(f"Customers loaded: {len(self.customer_data)}")
            else:
                self.customer_data = pd.DataFrame()
                self.debug_print("No customer_name column in sales_data")
        else:
            self.customer_data = pd.DataFrame()
            self.debug_print("No sales data to load customers")
    
    def get_daily_sales(self, thread_name=None, size=None):
        """Get daily sales aggregated by thread and size"""
        if self.sales_data is None or self.sales_data.empty:
            self.debug_print("No sales data available for daily sales")
            return pd.DataFrame()
        
        df = self.sales_data.copy()
        
        if thread_name:
            df = df[df['thread_name'] == thread_name]
        if size:
            df = df[df['size'] == size]
        
        if df.empty:
            self.debug_print(f"No sales data for thread={thread_name}, size={size}")
            return pd.DataFrame()
        
        daily = df.groupby(['date', 'thread_name', 'size'])['bundle_quantity'].sum().reset_index()
        self.debug_print(f"Daily sales: {len(daily)} records")
        return daily
    
    def get_current_stock_balance(self):
        """Get current stock balance per thread + size"""
        from database import get_available_stock
        
        if self.stock_data is None or self.stock_data.empty:
            self.debug_print("No stock data available for balance calculation")
            return pd.DataFrame()
        
        results = []
        self.debug_print(f"Calculating stock balance for {len(self.stock_data)} stock records...")
        
        for idx, row in self.stock_data.iterrows():
            stock_id = row['id']
            try:
                available = get_available_stock(stock_id)
                results.append({
                    'thread_name': row['thread_name'],
                    'size': row['size'],
                    'total_received': row['bundle_quantity'],
                    'available': available,
                    'supplier': row['supplier_name']
                })
            except Exception as e:
                self.debug_print(f"Error getting stock for id {stock_id}: {e}")
                continue
        
        self.debug_print(f"Stock balance calculated for {len(results)} records")
        return pd.DataFrame(results)
    
    def get_product_demand_history(self, days=90):
        """Get historical demand per product"""
        if self.sales_data is None or self.sales_data.empty:
            return pd.DataFrame()
        
        cutoff = datetime.now() - timedelta(days=days)
        df = self.sales_data[self.sales_data['date'] >= cutoff].copy()
        
        if df.empty:
            return pd.DataFrame()
        
        demand = df.groupby(['date', 'thread_name', 'size'])['bundle_quantity'].sum().reset_index()
        demand.columns = ['date', 'thread', 'size', 'quantity']
        
        return demand
    
    def get_suppliers_for_thread(self, thread_name):
        """Get suppliers who supply a specific thread"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT supplier_name, phone, company_name 
                FROM stock_in 
                WHERE thread_name = %s
            """, (thread_name,))
            suppliers = cursor.fetchall()
            conn.close()
            return suppliers
        except:
            return []


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing DataLoader...")
    print("=" * 60)
    
    loader = DataLoader()
    loader.load_all_data()
    
    print("\n" + "=" * 60)
    print("Current Stock Balance:")
    print("=" * 60)
    stock = loader.get_current_stock_balance()
    if not stock.empty:
        print(stock.to_string())
        print(f"\n✅ Total Available Stock: {stock['available'].sum():.0f} bundles")
        print(f"✅ Records: {len(stock)}")
    else:
        print("❌ No stock data available!")
        print("Check if database has data and connection is working.")
    
    # Show sales data
    print("\n" + "=" * 60)
    print("Sales Data:")
    print("=" * 60)
    if loader.sales_data is not None and not loader.sales_data.empty:
        print(loader.sales_data[['date', 'thread_name', 'size', 'bundle_quantity']].to_string())
    else:
        print("No sales data available.")
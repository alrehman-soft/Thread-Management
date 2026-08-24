"""
Feature #4: Anomaly Detection
"""

import pandas as pd
import numpy as np
from datetime import datetime

from .data_loader import DataLoader
from .config import ANOMALY_THRESHOLD

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class AnomalyDetector:
    """Detect unusual patterns in inventory transactions"""
    
    def __init__(self):
        self.loader = DataLoader()
        self.loader.load_all_data()
        self.alerts = []
    
    def detect_sales_anomalies(self):
        """Detect unusual sales patterns"""
        if self.loader.sales_data is None or self.loader.sales_data.empty:
            return []
        
        df = self.loader.sales_data.copy()
        daily_sales = df.groupby('date')['bundle_quantity'].sum().reset_index()
        daily_sales.columns = ['date', 'total_sales']
        
        if len(daily_sales) < 7:
            return []
        
        mean = daily_sales['total_sales'].mean()
        std = daily_sales['total_sales'].std()
        
        if std == 0:
            return []
        
        daily_sales['z_score'] = (daily_sales['total_sales'] - mean) / std
        anomalies = daily_sales[abs(daily_sales['z_score']) > ANOMALY_THRESHOLD]
        
        alerts = []
        for _, row in anomalies.iterrows():
            alerts.append({
                'type': 'sales_anomaly',
                'date': row['date'],
                'total_sales': row['total_sales'],
                'z_score': row['z_score'],
                'severity': 'high' if abs(row['z_score']) > 3 else 'medium',
                'message': f"Unusual sales on {row['date'].strftime('%Y-%m-%d')}: {row['total_sales']} bundles"
            })
        
        return alerts
    
    def detect_stock_mismatch(self):
        """Detect mismatches in stock movement"""
        if self.loader.stock_data is None or self.loader.stock_data.empty:
            return []
        
        alerts = []
        
        for _, row in self.loader.stock_data.iterrows():
            stock_id = row['id']
            thread = row['thread_name']
            size = row['size']
            total_received = row['bundle_quantity']
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT SUM(bundle_quantity) as total 
                    FROM stock_out 
                    WHERE thread_name = %s AND size = %s
                """, (thread, size))
                sold_qty = cursor.fetchone()['total'] or 0
                conn.close()
                
                if sold_qty > total_received * 1.1:  # 10% tolerance
                    alerts.append({
                        'type': 'stock_mismatch',
                        'thread': thread,
                        'size': size,
                        'total_received': total_received,
                        'total_sold': sold_qty,
                        'severity': 'high',
                        'message': f"Stock mismatch for {thread} ({size}): Sold ({sold_qty}) > Received ({total_received})"
                    })
            except:
                pass
        
        return alerts
    
    def run_full_scan(self):
        """Run all anomaly detection checks"""
        all_alerts = []
        all_alerts.extend(self.detect_sales_anomalies())
        all_alerts.extend(self.detect_stock_mismatch())
        
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        all_alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        self.alerts = all_alerts
        return all_alerts
from .data_loader import DataLoader
from .demand_forecast import DemandForecaster
from .config import SAFETY_STOCK_DAYS, REORDER_LEAD_TIME_DAYS
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class ReorderEngine:
    """Smart reorder recommendations based on demand and lead time"""
    
    def __init__(self):
        self.loader = DataLoader()
        self.loader.load_all_data()
        self.forecaster = DemandForecaster()
    
    def get_supplier_info(self, thread_name):
        """Get all suppliers for a thread with their performance"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    supplier_name,
                    COUNT(*) as order_count,
                    AVG(bundle_price) as avg_price,
                    SUM(bundle_quantity) as total_supplied
                FROM stock_in
                WHERE thread_name = %s
                GROUP BY supplier_name
            """, (thread_name,))
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []
    
    def recommend_order(self, thread, size):
        """Generate order recommendation for a specific product"""
        forecast = self.forecaster.forecast_product(thread, size)
        
        if forecast['status'] != 'success':
            return {
                'status': 'error',
                'message': forecast.get('message', 'Unable to generate recommendation')
            }
        
        stock_df = self.loader.get_current_stock_balance()
        current_stock = stock_df[
            (stock_df['thread_name'] == thread) & 
            (stock_df['size'] == size)
        ]
        
        available = current_stock['available'].sum() if not current_stock.empty else 0
        
        daily_demand = forecast['average_daily_demand']
        lead_time_demand = daily_demand * REORDER_LEAD_TIME_DAYS
        safety_stock = daily_demand * SAFETY_STOCK_DAYS
        reorder_point = lead_time_demand + safety_stock
        
        if available < reorder_point:
            days_to_cover = REORDER_LEAD_TIME_DAYS + SAFETY_STOCK_DAYS + 7
            recommended_qty = max(
                daily_demand * days_to_cover - available,
                10
            )
        else:
            recommended_qty = 0
        
        # Get suppliers
        suppliers = self.get_supplier_info(thread)
        best_supplier = suppliers[0] if suppliers else None
        
        return {
            'status': 'success',
            'thread': thread,
            'size': size,
            'current_stock': available,
            'daily_demand': daily_demand,
            'lead_time_demand': lead_time_demand,
            'safety_stock': safety_stock,
            'reorder_point': reorder_point,
            'recommended_quantity': recommended_qty,
            'best_supplier': best_supplier,
            'urgency': 'high' if available < safety_stock else 'medium' if available < reorder_point else 'low'
        }
    
    def get_all_recommendations(self):
        products = set()

        # Sales se products
        if self.loader.sales_data is not None and not self.loader.sales_data.empty:
            for _, row in self.loader.sales_data[['thread_name', 'size']].drop_duplicates().iterrows():
                thread = row['thread_name']
                size = row['size']

                if thread and size:
                    products.add((thread, size))

        # Stock se products
        stock_df = self.loader.get_current_stock_balance()

        if stock_df is not None and not stock_df.empty:
            for _, row in stock_df[['thread_name', 'size']].drop_duplicates().iterrows():
                thread = row['thread_name']
                size = row['size']

                if thread and size:
                    products.add((thread, size))

        recommendations = []

        for thread, size in products:

            # Current stock
            current_stock = stock_df[
                (stock_df['thread_name'] == thread) &
                (stock_df['size'] == size)
            ]

            available = (
                current_stock['available'].sum()
                if not current_stock.empty else 0
            )

            # Try AI forecast
            forecast = self.forecaster.forecast_product(thread, size)

            if forecast['status'] == 'success':

                daily_demand = forecast['average_daily_demand']

                lead_time_demand = daily_demand * REORDER_LEAD_TIME_DAYS
                safety_stock = daily_demand * SAFETY_STOCK_DAYS
                reorder_point = lead_time_demand + safety_stock

            else:
                # No sufficient sales history
                # Still create reorder alert for zero/low stock

                daily_demand = 0
                lead_time_demand = 0
                safety_stock = 0

                # Basic low-stock threshold
                reorder_point = 10

            # Reorder if stock is low
            if available <= reorder_point:

                if daily_demand > 0:
                    days_to_cover = (
                        REORDER_LEAD_TIME_DAYS +
                        SAFETY_STOCK_DAYS +
                        7
                    )

                    recommended_qty = max(
                        daily_demand * days_to_cover - available,
                        10
                    )

                else:
                    # No sales history
                    # Minimum reorder quantity
                    recommended_qty = 10

                if available <= 0:
                    urgency = 'high'
                elif available < reorder_point:
                    urgency = 'medium'
                else:
                    urgency = 'low'

                suppliers = self.get_supplier_info(thread)
                best_supplier = suppliers[0] if suppliers else None

                recommendations.append({
                    'status': 'success',
                    'thread': thread,
                    'size': size,
                    'current_stock': available,
                    'daily_demand': daily_demand,
                    'lead_time_demand': lead_time_demand,
                    'safety_stock': safety_stock,
                    'reorder_point': reorder_point,
                    'recommended_quantity': recommended_qty,
                    'best_supplier': best_supplier,
                    'urgency': urgency
                })

        urgency_order = {
            'high': 0,
            'medium': 1,
            'low': 2
        }

        recommendations.sort(
            key=lambda x: urgency_order.get(x['urgency'], 3)
        )

        return recommendations
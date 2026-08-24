import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
from .data_loader import DataLoader
from .config import FORECAST_DAYS, HISTORY_DAYS, MIN_HISTORY_DAYS
from statsmodels.tsa.holtwinters import ExponentialSmoothing


class DemandForecaster:
    """Predict future demand for each thread + size combination"""
    
    def __init__(self):
        self.loader = DataLoader()
        self.loader.load_all_data()
        self.predictions = {}
    
    def prepare_ts_data(self, thread, size):
        df = self.loader.get_daily_sales(thread, size)
        
        if df.empty:
            return None
        
        # Ensure date is datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        if df.empty:
            return None
        
        df = df.set_index('date')
        
        # Resample to daily, fill missing with 0
        full_range = pd.date_range(start=df.index.min(),
            end=df.index.max(),freq='D')
        quantity = df['bundle_quantity'].reindex(full_range, fill_value=0)

        df = pd.DataFrame({
            'date': full_range,
            'thread': thread,
            'size': size,
            'quantity': quantity.values
        })
        
        return df
    
    def forecast_holtwinters(self, series, days=FORECAST_DAYS):
        """Forecast using Holt-Winters Exponential Smoothing"""
        try:
            if len(series) < 14:
                return None
            model = ExponentialSmoothing(
                series,
                trend='add',
                seasonal='add',
                seasonal_periods=7
            )
            fitted = model.fit()
            forecast = fitted.forecast(days)
            return forecast.tolist()
        except Exception as e:
            return None
    
    def forecast_product(self, thread, size):
        """Full forecasting pipeline for a single product"""
        df = self.prepare_ts_data(thread, size)
        
        if df is None or len(df) < MIN_HISTORY_DAYS:
            return {
                'thread': thread,
                'size': size,
                'status': 'insufficient_data',
                'message': f'Need at least {MIN_HISTORY_DAYS} days of data'
            }
        
        train = df.tail(HISTORY_DAYS).copy()
        series = train['quantity'].values
        
        # Try forecasting
        forecast = self.forecast_holtwinters(series)
        
        if forecast is None:
            # Fallback: simple moving average
            avg = np.mean(series[-7:]) if len(series) >= 7 else np.mean(series)
            forecast = [max(0, avg)] * FORECAST_DAYS
        
        # Generate dates
        last_date = df['date'].max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(FORECAST_DAYS)]
        
        result = {
            'thread': thread,
            'size': size,
            'status': 'success',
            'dates': future_dates,
            'forecast': forecast,
            'average_daily_demand': np.mean(series[-30:]) if len(series) >= 30 else np.mean(series),
            'total_forecast_demand': sum(forecast),
            'last_30_days_demand': sum(series[-30:]) if len(series) >= 30 else sum(series),
            'trend': 'increasing' if forecast[-1] > forecast[0] else 'decreasing' if forecast[-1] < forecast[0] else 'stable'
        }
        
        return result
    
    def forecast_all_products(self):
        """Forecast demand for all products"""
        if self.loader.sales_data is None or self.loader.sales_data.empty:
            return {}
        
        products = self.loader.sales_data[['thread_name', 'size']].drop_duplicates()
        
        results = {}
        for _, row in products.iterrows():
            thread = row['thread_name']
            size = row['size']
            if thread and size:
                key = f"{thread}|{size}"
                results[key] = self.forecast_product(thread, size)
        
        self.predictions = results
        return results
    
    def get_low_stock_alerts(self, threshold_days=5):
        """Get products that will run out within threshold_days"""
        stock_df = self.loader.get_current_stock_balance()
        
        if stock_df.empty:
            return []
        
        if not self.predictions:
            self.forecast_all_products()
        
        alerts = []
        for _, row in stock_df.iterrows():
            thread = row['thread_name']
            size = row['size']
            available = row['available']
            
            key = f"{thread}|{size}"
            if key in self.predictions:
                pred = self.predictions[key]
                if pred['status'] == 'success':
                    daily_demand = pred['average_daily_demand']
                    if daily_demand > 0:
                        days_left = available / daily_demand
                        if days_left < threshold_days:
                            alerts.append({
                                'thread': thread,
                                'size': size,
                                'available': available,
                                'daily_demand': daily_demand,
                                'days_left': days_left,
                                'recommended_order': daily_demand * (threshold_days + 7) - available
                            })
        
        return sorted(alerts, key=lambda x: x['days_left'])
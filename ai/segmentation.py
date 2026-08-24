import pandas as pd
from datetime import datetime
from .data_loader import DataLoader


class Segmenter:
    """Segment customers and suppliers using RFM analysis"""
    
    def __init__(self):
        self.loader = DataLoader()
        self.loader.load_all_data()
    
    def calculate_rfm_customers(self):
        """Calculate RFM scores for customers"""

        if self.loader.sales_data is None or self.loader.sales_data.empty:
            return pd.DataFrame()

        df = self.loader.sales_data.copy()

        # Remove empty customer names
        df = df.dropna(subset=['customer_name'])

        if df.empty:
            return pd.DataFrame()

        today = datetime.now()

        rfm = df.groupby('customer_name').agg({
            'date': lambda x: (today - x.max()).days,
            'so_number': 'count',
            'final_total_price': 'sum'
        }).reset_index()

        rfm.columns = [
            'customer',
            'recency',
            'frequency',
            'monetary'
        ]

        # Remove customers with zero/negative sales
        rfm = rfm[rfm['monetary'] > 0].copy()

        if rfm.empty:
            return pd.DataFrame()

        # Number of customers
        count = len(rfm)

        # RFM scoring
        if count >= 4:

            rfm['r_score'] = pd.qcut(
                rfm['recency'].rank(method='first'),
                q=4,
                labels=[4, 3, 2, 1]
            )

            rfm['f_score'] = pd.qcut(
                rfm['frequency'].rank(method='first'),
                q=4,
                labels=[1, 2, 3, 4]
            )

            rfm['m_score'] = pd.qcut(
                rfm['monetary'].rank(method='first'),
                q=4,
                labels=[1, 2, 3, 4]
            )

        else:
            # If less than 4 customers, don't use qcut
            rfm['r_score'] = 3
            rfm['f_score'] = 3
            rfm['m_score'] = 3

        # Convert scores to numbers
        rfm['r_score'] = rfm['r_score'].astype(int)
        rfm['f_score'] = rfm['f_score'].astype(int)
        rfm['m_score'] = rfm['m_score'].astype(int)

        # Total RFM score
        rfm['rfm_score'] = (
            rfm['r_score'] +
            rfm['f_score'] +
            rfm['m_score']
        )

        # Customer segment
        def get_segment(row):

            if row['rfm_score'] >= 10:
                return 'Gold'

            elif row['rfm_score'] >= 7:
                return 'Silver'

            elif row['rfm_score'] >= 4:
                return 'Bronze'

            else:
                return 'Lead'

        rfm['segment'] = rfm.apply(get_segment, axis=1)

        return rfm
    
    def calculate_rfm_suppliers(self):
        """Calculate RFM-like scores for suppliers"""

        if self.loader.stock_data is None or self.loader.stock_data.empty:
            return pd.DataFrame()

        df = self.loader.stock_data.copy()

        # Remove empty supplier names
        df = df.dropna(subset=['supplier_name'])

        if df.empty:
            return pd.DataFrame()

        today = datetime.now()

        rfm = df.groupby('supplier_name').agg({
            'date': lambda x: (today - x.max()).days,
            'po_number': 'count',
            'total_price': 'sum'
        }).reset_index()

        rfm.columns = [
            'supplier',
            'recency',
            'frequency',
            'monetary'
        ]

        rfm = rfm[rfm['monetary'] > 0].copy()

        if rfm.empty:
            return pd.DataFrame()

        count = len(rfm)

        if count >= 4:

            rfm['r_score'] = pd.qcut(
                rfm['recency'].rank(method='first'),
                q=4,
                labels=[4, 3, 2, 1]
            )

            rfm['f_score'] = pd.qcut(
                rfm['frequency'].rank(method='first'),
                q=4,
                labels=[1, 2, 3, 4]
            )

            rfm['m_score'] = pd.qcut(
                rfm['monetary'].rank(method='first'),
                q=4,
                labels=[1, 2, 3, 4]
            )

        else:
            rfm['r_score'] = 3
            rfm['f_score'] = 3
            rfm['m_score'] = 3

        rfm['r_score'] = rfm['r_score'].astype(int)
        rfm['f_score'] = rfm['f_score'].astype(int)
        rfm['m_score'] = rfm['m_score'].astype(int)

        rfm['rfm_score'] = (
            rfm['r_score'] +
            rfm['f_score'] +
            rfm['m_score']
        )

        def get_segment(row):

            if row['rfm_score'] >= 10:
                return 'Strategic Partner'

            elif row['rfm_score'] >= 7:
                return 'Preferred Supplier'

            elif row['rfm_score'] >= 4:
                return 'Regular Supplier'

            else:
                return 'New/Trial'

        rfm['segment'] = rfm.apply(get_segment, axis=1)

        return rfm
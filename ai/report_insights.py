import pandas as pd
from .data_loader import DataLoader
from .config import LLM_MODEL


class ReportInsights:    
    def __init__(self):
        self.loader = DataLoader()
        self.loader.load_all_data()
        self.llm_available = self.check_ollama()
    
    def check_ollama(self):
        """Check if Ollama is available"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 11434))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_sales_insights(self):
        """Generate insights from sales data"""
        if self.loader.sales_data is None or self.loader.sales_data.empty:
            return "No sales data available for insights."
        
        df = self.loader.sales_data.copy()
        
        # Top selling threads
        top_threads = df.groupby('thread_name')['bundle_quantity'].sum().sort_values(ascending=False)
        
        # Top selling sizes
        top_sizes = df.groupby('size')['bundle_quantity'].sum().sort_values(ascending=False)
        
        # Monthly sales
        df['month'] = df['date'].dt.month
        monthly_sales = df.groupby('month')['bundle_quantity'].sum()
        
        # Total revenue
        total_revenue = df['final_total_price'].sum()
        
        insights = {
            'top_selling_thread': top_threads.index[0] if not top_threads.empty else 'N/A',
            'top_selling_thread_qty': int(top_threads.iloc[0]) if not top_threads.empty else 0,
            'top_selling_size': top_sizes.index[0] if not top_sizes.empty else 'N/A',
            'top_selling_size_qty': int(top_sizes.iloc[0]) if not top_sizes.empty else 0,
            'total_revenue': float(total_revenue),
            'total_sales': int(df['bundle_quantity'].sum()),
            'total_orders': len(df),
            'best_month': int(monthly_sales.idxmax()) if not monthly_sales.empty else 0,
            'best_month_sales': int(monthly_sales.max()) if not monthly_sales.empty else 0
        }
        
        return insights
    
    def get_supplier_insights(self):
        """Generate insights from supplier data"""
        if self.loader.stock_data is None or self.loader.stock_data.empty:
            return "No supplier data available for insights."
        
        df = self.loader.stock_data.copy()
        
        # Supplier performance
        supplier_stats = df.groupby('supplier_name').agg({
            'bundle_quantity': 'sum',
            'bundle_price': 'mean',
            'po_number': 'count'
        }).reset_index()
        
        supplier_stats.columns = ['supplier', 'total_quantity', 'avg_price', 'order_count']
        
        # Find best and worst suppliers
        if not supplier_stats.empty:
            cheapest = supplier_stats.loc[supplier_stats['avg_price'].idxmin()]
            most_expensive = supplier_stats.loc[supplier_stats['avg_price'].idxmax()]
            most_supplied = supplier_stats.loc[supplier_stats['total_quantity'].idxmax()]
            
            insights = {
                'cheapest_supplier': cheapest['supplier'],
                'cheapest_price': float(cheapest['avg_price']),
                'most_expensive_supplier': most_expensive['supplier'],
                'most_expensive_price': float(most_expensive['avg_price']),
                'most_supplied_supplier': most_supplied['supplier'],
                'most_supplied_qty': int(most_supplied['total_quantity']),
                'total_suppliers': len(supplier_stats),
                'avg_price_all': float(supplier_stats['avg_price'].mean())
            }
            
            # Calculate potential savings
            if cheapest['avg_price'] < supplier_stats['avg_price'].mean():
                savings_percent = ((supplier_stats['avg_price'].mean() - cheapest['avg_price']) / supplier_stats['avg_price'].mean()) * 100
                insights['potential_savings'] = round(savings_percent, 1)
            else:
                insights['potential_savings'] = 0
            
            return insights
        
        return "No supplier insights available."
    
    def get_stock_insights(self):
        """Generate insights from stock data"""
        stock = self.loader.get_current_stock_balance()
        
        if stock.empty:
            return "No stock data available for insights."
        
        # Convert available to numeric
        stock['available'] = pd.to_numeric(stock['available'], errors='coerce')
        stock = stock.dropna(subset=['available'])
        
        if stock.empty:
            return "No stock data available."
        
        # Low stock items
        low_stock = stock[stock['available'] < 50]
        
        # High stock items
        high_stock = stock[stock['available'] > 200]
        
        insights = {
            'total_products': len(stock),
            'total_available': int(stock['available'].sum()),
            'low_stock_count': len(low_stock),
            'low_stock_items': low_stock[['thread_name', 'size', 'available']].to_dict('records'),
            'high_stock_count': len(high_stock),
            'high_stock_items': high_stock[['thread_name', 'size', 'available']].to_dict('records'),
            'avg_stock': float(stock['available'].mean())
        }
        return insights
    
    def generate_insights_text(self):
        sales = self.get_sales_insights()
        suppliers = self.get_supplier_insights()
        stock = self.get_stock_insights()
        
        insights = []
        
        # Sales insights
        if isinstance(sales, dict):
            insights.append(f"📈 **Top Selling Thread**: {sales['top_selling_thread']} with {sales['top_selling_thread_qty']} bundles sold")
            insights.append(f"📏 **Top Selling Size**: {sales['top_selling_size']} with {sales['top_selling_size_qty']} bundles sold")
            insights.append(f"💰 **Total Revenue**: Rs. {sales['total_revenue']:,.2f}")
            insights.append(f"📦 **Total Sales**: {sales['total_sales']} bundles")
            
            if sales['best_month'] > 0:
                insights.append(f"📅 **Best Month**: Month {sales['best_month']} with {sales['best_month_sales']} bundles sold")
        
        # Supplier insights
        if isinstance(suppliers, dict):
            insights.append(f"🏢 **Cheapest Supplier**: {suppliers['cheapest_supplier']} (Rs. {suppliers['cheapest_price']:.2f}/bundle)")
            insights.append(f"🏢 **Most Supplied Supplier**: {suppliers['most_supplied_supplier']} with {suppliers['most_supplied_qty']} bundles")
            
            if suppliers.get('potential_savings', 0) > 0:
                insights.append(f"💡 **Potential Savings**: You could save {suppliers['potential_savings']}% by ordering from {suppliers['cheapest_supplier']}")
        
        # Stock insights
        if isinstance(stock, dict):
            insights.append(f"📦 **Total Stock**: {stock['total_available']} bundles across {stock['total_products']} products")
            insights.append(f"📊 **Average Stock**: {stock['avg_stock']:.0f} bundles per product")
            
            if stock['low_stock_count'] > 0:
                insights.append(f"⚠️ **Low Stock Alert**: {stock['low_stock_count']} items are below 50 bundles")
                for item in stock['low_stock_items'][:3]:
                    insights.append(f"   - {item['thread_name']} ({item['size']}): {item['available']} bundles")
            
            if stock['high_stock_count'] > 0:
                insights.append(f"📦 **Overstocked Items**: {stock['high_stock_count']} items are above 200 bundles")
        
        return "\n\n".join(insights)
    
    def generate_llm_insights(self, question="Generate a summary report with insights and recommendations based on the data."):
        """Generate insights using LLM (with fallback)"""
        
        # First try
        text_insights = self.generate_insights_text()
        
        # If LLM is available
        if self.llm_available:
            try:
                # Get data context
                sales = self.get_sales_insights()
                suppliers = self.get_supplier_insights()
                stock = self.get_stock_insights()
                
                context = f"""
Sales Data:
- Top selling thread: {sales.get('top_selling_thread', 'N/A')} with {sales.get('top_selling_thread_qty', 0)} bundles
- Top selling size: {sales.get('top_selling_size', 'N/A')} with {sales.get('top_selling_size_qty', 0)} bundles
- Total revenue: Rs. {sales.get('total_revenue', 0):,.2f}
- Total sales: {sales.get('total_sales', 0)} bundles

Supplier Data:
- Cheapest supplier: {suppliers.get('cheapest_supplier', 'N/A')} at Rs. {suppliers.get('cheapest_price', 0):.2f}/bundle
- Most supplied supplier: {suppliers.get('most_supplied_supplier', 'N/A')}
- Potential savings: {suppliers.get('potential_savings', 0)}%

Stock Data:
- Total available stock: {stock.get('total_available', 0)} bundles
- Low stock items: {stock.get('low_stock_count', 0)}
- Overstocked items: {stock.get('high_stock_count', 0)}
"""
                
                prompt = f"""You are an inventory management expert. Based on the following data, generate a concise business summary with insights and actionable recommendations.

Data:
{context}

Question: {question}

Format your response in Roman Urdu with clear sections:
1. Executive Summary
2. Key Insights
3. Recommendations
4. Action Items

Response:"""
                
                import subprocess
                result = subprocess.run(
                    ['ollama', 'run', LLM_MODEL, prompt],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=30
                )
                
                if result.stdout.strip():
                    return result.stdout.strip()
                else:
                    return text_insights
                    
            except subprocess.TimeoutExpired:
                return text_insights # + "\n\n⏱️ LLM took too long. Showing text insights above."
            except Exception as e:
                return text_insights + f"\n\n❌ Error: {str(e)}"
        
        # ✅ Fallback: Text insights only
        return text_insights
    
    def get_full_report(self):
        """Get complete report with insights"""
        return {
            'sales_insights': self.get_sales_insights(),
            'supplier_insights': self.get_supplier_insights(),
            'stock_insights': self.get_stock_insights(),
            'summary_text': self.generate_insights_text(),
            'llm_report': self.generate_llm_insights()
        }
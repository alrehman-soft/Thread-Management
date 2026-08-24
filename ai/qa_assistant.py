import subprocess, socket, os
from datetime import datetime
import pandas as pd
from .data_loader import DataLoader
from .config import LLM_MODEL


class QAAssistant:
    """Natural language Q&A assistant - Supports English, Urdu & Roman Urdu"""
    
    def __init__(self):
        self.loader = DataLoader()
        self.loader.load_all_data()
        self.llm_available = self.check_ollama()
    
    def find_ollama(self):
        """Find Ollama executable path"""
        possible_paths = [
            r"C:\Users\AL REHMAN\AppData\Local\Programs\Ollama\ollama.exe",
            r"C:\Program Files\Ollama\ollama.exe",
            "ollama"
        ]
        
        user = os.environ.get('USERNAME', '')
        if user:
            possible_paths.insert(0, f"C:\\Users\\{user}\\AppData\\Local\\Programs\\Ollama\\ollama.exe")
        
        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    timeout=2
                )
                if result.returncode == 0:
                    return path
            except:
                continue
        
        return None
    
    def check_ollama(self):
        """Check if Ollama is installed and running"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 11434))
            sock.close()
            
            if result == 0:
                ollama_path = self.find_ollama()
                if not ollama_path:
                    return False
                
                try:
                    result = subprocess.run(
                        [ollama_path, 'list'],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore',
                        timeout=10
                    )
                    if LLM_MODEL in result.stdout:
                        return True
                    else:
                        return False
                except:
                    return False
            else:
                return False
        except:
            return False
    
    def get_context(self):
        """Get current inventory context for LLM"""
        context = "📊 Current Inventory Status:\n"
        
        stock = self.loader.get_current_stock_balance()
        if not stock.empty:
            stock['available'] = pd.to_numeric(stock['available'], errors='coerce')
            stock = stock.dropna(subset=['available'])
            
            if not stock.empty:
                total_stock = stock['available'].sum()
                context += f"• Total Available Stock: {total_stock:.0f} bundles\n"
                
                top = stock.nlargest(5, 'available')
                context += "• Top Stock Items:\n"
                for _, row in top.iterrows():
                    context += f"  - {row['thread_name']} ({row['size']}): {row['available']:.0f} bundles\n"
        
        if self.loader.sales_data is not None and not self.loader.sales_data.empty:
            df = self.loader.sales_data
            last_30 = df[df['date'] >= datetime.now() - pd.Timedelta(days=30)]
            if not last_30.empty:
                total_sales = last_30['bundle_quantity'].sum()
                total_amount = last_30['final_total_price'].sum()
                context += f"• Sales (Last 30 Days): {total_sales:.0f} bundles\n"
                context += f"• Revenue (Last 30 Days): Rs. {total_amount:,.2f}\n"
        
        if self.loader.customer_data is not None and not self.loader.customer_data.empty:
            context += f"• Total Customers: {len(self.loader.customer_data)}\n"
        
        if self.loader.supplier_data is not None and not self.loader.supplier_data.empty:
            context += f"• Total Suppliers: {len(self.loader.supplier_data)}\n"
        
        return context
    
    def query(self, question):
        """Ask a question to the assistant using LLM"""
        if not self.llm_available:
            return "⚠️ LLM not available. Please install Ollama and pull the model.\n\n" + self.get_context()
        
        context = self.get_context()
        
        prompt = f"""You are an inventory management assistant. Answer the question in the same language as the question (English, Urdu, or Roman English).

Context:
{context}

Question: {question}

Answer:"""
        
        try:
            ollama_path = self.find_ollama() or "ollama"
            result = subprocess.run(
                [ollama_path, 'run', LLM_MODEL, prompt],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=120
            )
            
            if result.stdout.strip():
                return result.stdout.strip()
            else:
                return "⚠️ No response from LLM. Please try again."
                
        except subprocess.TimeoutExpired:
            return "⏱️ Request timed out. Please try again."
        except Exception as e:
            return f"Error: {str(e)}\n\n{self.get_context()}"
    
    def quick_query(self, question):
        """Quick query - Supports English, Urdu & Roman Urdu"""
        question_lower = question.lower()
        
        # Load data if not loaded
        if self.loader.sales_data is None or self.loader.sales_data.empty:
            self.loader.load_all_data()
        
        # ============ ROMAN URDU + URDU + ENGLISH KEYWORDS ============
        stock_keywords = [
            'stock', 'available', 'اسٹاک', 'موجودہ', 'بقیہ', 'بقایا', 'بچا',
            'mujooda', 'baqi', 'bacha', 'kya', 'kitna', 'kitni', 'kya hai', 
            'kitna hai', 'bache', 'bachi', 'rakam', 'maujooda',
            'stok', 'stak', 'stuck', 'shok', 'showk', 'shauk'
        ]
        sales_keywords = [
            'sales', 'sold', 'revenue', 'سیلز', 'فروخت', 'آمدنی',
            'bikri', 'farokht', 'amadani', 'bechay', 'bikay', 'bechi'
        ]
        customer_keywords = [
            'customer', 'customers', 'گاہک', 'کسٹمر', 'مشتری',
            'gahak', 'khareedar', 'mushteri', 'gahko'
        ]
        supplier_keywords = [
            'supplier', 'suppliers', 'سپلائر', 'فروش', 'تاجر',
            'farosh', 'tajar'
        ]
        help_keywords = [
            'help', 'what', 'how', 'مدد', 'کیا', 'کیسے',
            'kya', 'kaise', 'kese', 'batana', 'batao', 'dikhana', 'guide'
        ]
        
        # 1. Check for stock query
        if any(kw in question_lower for kw in stock_keywords):
            stock = self.loader.get_current_stock_balance()
            if not stock.empty:
                stock['available'] = pd.to_numeric(stock['available'], errors='coerce')
                stock = stock.dropna(subset=['available'])
                
                if stock.empty:
                    return "Koi stock available nahi hai.\n\nکوئی اسٹاک دستیاب نہیں ہے۔"
                
                # Check if specific thread mentioned
                thread_match = None
                for thread in stock['thread_name'].unique():
                    if thread and (thread.lower() in question_lower or 
                                question_lower in thread.lower()):
                        thread_match = thread
                        break
                
                if thread_match:
                    filtered = stock[stock['thread_name'] == thread_match]
                    response = f"📊 {thread_match} ka stock:\n"
                    for _, row in filtered.iterrows():
                        response += f"  • {row['thread_name']} (Size: {row['size']}): {row['available']:.0f} bundles\n"
                    return response
                else:
                    top = stock.nlargest(5, 'available')
                    response = "📊 Sab se zyada stock wali cheezein:\n"
                    for _, row in top.iterrows():
                        response += f"  • {row['thread_name']} (Size: {row['size']}): {row['available']:.0f} bundles\n"
                    
                    total = stock['available'].sum()
                    response += f"\n📦 Total stock: {total:.0f} bundles"
                    return response
            else:
                return "Koi stock data available nahi hai."
        
        # 2. Check for sales query
        if any(kw in question_lower for kw in sales_keywords):
            if self.loader.sales_data is not None and not self.loader.sales_data.empty:
                df = self.loader.sales_data
                total = df['bundle_quantity'].sum()
                total_amount = df['final_total_price'].sum()
                return f"📈 Total sales: {total:.0f} bundles\n💰 Total revenue: Rs. {total_amount:,.2f}"
            else:
                return "Sales ka koi data available nahi hai."
        
        # 3. Check for customers
        if any(kw in question_lower for kw in customer_keywords):
            if self.loader.customer_data is not None and not self.loader.customer_data.empty:
                return f"👥 Total Customer: {len(self.loader.customer_data)}"
            else:
                return "Customer ka koi data available nahi hai."
        
        # 4. Check for suppliers
        if any(kw in question_lower for kw in supplier_keywords):
            if self.loader.supplier_data is not None and not self.loader.supplier_data.empty:
                return f"🏢 Total suppliers: {len(self.loader.supplier_data)}"
            else:
                return "Suppliers ka koi data available nahi hai."
        
        # 5. Check for help
        if any(kw in question_lower for kw in help_keywords):
            return """🤖 Main in sawalon ka jawab de sakta hoon:

    📦 **Stock ke bare mein:**
    • "stock kya hai?" / "mujooda stock kya hai?"
    • "[name] ka kitna stock hai?"
    • "sab se zyada stock kis cheez ka hai?"

    💰 **Sales ke bare mein:**
    • "Total sales kya hain?"
    • "kitni bikri hui?"

    👥 **Gahakon ke bare mein:**
    • "Total kitne gahak hain?"

    🏢 **Suppliers ke bare mein:**
    • "Total kitne suppliers hain?"

    💡 **English, Urdu ya Roman Urdu mein pooch sakte hain!**
    """
        
        # 6. Try LLM as fallback (supports all languages)
        if self.llm_available:
            return self.query(question)
        
        # 7. Default response
        return """❓ Main aapka sawal samajh nahi paya.

    🤖 Main in sawalon ka jawab de sakta hoon:
    • Stock
    • Sales
    • Gahak (Customers)
    • Suppliers

    Roman Urdu, Urdu ya English mein pooch sakte hain.
    """

# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    assistant = QAAssistant()
    
    print("=" * 50)
    print("Q&A Assistant Test (Roman English Support)")
    print("=" * 50)
    
    questions = [
        "stock kya hai?",
        "mujooda stock kya hai?",
        "China ka kitna stock hai?",
        "Total sales kya hain?",
        "Total kitne customer hain?",
        "suppliers kitne hain?",
        "help"
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {assistant.quick_query(q)}")
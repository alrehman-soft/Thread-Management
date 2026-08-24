import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import threading
# Import AI modules from ai folder
from ai.data_loader import DataLoader
from ai.demand_forecast import DemandForecaster
from ai.reorder_engine import ReorderEngine
from ai.segmentation import Segmenter
from ai.anomaly_detector import AnomalyDetector
from ai.qa_assistant import QAAssistant
from ai.report_insights import ReportInsights


class AIDashboard:
    """AI Features Panel for Dashboard"""
    
    def __init__(self, parent):
        self.parent = parent
        self.loader = DataLoader()
        self.forecaster = DemandForecaster()
        self.engine = ReorderEngine()
        self.segmenter = Segmenter()
        self.detector = AnomalyDetector()
        self.assistant = QAAssistant()
        self.report_insights = ReportInsights()
        self.tts_engine = None
        
    def create_ai_panel(self, parent_frame):
        """Create AI features panel"""
        
        # AI Panel Frame
        ai_frame = tk.LabelFrame(
            parent_frame, 
            text="🤖 AI Intelligence", 
            font=("Segoe UI", 14, "bold"),
            bg="#f4f6f9", 
            fg="#1b4fbf"
        )
        ai_frame.pack(fill="x", padx=20, pady=10)
        
        # Row 1: Quick Stats
        stats_frame = tk.Frame(ai_frame, bg="#f4f6f9")
        stats_frame.pack(fill="x", pady=5)
        
        self.ai_status_label = tk.Label(
            stats_frame,
            text="🟢 AI System: Loading...",
            font=("Segoe UI", 11, "bold"),
            bg="#f4f6f9",
            fg="#047e37"
        )
        self.ai_status_label.pack(side="left", padx=15)
        
        # Load AI data in background
        self.load_data_thread()
        
        # Row 2: Feature Buttons
        btn_frame = tk.Frame(ai_frame, bg="#f4f6f9")
        btn_frame.pack(fill="x", pady=8)
        
        features = [
            ("📊 Demand Forecast", self.show_forecast),
            ("🔄 Reorder Alerts", self.show_reorder_alerts),
            ("👥 Segmentation", self.show_segmentation),
            ("⚠️ Anomalies", self.show_anomalies),
            ("💬 Q&A Assistant", self.show_qa_assistant),
            ("📈 AI Insights", self.show_insights),
        ]
        
        for i, (text, cmd) in enumerate(features):
            btn = tk.Button(btn_frame,text=text,command=cmd,bg="#1b4fbf",
                fg="white",font=("Segoe UI", 10, "bold"),width=18,height=2,
                relief="flat",cursor="hand2")
            btn.grid(row=0, column=i, padx=5, pady=5)
    
    def load_data_thread(self):
        def load():
            try:
                self.loader.load_all_data()
                self.forecaster.forecast_all_products()
                
                # Update status
                self.parent.after(0, lambda: self.ai_status_label.config(
                    text=f"🟢 AI System: {len(self.loader.sales_data)} Sales Records Loaded"
                ))
            except Exception as e:
                error_msg = f"🔴 AI Error: {str(e)[:50]}"
                self.parent.after(0, lambda err=error_msg: self.ai_status_label.config(
                    text=err
                ))
        threading.Thread(target=load, daemon=True).start()
    
    # ============================================================
    # FIX PRONUNCIATION
    # ============================================================
    def fix_pronunciation(self, text):
        """Fix text pronunciation issues - especially sizes like 20/2"""
        
        import re
        
        def fix_size(match):
            return match.group(1) + " slash " + match.group(2)
        
        text = re.sub(r'(\d+)\s*/\s*(\d+)', fix_size, text)
        
        # Replace common abbreviations
        replacements = {
            '20/2': '20 slash 2',
            '20/6': '20 slash 6',
            '40/2': '40 slash 2',
            '40/3': '40 slash 3',
            '50/2': '50 slash 2',
            '60/2': '60 slash 2',
        }
        
        for key, value in replacements.items():
            text = text.replace(key, value)
        
        return text
    
    # CONVERT TO URDU PRONUNCIATION
    def convert_to_urdu_pronunciation(self, text):
        """Convert Roman Urdu text to Urdu script for better pronunciation"""
        
        # Common Roman Urdu to Urdu mappings
        replacements = {
            # Stock related
            'stock': 'اسٹاک',
            'available': 'دستیاب',
            'bundles': 'بنڈلز',
            'bundle': 'بنڈل',
            'sales': 'سیلز',
            'revenue': 'آمدنی',
            'customers': 'گاہک',
            'customer': 'گاہک',
            'suppliers': 'سپلائرز',
            'supplier': 'سپلائر',
            'thread': 'دھاگہ',
            'total': 'کل',
            'current': 'موجودہ',
            'pending': 'زیر التواء',
            'returned': 'واپس',
            'issued': 'جاری',
            'sold': 'فروخت',
            'available stock': 'دستیاب اسٹاک',
            'Total': 'کل',
            'Customer': 'گاہک',
            'mujooda': 'موجودہ',
            'bikri': 'فروخت',
            'amadani': 'آمدنی',
            'farokht': 'فروخت',
            'bechay': 'بیچے',
            'bikay': 'بکے',
            'record': 'ریکارڈ',
            'records': 'ریکارڈز',
            'order': 'آرڈر',
            'orders': 'آرڈرز',
            'pending orders': 'زیر التواء آرڈرز',
            'balance': 'بیلنس',
            'price': 'قیمت',
            'prices': 'قیمتیں',
            'quantity': 'مقدار',
            'quantities': 'مقداریں',
            'payment': 'ادائیگی',
            'payments': 'ادائیگیاں',
            
            # Sizes - Fix pronunciation
            '20 slash 2': 'بیس سلیش تو',
            '20 slash 6': 'بیس سلیش چھے',
            '40 slash 2': 'چالیس سلیش تو',
            '40 slash 3': 'چالیس سلیش تین',
            '50 slash 2': 'پچاس سلیش تو',
            '60 slash 2': 'ساٹھ سلیش تو',
            
            # Company/Thread names
            'China': 'چائنا',
            'Tesla': 'ٹیسلا',
        }
        
        # Sort by length
        for key in sorted(replacements.keys(), key=len, reverse=True):
            text = text.replace(key, replacements[key])
        
        return text

    def clean_text_for_speech(self, text, speak_english=False):
        import re
        
        # Remove emojis and special characters
        text = re.sub(r'[^\w\s\.\,\?\-\!\:\;\(\)\/]', '', text)
        
        if not speak_english:
            replacements = {
                'suppliers': 'suppliers',
                'supplier': 'supplier',
                'customers': 'customers',
                'customer': 'customer',
                'stock': 'stock',
                'bundles': 'bundles',
                'bundle': 'bundle',
                'sales': 'sales',
                'revenue': 'revenue',
                'total': 'total',
                'available': 'available',
                'current': 'current',
                'pending': 'pending',
                'returned': 'returned',
                'issued': 'issued',
                'sold': 'sold',
                'kul': 'kul',
                'gahak': 'gahak',
                'mujooda': 'mujooda',
                'bikri': 'bikri',
                'amadani': 'amadani',
                'farokht': 'farokht',
                'bechay': 'bechay',
                'bikay': 'bikay',
            }
            
            for key, value in replacements.items():
                text = text.replace(key, value)
        
        # Fix size pronunciation
        def fix_size(match):
            return match.group(1) + " slash " + match.group(2)
        
        text = re.sub(r'(\d+)\s*/\s*(\d+)', fix_size, text)
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text
    
    # SPEAK RESPONSE FUNCTION 
    def speak_response(self, text, question=""):
        """Convert text to speech - Zira Female Voice"""
        try:
            import pyttsx3
            import re
            
            # Check if user asked for English
            speak_english = False
            if question and ('english' in question.lower() or 'english mein' in question.lower()):
                speak_english = True
            
            # Initialize TTS engine
            engine = pyttsx3.init()
            
            # Get available voices
            voices = engine.getProperty('voices')
            
            # Set ZIRA (FEMALE VOICE)
            female_voice_found = False
            for voice in voices:
                if 'zira' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    female_voice_found = True
                    break
            
            if not female_voice_found:
                for voice in voices:
                    if 'female' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        female_voice_found = True
                        break
            
            # Set speech rate
            rate = engine.getProperty('rate')
            engine.setProperty('rate', rate - 15)
            
            # CLEAN TEXT FOR SPEECH
            clean_text = self.clean_text_for_speech(text, speak_english)
            
            # Speak in separate thread
            def speak():
                try:
                    engine.say(clean_text)
                    engine.runAndWait()
                except Exception as e:
                    print(f"Speech playback error: {e}")
            
            threading.Thread(target=speak, daemon=True).start()
            
        except Exception as e:
            print(f"Speech error: {e}")
            
    # GET ANSWER AND SPEAK
    def get_answer_and_speak(self, question, update_answer_func):
        """Get answer from AI and speak it (Urdu Female default)"""
        try:
            # Get answer
            if self.assistant.llm_available:
                response = self.assistant.quick_query(question)
            else:
                response = "⚠️ LLM not available. Please install Ollama.\n\n"
                response += self.assistant.get_context()
            
            # Update text
            self.parent.after_idle(lambda: update_answer_func(response))
            
            # Speak the answer
            self.speak_response(response, question)
            
        except Exception as err:
            error_msg = f"❌ Error: {str(err)}"
            self.parent.after_idle(lambda: update_answer_func(error_msg))

    def convert_to_roman_urdu(self, text):
        """Convert Urdu script to Roman Urdu"""
        
        # Common Urdu to Roman Urdu mappings
        replacements = {
            # Question words
            'کیا': 'kya',
            'کتنا': 'kitna',
            'کتنی': 'kitni',
            'کیسے': 'kaise',
            'کہاں': 'kahan',
            'کیوں': 'kyun',
            'کب': 'kab',
            'کون': 'kaun',
            
            # Stock related
            'اسٹاک': 'stock',
            'موجودہ': 'mujooda',
            'دستیاب': 'available',
            'بنڈلز': 'bundles',
            'بنڈل': 'bundle',
            'فروخت': 'bikri',
            'آمدنی': 'amadani',
            'گاہک': 'gahak',
            'کسٹمر': 'customer',
            'مشتری': 'mushteri',
            'سپلائر': 'supplier',
            'تاجر': 'tajar',
            'دھاگہ': 'thread',
            'کل': 'kul',
            'بقیہ': 'baqi',
            'بقایا': 'baqaya',
            'بچا': 'bacha',
            'بچے': 'bache',
            
            # Common words
            'ہے': 'hai',
            'ہیں': 'hain',
            'میں': 'mein',
            'کا': 'ka',
            'کی': 'ki',
            'کے': 'ke',
            'نے': 'ne',
            'سے': 'se',
            'پر': 'par',
            'میں': 'mein',
            'لیے': 'liye',
            'تک': 'tak',
            
            # Numbers
            'ایک': 'ek',
            'دو': 'do',
            'تین': 'teen',
            'چار': 'chaar',
            'پانچ': 'paanch',
            'چھے': 'chhay',
            'سات': 'saat',
            'آٹھ': 'aath',
            'نو': 'nau',
            'دس': 'das',
            'بیس': 'bis',
            'پچاس': 'pachaas',
            'ساٹھ': 'saath',
            'سو': 'so',
            
            # Others
            'چائنا': 'China',
            'ٹیسلا': 'Tesla',
            'ریکارڈ': 'record',
            'آرڈر': 'order',
            'بیلنس': 'balance',
            'قیمت': 'price',
            'مقدار': 'quantity',
            'ادائیگی': 'payment',
        }
        
        # Sort by length (longest first)
        for key in sorted(replacements.keys(), key=len, reverse=True):
            text = text.replace(key, replacements[key])
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text
    
    # VOICE INPUT FUNCTION
    def voice_input(self, entry_widget, update_answer_func, ask_function):
        """Capture voice input and automatically answer with voice output"""
        try:
            import speech_recognition as sr
            
            update_answer_func("🎙️ Listening... Please speak your question.")
            
            recognizer = sr.Recognizer()
            recognizer.pause_threshold = 1.0
            recognizer.phrase_time_limit = 15
            
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                    
                    # Try multiple languages
                    text = None
                    for lang in ["ur-PK", "ur-IN", "en-US"]:
                        try:
                            text = recognizer.recognize_google(audio, language=lang)
                            break
                        except:
                            continue
                    
                    if not text:
                        update_answer_func("❌ Could not understand audio. Please try again.")
                        return
                    
                    # ✅ FIX: Convert Urdu script to Roman Urdu
                    text = self.convert_to_roman_urdu(text)
                    
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, text)
                    
                    update_answer_func(f"✅ I heard: '{text}'\n\n⏳ Getting answer...")
                    
                    # Get answer and speak it
                    self.get_answer_and_speak(text, update_answer_func)
                    
                except sr.WaitTimeoutError:
                    update_answer_func("⏱️ No speech detected. Please try again.")
                except sr.UnknownValueError:
                    update_answer_func("❌ Could not understand audio. Please try again.")
                except sr.RequestError as e:
                    update_answer_func(f"❌ Speech recognition service error: {str(e)}")
                    
        except ImportError:
            messagebox.showerror(
                "Voice Not Available",
                "Required modules not installed.\n\n"
                "Install with: pip install SpeechRecognition pyaudio pyttsx3"
            )
        except Exception as e:
            update_answer_func(f"❌ Voice Error: {str(e)}")

    # ============================================================
    # SHOW FORECAST
    # ============================================================
    def show_forecast(self):
        """Show demand forecast window"""
        win = tk.Toplevel(self.parent)
        win.title("📊 Demand Forecast")
        win.geometry("900x600")
        win.config(bg="#f4f6f9")
        
        tk.Label(
            win,
            text="📊 Demand Forecast - Next 30 Days",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f6f9",
            fg="#1b4fbf"
        ).pack(pady=15)
        
        tree_frame = tk.Frame(win, bg="#f4f6f9")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("Thread", "Size", "Avg Daily", "Total Forecast", "Trend", "Status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        results = self.forecaster.forecast_all_products()
        
        for key, result in results.items():
            if result['status'] == 'success':
                thread, size = key.split('|')
                trend_icon = "📈" if result['trend'] == 'increasing' else "📉" if result['trend'] == 'decreasing' else "➡️"
                tree.insert("", "end", values=(
                    thread,
                    size,
                    f"{result['average_daily_demand']:.1f}",
                    f"{result['total_forecast_demand']:.0f}",
                    trend_icon,
                    "✅"
                ))
            else:
                thread, size = key.split('|')
                tree.insert("", "end", values=(
                    thread,
                    size,
                    "N/A",
                    "N/A",
                    "❌",
                    "Insufficient Data"
                ))
        
        tk.Button(
            win,
            text="Close",
            command=win.destroy,
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=12,
            height=2,
            relief="flat"
        ).pack(pady=15)
    
    # ============================================================
    # SHOW REORDER ALERTS
    # ============================================================
    def show_reorder_alerts(self):
        """Show reorder recommendations"""
        win = tk.Toplevel(self.parent)
        win.title("🔄 Reorder Recommendations")
        win.geometry("1000x600")
        win.config(bg="#f4f6f9")
        
        tk.Label(
            win,
            text="🔄 Smart Reorder Recommendations",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f6f9",
            fg="#1b4fbf"
        ).pack(pady=15)
        
        main_container = tk.Frame(win, bg="#f4f6f9")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        recs = self.engine.get_all_recommendations()
        
        if recs:
            tree_frame = tk.Frame(main_container, bg="#f4f6f9")
            tree_frame.pack(fill="both", expand=True)
            
            columns = ("Thread", "Size", "Current Stock", "Daily Demand", "Reorder Point", "Recommendation", "Urgency")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
            
            widths = {"Thread": 120, "Size": 80, "Current Stock": 100, "Daily Demand": 100, 
                      "Reorder Point": 100, "Recommendation": 120, "Urgency": 80}
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=widths.get(col, 100), anchor="center")
            
            v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
            
            tree.pack(side="left", fill="both", expand=True)
            v_scroll.pack(side="right", fill="y")
            h_scroll.pack(side="bottom", fill="x")
            
            for rec in recs:
                urgency_icon = "🔴" if rec['urgency'] == 'high' else "🟡" if rec['urgency'] == 'medium' else "🟢"
                tree.insert("", "end", values=(
                    rec['thread'],
                    rec['size'],
                    f"{rec['current_stock']:.0f}",
                    f"{rec['daily_demand']:.1f}",
                    f"{rec['reorder_point']:.0f}",
                    f"{rec['recommended_quantity']:.0f}",
                    urgency_icon
                ))
        else:
            msg_frame = tk.Frame(main_container, bg="#f4f6f9")
            msg_frame.pack(fill="both", expand=True)
            
            tk.Label(
                msg_frame,
                text="✅ All stock levels are healthy!\nNo reorder needed.",
                font=("Segoe UI", 16, "bold"),
                bg="#f4f6f9",
                fg="#27ae60"
            ).place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Button(
            win,
            text="Close",
            command=win.destroy,
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=12,
            height=2,
            relief="flat"
        ).pack(pady=15)
    
    # ============================================================
    # SHOW SEGMENTATION
    # ============================================================
    def show_segmentation(self):
        """Show customer/supplier segmentation"""
        win = tk.Toplevel(self.parent)
        win.title("👥 Segmentation Analysis")
        win.geometry("900x600")
        win.config(bg="#f4f6f9")
        
        tk.Label(
            win,
            text="👥 Customer & Supplier Segmentation",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f6f9",
            fg="#1b4fbf"
        ).pack(pady=15)
        
        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Customer Tab
        customer_tab = tk.Frame(notebook, bg="#f4f6f9")
        notebook.add(customer_tab, text="👤 Customers")
        
        customer_rfm = self.segmenter.calculate_rfm_customers()
        
        if not customer_rfm.empty:
            tree_frame = tk.Frame(customer_tab, bg="#f4f6f9")
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            tree = ttk.Treeview(tree_frame, columns=("Customer", "Recency", "Frequency", "Monetary", "Segment"), show="headings")
            
            for col in ("Customer", "Recency", "Frequency", "Monetary", "Segment"):
                tree.heading(col, text=col)
                tree.column(col, width=140, anchor="center")
            
            v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
            
            tree.pack(side="left", fill="both", expand=True)
            v_scroll.pack(side="right", fill="y")
            h_scroll.pack(side="bottom", fill="x")
            
            for _, row in customer_rfm.iterrows():
                tree.insert("", "end", values=(
                    row['customer'][:25],
                    row['recency'],
                    row['frequency'],
                    f"{row['monetary']:.0f}",
                    row['segment']
                ))
        else:
            tk.Label(customer_tab, text="No customer data available", bg="#f4f6f9", font=("Segoe UI", 12)).pack(pady=50)
        
        # Supplier Tab
        supplier_tab = tk.Frame(notebook, bg="#f4f6f9")
        notebook.add(supplier_tab, text="🏢 Suppliers")
        
        supplier_rfm = self.segmenter.calculate_rfm_suppliers()
        
        if not supplier_rfm.empty:
            tree_frame = tk.Frame(supplier_tab, bg="#f4f6f9")
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            tree = ttk.Treeview(tree_frame, columns=("Supplier", "Recency", "Frequency", "Monetary", "Segment"), show="headings")
            
            for col in ("Supplier", "Recency", "Frequency", "Monetary", "Segment"):
                tree.heading(col, text=col)
                tree.column(col, width=140, anchor="center")
            
            v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
            
            tree.pack(side="left", fill="both", expand=True)
            v_scroll.pack(side="right", fill="y")
            h_scroll.pack(side="bottom", fill="x")
            
            for _, row in supplier_rfm.iterrows():
                tree.insert("", "end", values=(
                    row['supplier'][:25],
                    row['recency'],
                    row['frequency'],
                    f"{row['monetary']:.0f}",
                    row['segment']
                ))
        else:
            tk.Label(supplier_tab, text="No supplier data available", bg="#f4f6f9", font=("Segoe UI", 12)).pack(pady=50)
        
        tk.Button(
            win,
            text="Close",
            command=win.destroy,
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=12,
            height=2,
            relief="flat"
        ).pack(pady=15)
    
    # ============================================================
    # SHOW ANOMALIES
    # ============================================================
    def show_anomalies(self):
        """Show anomaly detection results"""
        win = tk.Toplevel(self.parent)
        win.title("⚠️ Anomaly Detection")
        win.geometry("800x500")
        win.config(bg="#f4f6f9")
        
        tk.Label(
            win,
            text="⚠️ System Anomaly Alerts",
            font=("Segoe UI", 18, "bold"),
            bg="#f4f6f9",
            fg="#1b4fbf"
        ).pack(pady=15)
        
        alerts_frame = tk.Frame(win, bg="#f4f6f9")
        alerts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        alerts = self.detector.run_full_scan()
        
        if alerts:
            text_area = scrolledtext.ScrolledText(
                alerts_frame,
                font=("Consolas", 11),
                bg="white",
                height=15,
                wrap="word"
            )
            text_area.pack(fill="both", expand=True)
            
            for alert in alerts:
                severity_icon = "🔴" if alert['severity'] == 'high' else "🟡" if alert['severity'] == 'medium' else "🟢"
                text_area.insert("end", f"{severity_icon} [{alert['type'].upper()}] {alert['message']}\n\n")
            
            text_area.config(state="disabled")
        else:
            tk.Label(
                alerts_frame,
                text="✅ No anomalies detected! System is healthy.",
                font=("Segoe UI", 14, "bold"),
                bg="#f4f6f9",
                fg="#27ae60"
            ).pack(pady=50)
        
        tk.Button(
            win,
            text="Close",
            command=win.destroy,
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=12,
            height=2,
            relief="flat"
        ).pack(pady=15)
    
    # SHOW QA ASSISTANT
    def show_qa_assistant(self):

        win = tk.Toplevel(self.parent)
        win.title("💬 AI Q&A Assistant")
        win.geometry("850x720")
        win.minsize(750, 650)
        win.config(bg="#eef3f9")

        # ================= COLORS =================
        BLUE = "#1b4fbf"
        DARK_BLUE = "#123b91"
        LIGHT_BLUE = "#eaf2ff"
        BG = "#eef3f9"
        WHITE = "#ffffff"
        TEXT = "#263238"
        GRAY = "#718096"
        BORDER = "#d9e2ef"
        GREEN = "#20a464"

        # =========================================================
        # HEADER
        # =========================================================
        header = tk.Frame(
            win,
            bg=BLUE,
            height=100
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        header_content = tk.Frame(
            header,
            bg=BLUE
        )
        header_content.pack(expand=True)

        tk.Label(
            header_content,
            text="🤖",
            font=("Segoe UI Emoji", 32),
            bg=BLUE,
            fg="white"
        ).pack(
            side="left",
            padx=(0, 14)
        )

        title_frame = tk.Frame(
            header_content,
            bg=BLUE
        )
        title_frame.pack(side="left")

        tk.Label(
            title_frame,
            text="AI Q&A Assistant",
            font=("Segoe UI", 23, "bold"),
            bg=BLUE,
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text="Ask anything about your Thread Management System",
            font=("Segoe UI", 10),
            bg=BLUE,
            fg="#dbe8ff"
        ).pack(anchor="w")

        # =========================================================
        # MAIN CONTAINER
        # =========================================================
        main = tk.Frame(
            win,
            bg=BG
        )
        main.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=20
        )

        # =========================================================
        # QUESTION CARD
        # =========================================================
        question_card = tk.Frame(
            main,
            bg=WHITE,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        question_card.pack(
            fill="x",
            pady=(0, 15)
        )

        q_content = tk.Frame(
            question_card,
            bg=WHITE
        )
        q_content.pack(
            fill="x",
            padx=18,
            pady=15
        )

        # Question title
        title_row = tk.Frame(
            q_content,
            bg=WHITE
        )
        title_row.pack(
            fill="x",
            pady=(0, 8)
        )

        tk.Label(
            title_row,
            text="💬",
            font=("Segoe UI Emoji", 17),
            bg=WHITE
        ).pack(
            side="left",
            padx=(0, 8)
        )

        tk.Label(
            title_row,
            text="Ask Your Question",
            font=("Segoe UI", 13, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(side="left")

        # =========================================================
        # QUESTION INPUT
        # =========================================================
        input_frame = tk.Frame(
            q_content,
            bg="#f7faff",
            highlightthickness=1,
            highlightbackground=BORDER
        )
        input_frame.pack(fill="x")

        input_frame.grid_columnconfigure(
            0,
            weight=1
        )

        placeholder_text = "Type your question here..."

        question_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            bg="#f7faff",
            fg="#8a94a6",
            relief="flat",
            bd=0
        )

        question_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(14, 5),
            ipady=11
        )

        question_entry.insert(
            0,
            placeholder_text
        )

        # =========================================================
        # PLACEHOLDER
        # =========================================================
        def on_entry_click(event):

            if question_entry.get() == placeholder_text:

                question_entry.delete(
                    0,
                    tk.END
                )

                question_entry.config(
                    fg=TEXT
                )

        def on_focus_out(event):

            if question_entry.get().strip() == "":

                question_entry.insert(
                    0,
                    placeholder_text
                )

                question_entry.config(
                    fg="#8a94a6"
                )

        question_entry.bind(
            "<FocusIn>",
            on_entry_click
        )

        question_entry.bind(
            "<FocusOut>",
            on_focus_out
        )

        # =========================================================
        # ANSWER CARD
        # =========================================================
        answer_card = tk.Frame(
            main,
            bg=WHITE,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        # IMPORTANT:
        # Answer card is packed AFTER the fixed areas below.
        # This allows it to take only the remaining space.

        answer_content = tk.Frame(
            answer_card,
            bg=WHITE
        )
        answer_content.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=15
        )

        # Answer header
        answer_header = tk.Frame(
            answer_content,
            bg=WHITE
        )
        answer_header.pack(
            fill="x",
            pady=(0, 8)
        )

        ai_icon = tk.Label(
            answer_header,
            text="🤖",
            font=("Segoe UI Emoji", 16),
            bg=LIGHT_BLUE,
            fg=BLUE,
            width=3
        )
        ai_icon.pack(
            side="left",
            padx=(0, 10)
        )

        answer_title_frame = tk.Frame(
            answer_header,
            bg=WHITE
        )
        answer_title_frame.pack(
            side="left"
        )

        tk.Label(
            answer_title_frame,
            text="AI Response",
            font=("Segoe UI", 13, "bold"),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            answer_title_frame,
            text="Your answer will appear here",
            font=("Segoe UI", 9),
            bg=WHITE,
            fg=GRAY
        ).pack(anchor="w")

        # AI Ready status
        status_frame = tk.Frame(
            answer_header,
            bg=WHITE
        )
        status_frame.pack(
            side="right",
            pady=5
        )

        tk.Label(
            status_frame,
            text="●",
            font=("Segoe UI", 12),
            bg=WHITE,
            fg=GREEN
        ).pack(side="left")

        tk.Label(
            status_frame,
            text="AI Ready",
            font=("Segoe UI", 9, "bold"),
            bg=WHITE,
            fg=GREEN
        ).pack(
            side="left",
            padx=(3, 0)
        )

        # =========================================================
        # ANSWER TEXT BOX
        # =========================================================
        answer_box_frame = tk.Frame(
            answer_content,
            bg="#f7faff",
            highlightthickness=1,
            highlightbackground=BORDER
        )

        answer_box_frame.pack(
            fill="both",
            expand=True
        )

        answer_text = scrolledtext.ScrolledText(
            answer_box_frame,
            font=("Segoe UI", 11),
            bg="#f7faff",
            fg=TEXT,
            wrap="word",
            relief="flat",
            bd=0,
            padx=15,
            pady=15
        )

        answer_text.pack(
            fill="both",
            expand=True
        )

        answer_text.config(
            state="disabled"
        )

        # =========================================================
        # UPDATE ANSWER
        # =========================================================
        def update_answer(response):

            answer_text.config(
                state="normal"
            )

            answer_text.delete(
                "1.0",
                tk.END
            )

            answer_text.insert(
                "1.0",
                response
            )

            answer_text.config(
                state="disabled"
            )

            answer_text.see("1.0")

        # =========================================================
        # ASK QUESTION
        # =========================================================
        def ask_question():

            question = question_entry.get().strip()

            if question == placeholder_text or not question:

                messagebox.showwarning(
                    "Question Required",
                    "Please type a question first."
                )

                question_entry.focus()

                return

            # Loading message
            update_answer(
                "🤔  Thinking...\n\n"
                "Please wait while AI prepares your answer."
            )

            ask_btn.config(
                state="disabled",
                text="⏳  Thinking..."
            )

            def process():

                try:

                    if self.assistant.llm_available:

                        response = self.assistant.quick_query(
                            question
                        )

                    else:

                        response = (
                            "⚠️ LLM is not available.\n\n"
                            "Please install and run Ollama.\n\n"
                        )

                        response += self.assistant.get_context()

                    # Update answer
                    self.parent.after(
                        0,
                        lambda: update_answer(response)
                    )

                    # Speak answer
                    self.speak_response(
                        response,
                        question
                    )

                except Exception as err:

                    error_msg = (
                        "❌ Error occurred.\n\n"
                        f"{str(err)}"
                    )

                    self.parent.after(
                        0,
                        lambda: update_answer(error_msg)
                    )

                finally:

                    self.parent.after(
                        0,
                        lambda: ask_btn.config(
                            state="normal",
                            text="🔍  Ask AI"
                        )
                    )

            threading.Thread(
                target=process,
                daemon=True
            ).start()

        # =========================================================
        # MICROPHONE BUTTON
        # =========================================================
        def mic_enter(event):

            voice_btn.config(
                bg=LIGHT_BLUE
            )

        def mic_leave(event):

            voice_btn.config(
                bg="#f7faff"
            )

        voice_btn = tk.Button(
            input_frame,
            text="🎙️",
            font=("Segoe UI Emoji", 18),
            bg="#f7faff",
            fg=BLUE,
            activebackground=LIGHT_BLUE,
            activeforeground=BLUE,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=4,
            command=lambda: self.voice_input(
                question_entry,
                update_answer,
                ask_question
            )
        )

        voice_btn.grid(
            row=0,
            column=1,
            padx=(0, 7),
            pady=4
        )

        voice_btn.bind(
            "<Enter>",
            mic_enter
        )

        voice_btn.bind(
            "<Leave>",
            mic_leave
        )

        # =========================================================
        # BUTTON FRAME
        # =========================================================
        # IMPORTANT:
        # This frame is packed BEFORE answer_card.
        # Therefore buttons always remain visible.

        button_frame = tk.Frame(
            main,
            bg=BG,
            height=55
        )

        button_frame.pack(
            fill="x",
            pady=(15, 5)
        )

        button_frame.pack_propagate(False)

        # =========================================================
        # ASK BUTTON
        # =========================================================
        ask_btn = tk.Button(
            button_frame,
            text="🔍  Ask AI",
            command=ask_question,
            bg=BLUE,
            fg="white",
            activebackground=DARK_BLUE,
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            width=15,
            height=2
        )

        ask_btn.pack(
            side="left",
            padx=(0, 10)
        )

        def ask_enter(event):

            if ask_btn["state"] != "disabled":
                ask_btn.config(
                    bg=DARK_BLUE
                )

        def ask_leave(event):

            if ask_btn["state"] != "disabled":
                ask_btn.config(
                    bg=BLUE
                )

        ask_btn.bind(
            "<Enter>",
            ask_enter
        )

        ask_btn.bind(
            "<Leave>",
            ask_leave
        )

        # =========================================================
        # CLEAR BUTTON
        # =========================================================
        def clear_question():

            question_entry.delete(
                0,
                tk.END
            )

            question_entry.insert(
                0,
                placeholder_text
            )

            question_entry.config(
                fg="#8a94a6"
            )

            update_answer(
                "💡  Hello! I'm your AI Assistant.\n\n"
                "Type your question above and click "
                "'Ask AI' to get an answer."
            )

            question_entry.focus()

        clear_btn = tk.Button(
            button_frame,
            text="🗑  Clear",
            command=clear_question,
            bg=WHITE,
            fg="#596579",
            activebackground="#edf1f7",
            activeforeground=TEXT,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            width=12,
            height=2,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        clear_btn.pack(
            side="left",
            padx=(0, 10)
        )

        # =========================================================
        # CLOSE BUTTON
        # =========================================================
        close_btn = tk.Button(
            button_frame,
            text="✕  Close",
            command=win.destroy,
            bg=WHITE,
            fg="#596579",
            activebackground="#edf1f7",
            activeforeground=TEXT,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            width=12,
            height=2,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        close_btn.pack(
            side="left"
        )

        # =========================================================
        # BUTTON HOVER
        # =========================================================
        def clear_enter(event):

            clear_btn.config(
                bg="#edf1f7"
            )

        def clear_leave(event):

            clear_btn.config(
                bg=WHITE
            )

        def close_enter(event):

            close_btn.config(
                bg="#edf1f7"
            )

        def close_leave(event):

            close_btn.config(
                bg=WHITE
            )

        clear_btn.bind(
            "<Enter>",
            clear_enter
        )

        clear_btn.bind(
            "<Leave>",
            clear_leave
        )

        close_btn.bind(
            "<Enter>",
            close_enter
        )

        close_btn.bind(
            "<Leave>",
            close_leave
        )

        # =========================================================
        # VOICE INFORMATION
        # =========================================================
        info_frame = tk.Frame(
            main,
            bg=BG,
            height=25
        )

        info_frame.pack(
            fill="x",
            pady=(2, 0)
        )

        tk.Label(
            info_frame,
            text="🎙️ Voice Assistant",
            font=("Segoe UI", 9, "bold"),
            bg=BG,
            fg=BLUE
        ).pack(
            side="left"
        )

        tk.Label(
            info_frame,
            text="  •  Urdu Female Voice  •  Say "
                "'english mein batao' for English",
            font=("Segoe UI", 9),
            bg=BG,
            fg=GRAY
        ).pack(
            side="left"
        )

        # =========================================================
        # IMPORTANT:
        # PACK ANSWER CARD LAST
        # =========================================================
        answer_card.pack(
            fill="both",
            expand=True,
            pady=(0, 0)
        )

        # =========================================================
        # ENTER KEY
        # =========================================================
        question_entry.bind(
            "<Return>",
            lambda event: ask_question()
        )
        # INITIAL ANSWER
        update_answer(
            "💡  Hello! I'm your AI Assistant.\n\n"
            "You can ask me questions about your "
            "Thread Management System, inventory, "
            "stock, suppliers, customers and more.\n\n"
            "Type OR Voice your question above and click "
            "'Ask AI' or press Enter."
        )
        question_entry.focus()

    # REPORT INSIGHT
    def show_insights(self):
        win = tk.Toplevel(self.parent)
        win.title("📈 AI Insights Report Designed By: AlRehman Software")
        win.geometry("700x650")
        win.config(bg="#f4f6f9")
        
        tk.Label(win,text="📈 AI-Powered Insights Report",font=("Segoe UI", 20, "bold"),
            bg="#f4f6f9",fg="#1b4fbf").pack(pady=15)
        
        # Loading
        loading_label = tk.Label(win,text="⏳ Generating insights... Please wait.",
            font=("Segoe UI", 12, "italic"),bg="#f4f6f9",fg="#757879")
        loading_label.pack(pady=15)
        
        # Text area
        text_frame = tk.Frame(win, bg="#f4f6f9")
        text_frame.pack(fill="both", expand=True, padx=12, pady=10)
        
        text_area = scrolledtext.ScrolledText(text_frame,font=("Segoe UI", 12,"bold"),
            bg="black", fg="white",height=20,wrap="word")
        text_area.pack(fill="both", expand=True)
        text_area.config(state="disabled")
        
        def update_text(content):
            text_area.config(state="normal")
            text_area.delete("1.0", "end")
            text_area.insert("1.0", content)
            text_area.config(state="disabled")
            loading_label.config(text="✅ Insights generated successfully!")
        
        def generate():
            try:
                # Get insights
                report = self.report_insights.get_full_report()
                
                content = "=" * 60 + "\n"
                content += "📊 INVENTORY INSIGHTS REPORT\n"
                content += f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                content += "=" * 60 + "\n\n"
                
                # Sales Insights
                content += "📈 SALES INSIGHTS\n"
                content += "-" * 40 + "\n"
                sales = report['sales_insights']
                if isinstance(sales, dict):
                    content += f"• Top Selling Thread: {sales.get('top_selling_thread', 'N/A')}\n"
                    content += f"• Top Selling Size: {sales.get('top_selling_size', 'N/A')}\n"
                    content += f"• Total Revenue: Rs. {sales.get('total_revenue', 0):,.2f}\n"
                    content += f"• Total Sales: {sales.get('total_sales', 0)} bundles\n"
                else:
                    content += f"{sales}\n"
                
                content += "\n\n"
                
                # Supplier Insights
                content += "🏢 SUPPLIER INSIGHTS\n"
                content += "-" * 40 + "\n"
                suppliers = report['supplier_insights']
                if isinstance(suppliers, dict):
                    content += f"• Cheapest Supplier: {suppliers.get('cheapest_supplier', 'N/A')}\n"
                    content += f"• Most Expensive Supplier: {suppliers.get('most_expensive_supplier', 'N/A')}\n"
                    content += f"• Potential Savings: {suppliers.get('potential_savings', 0)}%\n"
                else:
                    content += f"{suppliers}\n"
                
                content += "\n\n"
                
                # Stock Insights
                content += "📦 STOCK INSIGHTS\n"
                content += "-" * 40 + "\n"
                stock = report['stock_insights']
                if isinstance(stock, dict):
                    content += f"• Total Available Stock: {stock.get('total_available', 0)} bundles\n"
                    content += f"• Low Stock Items: {stock.get('low_stock_count', 0)}\n"
                    content += f"• Overstocked Items: {stock.get('high_stock_count', 0)}\n"
                else:
                    content += f"{stock}\n"
                
                content += "\n\n"
                
                # AI Summary
                content += "🤖 AI EXECUTIVE SUMMARY\n"
                content += "-" * 40 + "\n"
                content += report['llm_report']
                
                self.parent.after(0, lambda: update_text(content))
                
            except Exception as e:
                self.parent.after(0, lambda: update_text(f"❌ Error generating insights: {str(e)}"))
        
        # Generate in background
        threading.Thread(target=generate, daemon=True).start()
        
        # Close button
        tk.Button(win,text="Close",command=win.destroy,bg="#34495e",fg="white",
            font=("Segoe UI", 11, "bold"),width=12,height=2,relief="flat").pack(pady=15)

# TEST
if __name__ == "__main__":
    root = tk.Tk()
    root.title("AI Dashboard Test")
    root.geometry("900x600")
    root.config(bg="#f4f6f9")
    
    ai = AIDashboard(root)
    ai.create_ai_panel(root)
    
    root.mainloop()
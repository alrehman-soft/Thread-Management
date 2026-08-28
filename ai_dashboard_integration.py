import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import threading, os, tempfile

# Try to import Windows printing modules
try:
    import win32api
    import win32print
    WIN_PRINT_AVAILABLE = True
except ImportError:
    WIN_PRINT_AVAILABLE = False
    print("⚠️ win32api not available. Print feature will be limited.")

# Try to import reportlab for PDF
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ reportlab not available. PDF feature will be limited.")

# Import AI modules from ai folder
from ai.data_loader import DataLoader
from ai.demand_forecast import DemandForecaster
from ai.reorder_engine import ReorderEngine
from ai.segmentation import Segmenter
from ai.anomaly_detector import AnomalyDetector
from ai.qa_assistant import QAAssistant
from ai.report_insights import ReportInsights


class AIDashboard:
    """AI Features Panel for Dashboard with Voice Print Support"""
    
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
        
        # Assistant Name
        self.assistant_name = "AlRehman"
        
        # Store last answer for printing
        self.last_answer = ""
        self.last_question = ""
        self.last_response_time = None
        
        # For tracking voice print status
        self.is_printing = False
        
        # Store answer text widget reference
        self.current_answer_widget = None
    
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
        
        # Print Status Label
        self.print_status_label = tk.Label(
            stats_frame,
            text="",
            font=("Segoe UI", 10),
            bg="#f4f6f9",
            fg="#c0392b"
        )
        self.print_status_label.pack(side="right", padx=15)
        
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
            btn = tk.Button(
                btn_frame,
                text=text,
                command=cmd,
                bg="#1b4fbf",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                width=18,
                height=2,
                relief="flat",
                cursor="hand2"
            )
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
    
    # DIRECT PRINT TO PRINTER    
    def print_last_answer(self):
        """Print the last answer that was given"""
        if not self.last_answer:
            messagebox.showwarning(
                "No Answer",
                "Pehle koi sawal poochiye!\n\n"
                "Mai tabhi print kar sakta hoon jab answer ho."
            )
            return False
        
        return self.print_direct_to_printer(self.last_answer, self.last_question)
    
    def print_direct_to_printer(self, text, question=""):
        """Directly print to default Windows printer"""
        if self.is_printing:
            return False
        
        self.is_printing = True
        self.parent.after(0, lambda: self.print_status_label.config(
            text="🖨️ Printing...", fg="#2980b9"
        ))
        
        try:
            # Check if text has content
            if not text or len(text.strip()) < 5:
                self.parent.after(0, lambda: messagebox.showwarning(
                    "No Content", "Kuch print karne ke liye nahi hai."
                ))
                self.is_printing = False
                self.parent.after(0, lambda: self.print_status_label.config(text=""))
                return False
            
            # Create PDF first
            pdf_path = self.create_answer_pdf(text, question)
            
            if not pdf_path:
                self.is_printing = False
                self.parent.after(0, lambda: self.print_status_label.config(text=""))
                return False
            
            # Try Windows printing
            if WIN_PRINT_AVAILABLE:
                try:
                    printer_name = win32print.GetDefaultPrinter()
                    
                    if printer_name:
                        # Send to printer
                        win32api.ShellExecute(
                            0,
                            "print",
                            pdf_path,
                            f'/d:"{printer_name}"',
                            ".",
                            0
                        )
                        
                        self.parent.after(0, lambda: self.print_status_label.config(
                            text=f"✅ Printed on: {printer_name}", fg="#27ae60"
                        ))
                        
                        # Reset after 5 seconds
                        self.parent.after(5000, lambda: self.print_status_label.config(text=""))
                        
                        # Show success
                        self.parent.after(0, lambda: messagebox.showinfo(
                            "Print Success",
                            f"✅ Answer sent to printer!\n\n"
                            f"🖨️ Printer: {printer_name}\n"
                            f"📄 File: {os.path.basename(pdf_path)}"
                        ))
                        
                        self.is_printing = False
                        return True
                        
                except Exception as e:
                    print(f"Windows print error: {e}")
            
            # Fallback: Open PDF for manual printing
            os.startfile(pdf_path)
            
            self.parent.after(0, lambda: self.print_status_label.config(
                text="📄 PDF opened for printing", fg="#f39c12"
            ))
            
            self.parent.after(5000, lambda: self.print_status_label.config(text=""))
            
            self.parent.after(0, lambda: messagebox.showinfo(
                "PDF Created",
                f"✅ PDF file opened!\n\n"
                f"📄 File: {os.path.basename(pdf_path)}\n"
                f"📁 Location: {os.path.dirname(pdf_path)}\n\n"
                f"Now Press CTRL+P to print your answer."
            ))
            
            self.is_printing = False
            return True
            
        except Exception as e:
            error_msg = f"Print error: {str(e)}"
            self.parent.after(0, lambda: messagebox.showerror("Print Error", error_msg))
            self.is_printing = False
            self.parent.after(0, lambda: self.print_status_label.config(text="❌ Print Failed", fg="#c0392b"))
            self.parent.after(5000, lambda: self.print_status_label.config(text=""))
            return False
    
    def print_to_pdf_only(self, text, question=""):
        if self.is_printing:
            return False
        
        self.is_printing = True
        self.parent.after(0, lambda: self.print_status_label.config(
            text="📄 Creating PDF...", fg="#2980b9"
        ))
        
        try:
            pdf_path = self.create_answer_pdf(text, question)
            
            if pdf_path:
                # Open PDF
                os.startfile(pdf_path)
                
                self.parent.after(0, lambda: self.print_status_label.config(
                    text="📄 PDF Saved", fg="#27ae60"
                ))
                
                self.parent.after(5000, lambda: self.print_status_label.config(text=""))
                
                self.parent.after(0, lambda: messagebox.showinfo(
                    "PDF Created",
                    f"✅ PDF saved!\n\n"
                    f"📄 File: {os.path.basename(pdf_path)}\n"
                    f"📁 Location: {os.path.dirname(pdf_path)}"
                ))
                
                self.is_printing = False
                return True
            
            self.is_printing = False
            return False
            
        except Exception as e:
            error_msg = f"PDF error: {str(e)}"
            self.parent.after(0, lambda: messagebox.showerror("PDF Error", error_msg))
            self.is_printing = False
            self.parent.after(0, lambda: self.print_status_label.config(text="❌ PDF Failed", fg="#c0392b"))
            self.parent.after(5000, lambda: self.print_status_label.config(text=""))
            return False
    
    def create_answer_pdf(self, answer_text, question=""):
        if not REPORTLAB_AVAILABLE:
            return self.create_text_fallback(answer_text, question)
        try:
            # Create temp file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"AI_Response_{timestamp}.pdf"
            pdf_path = os.path.join(tempfile.gettempdir(), filename)
            
            pdf = canvas.Canvas(pdf_path, pagesize=A4)
            page_width, page_height = A4
            
            y = page_height - 50
            
            # ===== HEADER =====
            # Company Logo
            logo_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "images/company_logo.jpeg"
            )

            # ALTERNATIVE: Check multiple locations
            if not os.path.exists(logo_path):
                logo_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "images/company_logo.jpeg"
                )
            
            if os.path.exists(logo_path):
                try:
                    logo = ImageReader(logo_path)
                    pdf.drawImage(logo, 40, y - 40, width=60, height=60, 
                                  preserveAspectRatio=True, mask="auto")
                except Exception as e:
                    print(f"Logo error: {e}")
            
            # Company Name
            pdf.setFillColorRGB(0.05, 0.20, 0.45)  # Dark Blue
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawString(115, y - 10, "RASHID BROTHERS")
            
            pdf.setFont("Helvetica", 10)
            pdf.drawString(115, y - 28, "Manufacturer Of Leather & Leather Goods")
            
            # Contact Details
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawRightString(page_width - 40, y - 10, "+92-21-35116818")
            pdf.drawRightString(page_width - 40, y - 25, "rashidbrothers371@gmail.com")
            pdf.drawRightString(page_width - 40, y - 40, "Karachi, Pakistan")
            
            # Divider Line
            pdf.setLineWidth(1.5)
            pdf.line(40, y - 65, page_width - 40, y - 65)
            
            y -= 80
            
            # ===== TITLE =====
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawCentredString(page_width / 2, y, "🤖 AI ASSISTANT RESPONSE")
            
            y -= 35
            
            # ===== QUESTION =====
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(50, y, "❓ Question:")
            
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 11)
            question_text = question[:80] + "..." if len(question) > 80 else question
            pdf.drawString(140, y, question_text)
            
            y -= 30
            
            # ===== ANSWER BOX =====
            # Box border
            box_height = 300
            pdf.rect(45, y - box_height, page_width - 90, box_height)
            pdf.setFillColorRGB(0.95, 0.97, 1.0)  # Light blue background
            pdf.rect(45, y - box_height, page_width - 90, box_height, fill=1)
            
            # Box title
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(60, y - 20, "📝 Answer:")
            
            # Answer text with word wrap
            pdf.setFillColorRGB(0, 0, 0)
            pdf.setFont("Helvetica", 10)
            lines = answer_text.split('\n')
            
            current_y = y - 45
            for line in lines:
                if current_y < y - box_height + 20:
                    pdf.drawString(60, current_y, "... (more text below)")
                    break
                # Check if line starts with bullet point (•)
                if line.strip().startswith('•'):
                    pdf.drawString(65, current_y, line.strip())
                else:
                    pdf.drawString(60, current_y, line.strip())
                current_y -= 16
        
            y = y - box_height - 30
            
            # ===== METADATA =====
            pdf.setFont("Helvetica", 8)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawString(50, y, f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            pdf.drawString(300, y, f"📄 Page 1 of 1")
            
            y -= 30
            
            # ===== FOOTER =====
            pdf.line(40, y + 10, page_width - 40, y + 10)
            
            pdf.setFillColorRGB(0.05, 0.20, 0.45)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawCentredString(page_width / 2, y - 15, "RASHID BROTHERS")
            
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawCentredString(page_width / 2, y - 30, 
                                 "Plot # ST-371 SECTOR 7/A, Korangi Industrial Area, Karachi")
            
            pdf.setFont("Helvetica", 8)
            pdf.setFillColorRGB(0.5, 0.5, 0.5)
            pdf.drawCentredString(page_width / 2, y - 45, 
                    "Powered by Al-Rehman Software | RASHID BROTHERS")
            
            pdf.save()
            return pdf_path
            
        except Exception as e:
            print(f"PDF creation error: {e}")
            return self.create_text_fallback(answer_text, question)
    
    def create_text_fallback(self, answer_text, question=""):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"AI_Response_{timestamp}.txt"
            file_path = os.path.join(tempfile.gettempdir(), filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("RASHID BROTHERS\n")
                f.write("Manufacturer Of Leather & Leather Goods\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Question: {question}\n\n")
                f.write("Answer:\n")
                f.write("-" * 40 + "\n")
                f.write(answer_text)
                f.write("\n\n" + "=" * 60 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60)
            
            return file_path
            
        except Exception as e:
            print(f"Text fallback error: {e}")
            return None
    
    def wrap_text(self, text, width):
        """Wrap text to fit in PDF"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word) + 1
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    # VOICE COMMAND PROCESSING     
    def process_voice_command(self, question, update_answer_func):        
        question_lower = question.lower()
        
        # STEP 1: CHECK FOR NAME QUESTION
        name_keywords = [
            'apka naam kya hai', 'tumhara naam', 'aapka naam', 'name kya hai',
            'what is your name', 'who are you', 'kaun ho', 'tum kaun ho',
            'aap kaun hain', 'naam kya hai', 'kya naam hai',
            'your name', 'tell me your name'
        ]
        
        if any(kw in question_lower for kw in name_keywords):
            response = f"👋 Mera naam {self.assistant_name} hai! Main aapki AI assistant hoon."
            self.last_answer = response
            self.last_question = question
            self.parent.after_idle(lambda: update_answer_func(response))
            self.speak_response(response, question)
            return response
        
        # STEP 2: CHECK IF USER WANTS TO PRINT
        print_keywords = [
            'print', 'print karo', 'print kar do', 'print day', 
            'print out', 'hard copy', 'copy kar do',
            'print kar', 'print karein', 'print karen',
            'iska print', 'is ka print nikalo', 'is ka print day',
            'answer print', 'jawab print', 'jawaab print',
            'print this', 'print karein'
        ]
        
        wants_print = any(kw in question_lower for kw in print_keywords)
        
        pdf_keywords = ['pdf', 'save pdf', 'pdf banao', 'pdf save']
        wants_pdf = any(kw in question_lower for kw in pdf_keywords)
        
        # STEP 3: IF USER WANTS TO PRINT
        if wants_print or wants_pdf:
            if self.last_answer:
                if wants_print:
                    self.print_direct_to_printer(self.last_answer, self.last_question)
                    update_answer_func(
                        f"✅ Previous answer printer par bhej diya gaya!\n\n"
                        f"Question: {self.last_question}\n\n"
                        f"🖨️ Printing..."
                    )
                else:
                    self.print_to_pdf_only(self.last_answer, self.last_question)
                    update_answer_func(
                        f"✅ PDF save ho gayi!\n\n"
                        f"Question: {self.last_question}\n\n"
                        f"📄 PDF created..."
                    )
            else:
                update_answer_func(
                    "❌ Koi answer available nahi hai print karne ke liye.\n\n"
                    "Pehle koi sawal poochiye, phir 'print karo' boliye."
                )
                self.speak_response("Pehle koi sawal poochiye, phir print karo boliye.", question)
            return
        
        # STEP 4: NORMAL QUESTION
        try:
            if self.assistant.llm_available:
                response = self.assistant.quick_query(question)
            else:
                response = "⚠️ LLM not available. Please install Ollama.\n\n"
                response += self.assistant.get_context()
        except Exception as e:
            response = f"❌ Error: {str(e)}"
        
        # Store for printing
        self.last_answer = response
        self.last_question = question
        self.last_response_time = datetime.now()
        
        # Update text
        self.parent.after_idle(lambda: update_answer_func(response))
        
        # Speak the answer
        self.speak_response(response, question)
        
        # Show print hint
        self.parent.after(1000, lambda: self.print_status_label.config(
            text="💡 Say 'print karo' to print this answer", fg="#2980b9"
        ))
        self.parent.after(8000, lambda: self.print_status_label.config(text=""))
        
        return response
    
    # SPEAK RESPONSE FUNCTION    
    def speak_response(self, text, question=""):
        try:
            import pyttsx3
            
            # Check if user asked for English
            speak_english = False
            if question and ('english' in question.lower() or 'english mein' in question.lower()):
                speak_english = True
            
            # Initialize TTS engine
            engine = pyttsx3.init()
            
            # Get available voices
            voices = engine.getProperty('voices')
            
            # Set ZIRA
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
    
    def clean_text_for_speech(self, text, speak_english=False):
        import re
        
        # Remove emojis and special characters
        text = re.sub(r'[^\w\s\.\,\?\-\!\:\;\(\)\/]', '', text)
        
        if not speak_english:
            replacements = {
                # ===== NAME RELATED - PEHLE YE CHECK HOGA =====
                'تمہارا نام': 'tumhara naam',
                'آپ کا نام': 'apka naam',
                'نام کیا ہے': 'naam kya hai',
                'تمہارا نام کیا ہے': 'tumhara naam kya hai',
                'آپ کا نام کیا ہے': 'apka naam kya hai',
                'نام': 'naam',
                'تمہارا': 'tumhara',
                'آپ کا': 'apka',

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
    
    def convert_to_roman_english(self, text):        
        replacements = {
            # ===== NAME RELATED =====
            'تمہارا نام': 'tumhara naam',
            'آپ کا نام': 'apka naam',
            'نام کیا ہے': 'naam kya hai',
            'تمہارا نام کیا ہے': 'tumhara naam kya hai',
            'آپ کا نام کیا ہے': 'apka naam kya hai',
            'نام': 'naam',
            'تمہارا': 'tumhara',
            'آپ کا': 'apka',
            
            # ===== QUESTION WORDS =====
            'کیا': 'kya',
            'کتنا': 'kitna',
            'کتنی': 'kitni',
            'کیسے': 'kaise',
            'کہاں': 'kahan',
            'کیوں': 'kyun',
            'کب': 'kab',
            'کون': 'kaun',
            
            # ===== STOCK RELATED =====
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
            
            # ===== COMMON WORDS =====
            'ہے': 'hai',
            'ہیں': 'hain',
            'میں': 'mein',
            'کا': 'ka',
            'کی': 'ki',
            'کے': 'ke',
            'نے': 'ne',
            'سے': 'se',
            'پر': 'par',
            'لیے': 'liye',
            'تک': 'tak',
            'اور': 'aur',
            'تو': 'to',
            'بھی': 'bhi',
            
            # ===== NUMBERS =====
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
            'ہزار': 'hazaar',
            
            # ===== PRINT RELATED =====
            'پرنٹ': 'print',
            'پرنٹ کرو': 'print karo',
            'پرنٹ کر دو': 'print kar do',
            'پی ڈی ایف': 'pdf',
            'سیو': 'save',
            
            # ===== OTHERS =====
            'چائنا': 'China',
            'ٹیسلا': 'Tesla',
            'ریکارڈ': 'record',
            'آرڈر': 'order',
            'بیلنس': 'balance',
            'قیمت': 'price',
            'مقدار': 'quantity',
            'ادائیگی': 'payment',
        }
        
        # LONGEST FIRST
        for key in sorted(replacements.keys(), key=len, reverse=True):
            text = text.replace(key, replacements[key])
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text
    
    # VOICE INPUT FUNCTION
    def voice_input(self, entry_widget, update_answer_func, ask_function):
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
                    
                    text = None
                    
                    # ✅ First Try Urdu
                    for lang in ["ur-PK", "ur-IN"]:
                        try:
                            text = recognizer.recognize_google(audio, language=lang)
                            break
                        except:
                            continue
                    if not text:
                        try:
                            text = recognizer.recognize_google(audio, language="en-US")
                        except:
                            pass
                    
                    if not text:
                        update_answer_func("❌ Could not understand audio. Please try again.")
                        return
                    
                    # CONVERT URDU TO ROMAN ENGLISH
                    text = self.convert_to_roman_english(text)
                    
                    # CLEAN EXTRA SPACES
                    text = ' '.join(text.split())
                    
                    # SHOW IN ENTRY WIDGET (Roman English)
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, text)
                    
                    update_answer_func(f" I heard: '{text}'\n\n⏳ Getting answer...")
                    
                    self.process_voice_command(text, update_answer_func)
                    
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


    # SHOW QA ASSISTANT    
    def show_qa_assistant(self):        
        win = tk.Toplevel(self.parent)
        win.title("💬 AI VOICE Assistant")
        win.geometry("850x720")
        win.minsize(750, 650)
        win.config(bg="#eef3f9")
        
        BLUE = "#1b4fbf"
        DARK_BLUE = "#123b91"
        LIGHT_BLUE = "#eaf2ff"
        BG = "#eef3f9"
        WHITE = "#ffffff"
        TEXT = "#263238"
        GRAY = "#718096"
        BORDER = "#d9e2ef"
        GREEN = "#20a464"
        
        # ===== HEADER =====
        header = tk.Frame(win, bg=BLUE, height=100)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=BLUE)
        header_content.pack(expand=True)
        
        tk.Label(header_content,text="🤖",font=("Segoe UI Emoji", 32),bg=BLUE,
            fg="white").pack(side="left", padx=(0, 14))
        
        title_frame = tk.Frame(header_content, bg=BLUE)
        title_frame.pack(side="left")
        
        tk.Label(title_frame,text="AI Voice Assistant",font=("Segoe UI", 23, "bold"),
            bg=BLUE,fg="white").pack(anchor="w")
        
        tk.Label(title_frame,text="Ask anything about Thread Management System",
            font=("Segoe UI", 10),bg=BLUE,fg="#dbe8ff").pack(anchor="w")
        
        # ===== MAIN CONTAINER =====
        main = tk.Frame(win, bg=BG)
        main.pack(fill="both", expand=True, padx=28, pady=20)
        
        # ===== QUESTION CARD =====
        question_card = tk.Frame(main,bg=WHITE,highlightthickness=1,highlightbackground=BORDER)
        question_card.pack(fill="x", pady=(0, 15))
        
        q_content = tk.Frame(question_card, bg=WHITE)
        q_content.pack(fill="x", padx=18, pady=15)
        
        title_row = tk.Frame(q_content, bg=WHITE)
        title_row.pack(fill="x", pady=(0, 8))
        
        tk.Label(title_row,text="💬",font=("Segoe UI Emoji", 17),bg=WHITE
        ).pack(side="left", padx=(0, 8))
        
        tk.Label(title_row,text="Ask Your Question",font=("Segoe UI", 13, "bold"),
            bg=WHITE,fg=TEXT).pack(side="left")
        
        # ===== QUESTION INPUT =====
        input_frame = tk.Frame(q_content,bg="#f7faff",highlightthickness=1,highlightbackground=BORDER)
        input_frame.pack(fill="x")
        input_frame.grid_columnconfigure(0, weight=1)
        
        placeholder_text = "Type your question here..."
        
        question_entry = tk.Entry(input_frame,font=("Segoe UI", 12),bg="#f7faff",
            fg="#8a94a6",relief="flat",bd=0)
        
        question_entry.grid(row=0, column=0, sticky="ew", padx=(14, 5), ipady=11)
        question_entry.insert(0, placeholder_text)
        
        def on_entry_click(event):
            if question_entry.get() == placeholder_text:
                question_entry.delete(0, tk.END)
                question_entry.config(fg=TEXT)
        
        def on_focus_out(event):
            if question_entry.get().strip() == "":
                question_entry.insert(0, placeholder_text)
                question_entry.config(fg="#8a94a6")
        
        question_entry.bind("<FocusIn>", on_entry_click)
        question_entry.bind("<FocusOut>", on_focus_out)
        
        # ===== ANSWER CARD =====
        answer_card = tk.Frame(
            main,
            bg=WHITE,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        
        answer_content = tk.Frame(answer_card, bg=WHITE)
        answer_content.pack(fill="both", expand=True, padx=18, pady=15)
        
        answer_header = tk.Frame(answer_content, bg=WHITE)
        answer_header.pack(fill="x", pady=(0, 8))
        
        ai_icon = tk.Label(
            answer_header,
            text="🤖",
            font=("Segoe UI Emoji", 16),
            bg=LIGHT_BLUE,
            fg=BLUE,
            width=3
        )
        ai_icon.pack(side="left", padx=(0, 10))
        
        answer_title_frame = tk.Frame(answer_header, bg=WHITE)
        answer_title_frame.pack(side="left")
        
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
        
        status_frame = tk.Frame(answer_header, bg=WHITE)
        status_frame.pack(side="right", pady=5)
        
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
        ).pack(side="left", padx=(3, 0))
        
        # ===== ANSWER TEXT BOX =====
        answer_box_frame = tk.Frame(
            answer_content,
            bg="#f7faff",
            highlightthickness=1,
            highlightbackground=BORDER
        )
        answer_box_frame.pack(fill="both", expand=True)
        
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
        answer_text.pack(fill="both", expand=True)
        answer_text.config(state="disabled")
        
        self.current_answer_widget = answer_text
        
        def update_answer(response):
            answer_text.config(state="normal")
            answer_text.delete("1.0", tk.END)
            answer_text.insert("1.0", response)
            answer_text.config(state="disabled")
            answer_text.see("1.0")
        
        # ===== ASK QUESTION =====
        def ask_question():
            question = question_entry.get().strip()
            
            if question == placeholder_text or not question:
                messagebox.showwarning("Question Required", "Please type a question first.")
                question_entry.focus()
                return
            
            update_answer("🤔  Thinking...\n\nPlease wait while AI prepares your answer.")
            ask_btn.config(state="disabled", text="⏳  Thinking...")
            
            def process():
                try:
                    self.process_voice_command(question, update_answer)
                except Exception as err:
                    error_msg = f"❌ Error occurred.\n\n{str(err)}"
                    self.parent.after(0, lambda: update_answer(error_msg))
                finally:
                    self.parent.after(0, lambda: ask_btn.config(
                        state="normal", text="🔍  Ask AI"
                    ))
            
            threading.Thread(target=process, daemon=True).start()
        
        # ===== MICROPHONE BUTTON =====
        def mic_enter(event):
            voice_btn.config(bg=LIGHT_BLUE)
        
        def mic_leave(event):
            voice_btn.config(bg="#f7faff")
        
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
        voice_btn.grid(row=0, column=1, padx=(0, 7), pady=4)
        voice_btn.bind("<Enter>", mic_enter)
        voice_btn.bind("<Leave>", mic_leave)
        
        # ===== BUTTON FRAME =====
        button_frame = tk.Frame(main, bg=BG, height=55)
        button_frame.pack(fill="x", pady=(15, 5))
        button_frame.pack_propagate(False)
        
        ask_btn = tk.Button(button_frame,text="🔍 Ask AI",command=ask_question,
            bg=BLUE,fg="white",activebackground=DARK_BLUE,activeforeground="white",
            font=("Segoe UI", 11, "bold"),relief="flat",cursor="hand2",width=12,
            height=2)
        ask_btn.pack(side="left", padx=(0, 10))
        
        def clear_question():
            question_entry.delete(0, tk.END)
            question_entry.insert(0, placeholder_text)
            question_entry.config(fg="#BABDC3")
            
            update_answer("💡  Hello! I'm your AI Assistant.\n\n"
                         "Type your question above and click 'Ask AI' to get an answer.\n\n"
                         "🖨️  After getting the answer, say 'print karo' to print it!")
            
            question_entry.focus()
        
        clear_btn = tk.Button(button_frame,text="🗑Clear",command=clear_question,
            bg=WHITE,fg="#596579",activebackground="#edf1f7",activeforeground=TEXT,
            font=("Segoe UI", 11, "bold"),relief="flat",cursor="hand2",width=10,
            height=2,highlightthickness=1,highlightbackground=BORDER)
        clear_btn.pack(side="left", padx=(0, 10))
        
        def print_last_answer_click():
            if not self.last_answer:
                messagebox.showwarning("No Answer",
                    "Pehle koi sawal poochiye!\n\n"
                    "Mai tabhi print kar sakta hoon jab answer ho.")
                return
            
            self.print_direct_to_printer(self.last_answer, self.last_question)
        
        print_btn = tk.Button(button_frame,text=" 🖨️Print",command=print_last_answer_click,
            bg=WHITE,fg="#596579",activebackground="#edf1f7",activeforeground=TEXT,
            font=("Segoe UI", 11, "bold"),relief="flat",cursor="hand2",width=10,
            height=2,highlightthickness=1,highlightbackground=BORDER)
        print_btn.pack(side="left", padx=(0, 10))
        
        close_btn = tk.Button(button_frame,text="✕  Close",command=win.destroy,bg=WHITE,
            fg="#596579",activebackground="#edf1f7",activeforeground=TEXT,
            font=("Segoe UI", 11, "bold"),relief="flat",cursor="hand2",width=10,
            height=2,highlightthickness=1,highlightbackground=BORDER)
        close_btn.pack(side="left")
        
        question_entry.bind("<Return>", lambda event: ask_question())
        
        update_answer("💡  Hello! I'm your AI Assistant.\n\n"
                     "You can ask me questions about your Thread Management System,\n"
                     "inventory, stock, suppliers, customers and more.\n\n"
                     "🖨️  After getting the answer, say 'print karo' OR 'print this answer' to print it!\n\n"
                     "Type OR speak your question above!")
        
        question_entry.focus()
        answer_card.pack(fill="both", expand=True, pady=(0, 0))
    
    # Forecast
    def show_forecast(self):
        """Show demand forecast window"""
        win = tk.Toplevel(self.parent)
        win.title("📊 Demand Forecast")
        win.geometry("900x600")
        win.config(bg="#f4f6f9")
        
        tk.Label(win,text="📊 Demand Forecast - Next 30 Days",font=("Segoe UI", 18, "bold"),
            bg="#f4f6f9",fg="#1b4fbf").pack(pady=15)
        
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
                tree.insert("", "end", values=(thread,size,
                    f"{result['average_daily_demand']:.1f}",
                    f"{result['total_forecast_demand']:.0f}",
                    trend_icon,
                    "✅"))
            else:
                thread, size = key.split('|')
                tree.insert("", "end", values=(thread,size,"N/A","N/A","❌","Insufficient Data"))
        
        tk.Button(win,text="Close",command=win.destroy,bg="#34495e",fg="white",
            font=("Segoe UI", 11, "bold"),width=10,height=2).pack(pady=15)
    
    def show_reorder_alerts(self):
        """Show reorder recommendations"""
        win = tk.Toplevel(self.parent)
        win.title("🔄 Reorder Recommendations")
        win.geometry("1000x600")
        win.config(bg="#f4f6f9")
        
        tk.Label(win,text="🔄 Smart Reorder Recommendations",font=("Segoe UI", 18, "bold"),
            bg="#f4f6f9",fg="#1b4fbf").pack(pady=15)
        
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
            
            tk.Label(msg_frame,text="✅ All stock levels are healthy!\nNo reorder needed.",
                font=("Segoe UI", 16, "bold"),bg="#f4f6f9",fg="#27ae60"
            ).place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Button(win,text="Close",command=win.destroy,bg="#34495e",fg="white",
            font=("Segoe UI", 11, "bold"),width=10,height=2).pack(pady=15)
    
    def show_segmentation(self):
        """Show customer/supplier segmentation"""
        win = tk.Toplevel(self.parent)
        win.title("👥 Segmentation Analysis")
        win.geometry("900x600")
        win.config(bg="#f4f6f9")
        
        tk.Label(win,text="👥 Customer & Supplier Segmentation",font=("Segoe UI", 18, "bold"),
            bg="#f4f6f9",fg="#1b4fbf").pack(pady=15)
        
        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
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
        
        tk.Button(win,text="Close",command=win.destroy,bg="#34495e",fg="white",
            font=("Segoe UI", 11, "bold"),width=10,height=2).pack(pady=15)
    
    def show_anomalies(self):
        """Show anomaly detection results"""
        win = tk.Toplevel(self.parent)
        win.title("⚠️ Anomaly Detection")
        win.geometry("800x500")
        win.config(bg="#f4f6f9")
        
        tk.Label(win,text="⚠️ System Anomaly Alerts",font=("Segoe UI", 18, "bold"),
            bg="#f4f6f9",fg="#1b4fbf").pack(pady=15)
        
        alerts_frame = tk.Frame(win, bg="#f4f6f9")
        alerts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        alerts = self.detector.run_full_scan()
        
        if alerts:
            text_area = scrolledtext.ScrolledText(alerts_frame,font=("Consolas", 11),
                bg="white",height=15,wrap="word")
            text_area.pack(fill="both", expand=True)
            
            for alert in alerts:
                severity_icon = "🔴" if alert['severity'] == 'high' else "🟡" if alert['severity'] == 'medium' else "🟢"
                text_area.insert("end", f"{severity_icon} [{alert['type'].upper()}] {alert['message']}\n\n")
            
            text_area.config(state="disabled")
        else:
            tk.Label(alerts_frame,text="✅ No anomalies detected! System is healthy.",
                font=("Segoe UI", 14, "bold"),bg="#f4f6f9",fg="#27ae60").pack(pady=50)
        
        tk.Button(win,text="Close",command=win.destroy,bg="#34495e",fg="white",
            font=("Segoe UI", 11, "bold"),width=10,height=2,relief="flat").pack(pady=15)
    
    def show_insights(self):
        """Show AI Insights Report"""
        win = tk.Toplevel(self.parent)
        win.title("📈 AI Insights Report Designed By: AlRehman Software")
        win.geometry("700x650")
        win.config(bg="#f4f6f9")
        
        tk.Label(win, text="📈 AI-Powered Insights Report", font=("Segoe UI", 20, "bold"),
                 bg="#f4f6f9", fg="#1b4fbf").pack(pady=15)
        
        loading_label = tk.Label(win, text="⏳ Generating insights... Please wait.",
                    font=("Segoe UI", 12, "italic"), bg="#f4f6f9", fg="#757879")
        loading_label.pack(pady=15)
        
        text_frame = tk.Frame(win, bg="#f4f6f9")
        text_frame.pack(fill="both", expand=True, padx=12, pady=10)
        
        text_area = scrolledtext.ScrolledText(text_frame, font=("Segoe UI", 12, "bold"),
                                               bg="black", fg="white", height=20, wrap="word")
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
                report = self.report_insights.get_full_report()
                
                content = "=" * 60 + "\n"
                content += "📊 INVENTORY INSIGHTS REPORT\n"
                content += f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                content += "=" * 60 + "\n\n"
                
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
                
                content += "🤖 AI EXECUTIVE SUMMARY\n"
                content += "-" * 40 + "\n"
                content += report['llm_report']
                
                self.parent.after(0, lambda: update_text(content))
                
            except Exception as e:
                self.parent.after(0, lambda: update_text(f"❌ Error generating insights: {str(e)}"))
        
        threading.Thread(target=generate, daemon=True).start()
        
        tk.Button(win, text="Close", command=win.destroy, bg="#34495e", fg="white",
                  font=("Segoe UI", 11, "bold"), width=10, height=2, relief="flat").pack(pady=15)


# TEST
if __name__ == "__main__":
    root = tk.Tk()
    root.title("AI Dashboard Test")
    root.geometry("900x600")
    root.config(bg="#f4f6f9")
    
    ai = AIDashboard(root)
    ai.create_ai_panel(root)
    
    root.mainloop()

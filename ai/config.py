import os
from pathlib import Path


# Paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Demand Forecasting
FORECAST_DAYS = 30          # Predict next 30 days
HISTORY_DAYS = 90           # Use last 90 days for training
MIN_HISTORY_DAYS = 14       # Minimum days required for forecast

# Reorder Engine
SAFETY_STOCK_DAYS = 7       # Buffer stock for 7 days
REORDER_LEAD_TIME_DAYS = 5  # Supplier delivery time

# Anomaly Detection
ANOMALY_THRESHOLD = 2.5

# Segmentation
RFM_SCORES = [4, 3, 2, 1] 

# LLM (Local)
LLM_MODEL = "llama3.2:3b"
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 512

# Voice
VOICE_LANGUAGE = "en-US"
VOICE_TIMEOUT = 5           # Seconds to listen

# Enable/Disable Features
ENABLE_FORECAST = True
ENABLE_REORDER = True
ENABLE_SEGMENTATION = True
ENABLE_ANOMALY = True
ENABLE_QA = True
ENABLE_VOICE = False
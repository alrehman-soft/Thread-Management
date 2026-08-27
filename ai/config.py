import os
import sys
from pathlib import Path


# Paths
if getattr(sys, "frozen", False):
    BASE_DIR = Path(os.getenv("LOCALAPPDATA")) / "Thread Management System"
else:
    BASE_DIR = Path(__file__).parent

MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


# VOICE ASSISTANT NAME
VOICE_ASSISTANT_NAME = "AlRehman"


# Demand Forecasting
FORECAST_DAYS = 30
HISTORY_DAYS = 90
MIN_HISTORY_DAYS = 14


# Reorder Engine
SAFETY_STOCK_DAYS = 7
REORDER_LEAD_TIME_DAYS = 5


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
VOICE_TIMEOUT = 5


# Enable/Disable Features
ENABLE_FORECAST = True
ENABLE_REORDER = True
ENABLE_SEGMENTATION = True
ENABLE_ANOMALY = True
ENABLE_QA = True
ENABLE_VOICE = True


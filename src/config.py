from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

TARGET = "Churn"
ID_COLUMN = "customerID"

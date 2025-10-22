import os
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent  
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime('%Y-%m-%d')
raw_file = DATA_RAW_DIR / f"marinedata_{today}.json"

with open(raw_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)
print(df.head(10))


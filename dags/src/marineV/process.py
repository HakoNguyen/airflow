import os
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import argparse


# Thiết lập đường dẫn

BASE_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
CLEANED_DIR = DATA_PROCESSED_DIR / "cleaned"
DASHBOARD_DIR = DATA_PROCESSED_DIR / "dashboard"

for d in [DATA_RAW_DIR, DATA_PROCESSED_DIR, CLEANED_DIR, DASHBOARD_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# Định nghĩa hàm xử lý 1 file

def process_file(raw_file: Path):
    

    if not raw_file.exists():
        print(f" Cant find file: {raw_file}")
        return

    print(f" Processing file: {raw_file.name}")

    with open(raw_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df.replace("N/A", np.nan, inplace=True)

    # Xử lý dữ liệu numeric
    numeric_cols = [col for col in df.columns if col not in ["location", "time", "marine_condition"]]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    # Tính chỉ số an toàn biển 
    def compute_msi(row):
        if pd.isna(row.get("wave_height")) or pd.isna(row.get("ocean_current_velocity")):
            return np.nan
        wave_score = max(0, 1 - row["wave_height"] / 3)
        current_score = max(0, 1 - row["ocean_current_velocity"] / 1)
        temp_score = 1 - abs(row["sea_surface_temperature"] - 28) / 10
        return round((0.5 * wave_score + 0.3 * current_score + 0.2 * temp_score) * 100, 1)

    df["marine_safety_index"] = df.apply(compute_msi, axis=1)
    df_clean = df.round(3).fillna("N/A")

    # Chuyển datetime sang ISO string
    df_clean["time"] = df_clean["time"].apply(lambda x: x.isoformat() if pd.notnull(x) else None)

    # Xuất cleaned file
    date_str = raw_file.stem.split("_")[-1]
    clean_file = CLEANED_DIR / f"marinedata_cleaned_{date_str}.json"
    with open(clean_file, "w", encoding="utf-8") as f:
        json.dump(df_clean.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    # Tạo file dashboard
    df_agg = (
        df.groupby("location")
        .agg({
            "wave_height": "mean",
            "sea_surface_temperature": "mean",
            "ocean_current_velocity": "mean",
            "marine_safety_index": "mean",
        })
        .reset_index()
    )

    agg_file = DASHBOARD_DIR / f"marinedata_processed_{date_str}.json"
    with open(agg_file, "w", encoding="utf-8") as f:
        json.dump(df_agg.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    print(f"Processed successfully {raw_file.name}")



# Chạy qua CLI / Airflow

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="processed date (YYYY-MM-DD)")
    parser.add_argument("--all", action="store_true", help="Process all file in data/raw")
    args = parser.parse_args()

    if args.all:
        files = sorted(DATA_RAW_DIR.glob("marinedata_*.json"))
        print(f" Processing {len(files)} file in raw/")
        for file in files:
            process_file(file)
    else:
        date_str = args.date or datetime.now().strftime("%Y-%m-%d")
        raw_file = DATA_RAW_DIR / f"marinedata_{date_str}.json"
        process_file(raw_file)

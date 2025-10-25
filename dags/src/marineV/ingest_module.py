import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime
import numpy as np
import json, os
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  
DATA_DIR = BASE_DIR / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOCATIONS = [
    {"name": "Hải Phòng – Quảng Ninh (vịnh Bắc Bộ)", "lat": 20.95, "lng": 107.1},
    {"name": "Cù Lao Chàm (ngư trường trung bộ)", "lat": 15.7, "lng": 109.0},
    {"name": "Ven bờ Quảng Ngãi – Bình Định (khoảng 30 hải lý)", "lat": 14.3, "lng": 109.8},
    {"name": "Ven bờ Ninh Thuận – Bình Thuận", "lat": 11.0, "lng": 109.3},
    {"name": "Đông bắc đảo Côn Sơn (vùng Đông Nam Bộ biển Đông)", "lat": 8.9, "lng": 107.0},
    {"name": "Khu vực Quần đảo Hoàng Sa", "lat": 16.5, "lng": 112.0},
    {"name": "Khu vực Quần đảo Trường Sa", "lat": 9.5, "lng": 113.5},
    {"name": "Ngư trường Cà Mau – Kiên Giang", "lat": 8.5, "lng": 104.5},
]

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

URLS = {
    "marine": {
        "url": "https://marine-api.open-meteo.com/v1/marine",
        "fields": [
            "wave_height", "swell_wave_height", "wind_wave_height",
            "wave_period", "wind_wave_peak_period",
            "wave_direction", "wind_wave_direction",
            "ocean_current_velocity", "ocean_current_direction",
            "sea_surface_temperature", "sea_level_height_msl"
        ]
    },
    "weather": {
        "url": "https://api.open-meteo.com/v1/forecast",
        "fields": [
            "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
            "pressure_msl", "cloud_cover", "wind_speed_10m", "wind_direction_10m",
            "precipitation", "precipitation_probability", "weather_code", "visibility", "is_day"
        ]
    }
}


def ingest_data(locations, url, fields, chosen_date):
    result = []
    for loc in locations:
        params = {
            "latitude": loc["lat"],
            "longitude": loc["lng"],
            "hourly": fields,
            "start_date": chosen_date,
            "end_date": chosen_date,
            "timezone": "Asia/Ho_Chi_Minh",
        }
        try:
            responses = openmeteo.weather_api(url, params=params)
            response = responses[0]
            hourly = response.Hourly()

            times = pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
            if times.empty:
                continue

            now = pd.Timestamp.utcnow()
            idx = (abs(times - now)).argmin()
            item = {
                "location": loc["name"],
                "lat": loc["lat"],
                "lng": loc["lng"],
                "time": times[idx].isoformat()
            }
            for i, field in enumerate(fields):
                vals = hourly.Variables(i).ValuesAsNumpy()
                val = vals[idx] if vals.size > idx else None
                if isinstance(val, (np.floating, np.integer)):
                    val = val.item()
                item[field] = val
            result.append(item)
        except Exception as e:
            print(f"{loc['name']} Error: {e}")
    return result


def save_to_json(df, chosen_date):

    filename = DATA_DIR / f"marinedata_{chosen_date}.json"

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
    except FileNotFoundError:
        old_data = []

    new_data = df.to_dict('records')
    old_data.extend(new_data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(old_data, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu {len(new_data)} bản ghi vào {filename}")


def run_ingest(chosen_date):
    marine_data = ingest_data(LOCATIONS, URLS["marine"]["url"], URLS["marine"]["fields"], chosen_date)
    weather_data = ingest_data(LOCATIONS, URLS["weather"]["url"], URLS["weather"]["fields"], chosen_date)

    df_marine = pd.DataFrame(marine_data)
    df_weather = pd.DataFrame(weather_data)

    df_merged = pd.merge(
        df_marine,
        df_weather,
        on=['location', 'lat', 'lng', 'time'],
        how='outer',
        suffixes=("_marine", "_weather")
    )

    for col in df_merged.columns:
        if col.endswith("_marine") or col.endswith("_weather"):
            df_merged.rename(columns={col: col.replace("_marine", "").replace("_weather", "")}, inplace=True)

    df_merged.fillna("N/A", inplace=True)

    save_to_json(df_merged, chosen_date)
    print(f" Tổng số bản ghi thu thập: {len(df_merged)}")

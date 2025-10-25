import json
import sys
from datetime import datetime, date
from pathlib import Path
from supabase import create_client, Client
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

BASE_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATA_PATH = DATA_PROCESSED_DIR / "cleaned"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_data(date_str: str):
    candidates = [f for f in DATA_PATH.glob(f"marinedata_cleaned_{date_str}*.json")]
    if not candidates:
        return None
    candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return candidates[0]


def load_json(file_path: Path):
    print(f"Loading file: {file_path}")
    with file_path.open("r", encoding='utf-8') as f:
        records = json.load(f)

    for r in records:
        location = r['location']
        lat = r.get('lat')
        lng = r.get('lng')

        area = supabase.table('areas').select('id').eq('name', location).execute()
        if area.data:
            area_id = area.data[0]['id']
        else:
            new_area = supabase.table('areas').insert({
                'name': location,
                'lat': lat,
                'lng': lng
            }).execute()
            area_id = new_area.data[0]['id']

        timestamp = datetime.fromisoformat(r['time'].replace('Z', '+00:00')).isoformat()
        data = {
            "area_id": area_id,
            "timestamp": timestamp,
            "wave_height": r.get("wave_height"),
            "swell_wave_height": r.get("swell_wave_height"),
            "wind_wave_height": r.get("wind_wave_height"),
            "wave_period": r.get("wave_period"),
            "wave_direction": r.get("wave_direction"),
            "ocean_current_velocity": r.get("ocean_current_velocity"),
            "ocean_current_direction": r.get("ocean_current_direction"),
            "sea_surface_temperature": r.get("sea_surface_temperature"),
            "sea_level_height_msl": r.get("sea_level_height_msl"),
            "temperature_2m": r.get("temperature_2m"),
            "relative_humidity_2m": r.get("relative_humidity_2m"),
            "dew_point_2m": r.get("dew_point_2m"),
            "apparent_temperature": r.get("apparent_temperature"),
            "pressure_msl": r.get("pressure_msl"),
            "cloud_cover": r.get("cloud_cover"),
            "wind_speed_10m": r.get("wind_speed_10m"),
            "wind_direction_10m": r.get("wind_direction_10m"),
            "precipitation": r.get("precipitation"),
            "precipitation_probability": r.get("precipitation_probability"),
            "weather_code": r.get("weather_code"),
            "visibility": r.get("visibility"),
            "is_day": bool(r.get("is_day", 1)),
            "marine_safety_index": r.get("marine_safety_index"),
        }

        supabase.table('hourly_observations').delete().eq('area_id', area_id).eq('timestamp', timestamp).execute()
        supabase.table('hourly_observations').insert(data).execute()

    print(f"Done loading file: {file_path}")


def load_data(mode='all', date_str=None):
    if mode == 'single':
        file_path = get_data(date_str)
        if not file_path:
            print(f"Cannot find cleaned file for date {date_str}")
            return
        load_json(file_path)
    else:
        for f in sorted(DATA_PATH.glob("*.json")):
            load_json(f)

    print("Successfully loaded data.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        load_data(mode='single', date_str=date_str)
    else:
        load_data(mode="single", date_str=date.today().isoformat())

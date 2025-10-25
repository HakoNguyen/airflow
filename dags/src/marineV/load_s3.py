import boto3  
import sys
from datetime import date
from pathlib import Path  
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

BASE_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
CLEANED_DIR = DATA_PROCESSED_DIR / "cleaned"

s3 = boto3.client(
    "s3",
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name = AWS_REGION,
)

def get_file(date_str: str):
    candidates = list(CLEANED_DIR.glob(f"marinedata_cleaned_{date_str}*.json"))
    if not candidates:
        return None
    candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return candidates[0]

def upload_files(file_path: Path):
    day = file_path.stem.split("_")[2]
    s3_key = f"cleaned/{day}/{file_path.name}"
    print(f"Uploading {file_path.name} to s3://{S3_BUCKET_NAME}/{s3_key}")
    s3.upload_file(
        str(file_path),
        S3_BUCKET_NAME,
        s3_key,
        ExtraArgs = {"ContentType": "application/json"}
    )
    print("Uploaded successfully")

def upload_cleaned_data(mode="all", date_str=None):
    if mode == "single":
        file_path = get_file(date_str)
        if not file_path:
            print(f"No file found for {date_str}")
            return
        upload_files(file_path)
    else:
        for f in sorted(CLEANED_DIR.glob("*.json")):
            upload_files(f)
    print("Successfully uploaded data to S3")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        upload_cleaned_data(mode='single', date_str=date_str)
    else:
        upload_cleaned_data(mode="single", date_str=date.today().isoformat())

from ingest_module import run_ingest
from datetime import datetime

date_input = input("Nhập ngày cần lấy dữ liệu (YYYY-MM-DD, để trống = hôm nay): ").strip()

if date_input:
    try:
        chosen_date = datetime.strptime(date_input, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        print("Sai định dạng ngày! VD: 2025-09-25")
        raise
else:
    chosen_date = datetime.now().strftime("%Y-%m-%d")

print("📅 Lấy dữ liệu cho ngày:", chosen_date)
run_ingest(chosen_date)

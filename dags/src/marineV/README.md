# Marine Data Pipeline - Hướng dẫn sử dụng

## Tổng quan
Pipeline này thu thập, xử lý và lưu trữ dữ liệu biển từ Open-Meteo API, bao gồm:
- Thu thập dữ liệu thời tiết biển và khí tượng
- Xử lý và làm sạch dữ liệu
- Upload lên AWS S3
- Lưu trữ vào Supabase (PostgreSQL)

## Cấu trúc thư mục
```
dags/src/marineV/
├── data/
│   ├── raw/                    # Dữ liệu thô từ API
│   └── processed/
│       ├── cleaned/            # Dữ liệu đã làm sạch
│       └── dashboard/          # Dữ liệu tổng hợp cho dashboard
├── ingest_module.py            # Module thu thập dữ liệu
├── run_ingest.py              # Script chạy thu thập
├── process.py                 # Script xử lý dữ liệu
├── load_s3.py                 # Script upload S3
├── load_postgres.py           # Script load vào Supabase
└── README.md                  # File này
```

## Yêu cầu hệ thống

### 1. Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Tạo file `.env` trong thư mục gốc:
```env
# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-southeast-1
S3_BUCKET_NAME=your_bucket_name

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Hướng dẫn chạy từng bước

### Bước 1: Thu thập dữ liệu (Data Ingestion)
```bash
# Chạy thu thập dữ liệu cho ngày hiện tại
python run_ingest.py

# Hoặc chạy cho ngày cụ thể (nếu có date_input trong code)
python run_ingest.py
```

**Kết quả:** Tạo file `marinedata_YYYY-MM-DD.json` trong `data/raw/`

### Bước 2: Xử lý dữ liệu (Data Processing)
```bash
# Xử lý dữ liệu cho ngày hiện tại
python process.py --date 2025-10-25

# Xử lý tất cả file trong thư mục raw
python process.py --all
```

**Kết quả:** 
- File cleaned: `data/processed/cleaned/marinedata_cleaned_YYYY-MM-DD.json`
- File dashboard: `data/processed/dashboard/marinedata_processed_YYYY-MM-DD.json`

### Bước 3: Upload lên S3
```bash
# Upload file cho ngày cụ thể
python load_s3.py 2025-10-25

# Upload tất cả file cleaned
python load_s3.py
```

**Kết quả:** Dữ liệu được upload lên S3 bucket

### Bước 4: Load vào Supabase
```bash
# Load dữ liệu cho ngày cụ thể
python load_postgres.py 2025-10-25

# Load tất cả dữ liệu
python load_postgres.py
```

**Kết quả:** Dữ liệu được lưu vào bảng `hourly_observations` trong Supabase

## Chạy toàn bộ pipeline với Airflow

### 1. Khởi động Airflow
```bash
# Build và khởi động container
docker-compose build --no-cache
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps
```

### 2. Truy cập Airflow UI
- Mở trình duyệt: http://localhost:8082
- Username: `airflow`
- Password: `airflow`

### 3. Chạy DAG
1. Tìm DAG `marine_pipline` trong danh sách
2. Click vào DAG name
3. Click nút "Trigger DAG" để chạy manual
4. Hoặc DAG sẽ tự động chạy lúc 6:00 AM hàng ngày

### 4. Theo dõi logs
- Click vào task để xem chi tiết
- Click vào "Log" để xem log của từng task
- Kiểm tra trạng thái: Success/Failed/Running

## Các vị trí dữ liệu được thu thập

Pipeline thu thập dữ liệu từ 8 vị trí quan trọng:
1. Hải Phòng – Quảng Ninh (vịnh Bắc Bộ)
2. Cù Lao Chàm (ngư trường trung bộ)
3. Ven bờ Quảng Ngãi – Bình Định
4. Ven bờ Ninh Thuận – Bình Thuận
5. Đông bắc đảo Côn Sơn
6. Khu vực Quần đảo Hoàng Sa
7. Khu vực Quần đảo Trường Sa
8. Ngư trường Cà Mau – Kiên Giang

## Dữ liệu thu thập

### Dữ liệu biển (Marine Data)
- `wave_height`: Chiều cao sóng (m)
- `swell_wave_height`: Chiều cao sóng lừng (m)
- `wind_wave_height`: Chiều cao sóng gió (m)
- `wave_period`: Chu kỳ sóng (s)
- `wave_direction`: Hướng sóng (độ)
- `ocean_current_velocity`: Vận tốc dòng chảy (m/s)
- `ocean_current_direction`: Hướng dòng chảy (độ)
- `sea_surface_temperature`: Nhiệt độ mặt biển (°C)
- `sea_level_height_msl`: Mực nước biển (m)

### Dữ liệu thời tiết (Weather Data)
- `temperature_2m`: Nhiệt độ 2m (°C)
- `relative_humidity_2m`: Độ ẩm tương đối (%)
- `pressure_msl`: Áp suất khí quyển (hPa)
- `wind_speed_10m`: Tốc độ gió 10m (m/s)
- `wind_direction_10m`: Hướng gió 10m (độ)
- `precipitation`: Lượng mưa (mm)
- `cloud_cover`: Độ che phủ mây (%)
- `visibility`: Tầm nhìn (km)

### Chỉ số tính toán
- `marine_safety_index`: Chỉ số an toàn biển (0-100)

## Xử lý lỗi thường gặp

### 1. Lỗi thiếu dependencies
```bash
# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 2. Lỗi kết nối API
- Kiểm tra kết nối internet
- Kiểm tra API key (nếu có)
- Thử lại sau vài phút

### 3. Lỗi kết nối S3/Supabase
- Kiểm tra environment variables
- Kiểm tra credentials
- Kiểm tra network connectivity

### 4. Lỗi DAG không chạy
- Kiểm tra logs của DAG processor
- Kiểm tra syntax Python
- Restart Airflow scheduler

## Monitoring và Maintenance

### 1. Kiểm tra logs
```bash
# Xem logs của container
docker-compose logs airflow-scheduler
docker-compose logs airflow-worker

# Xem logs của DAG
# Truy cập Airflow UI > DAG > Task > Log
```

### 2. Cleanup dữ liệu cũ
```bash
# Xóa dữ liệu cũ hơn 30 ngày
find data/raw -name "*.json" -mtime +30 -delete
find data/processed -name "*.json" -mtime +30 -delete
```

### 3. Backup dữ liệu
- Dữ liệu được backup tự động trên S3
- Có thể export từ Supabase khi cần

## Liên hệ và hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs chi tiết
2. Xem lại hướng dẫn này
3. Kiểm tra cấu hình environment variables
4. Liên hệ team phát triển

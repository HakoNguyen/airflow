# ⚙️ Apache Airflow Orchestration Platform

## 🌐 Giới thiệu

Dự án này sử dụng **Apache Airflow** như một **nền tảng điều phối (orchestration platform)** cho các quy trình tự động trong lĩnh vực **Data Engineering, Machine Learning và Automation**.  
Hệ thống cho phép định nghĩa, lên lịch, giám sát và mở rộng các workflow phức tạp — từ **ETL/ELTL pipelines**, **data processing**, đến **AI model training** hoặc **automation jobs**.

Toàn bộ dự án được triển khai bằng **Python**, quản lý bằng **Docker Compose**, và có khả năng mở rộng linh hoạt cho nhiều loại pipeline khác nhau.

---

## 🚀 Tính năng chính

- 🧩 **Orchestrator trung tâm:** quản lý mọi quy trình xử lý dữ liệu, AI, tự động hóa.  
- 📅 **Scheduling & Monitoring:** lập lịch, giám sát trực tiếp qua Airflow UI.  
- 📦 **Hỗ trợ đa pipeline:** mỗi module là một workflow độc lập, có thể tái sử dụng hoặc kết hợp.  
- 🐳 **Triển khai nhanh với Docker Compose:** chạy toàn bộ hệ thống chỉ với 1 lệnh duy nhất.  
- 🧠 **Mở rộng dễ dàng:** thêm module mới (data, ML, API, automation) mà không ảnh hưởng pipeline khác.  
- 📜 **Logging & retry:** ghi log chi tiết và tự động retry khi task thất bại.  

---

## 🧱 Cấu trúc thư mục

```bash
.
├── dags/                     # Chứa toàn bộ DAG workflow
│   └── src/
│       ├── marineV/          # Ứng dụng: pipeline xử lý dữ liệu biển
│       └── ...               # Có thể thêm các pipeline khác 
├── config/                   # Cấu hình Airflow & pipeline
├── logs/                     # Airflow runtime logs (được mount trong container)
├── docker-compose.yaml       # Cấu hình Docker Compose cho toàn hệ thống
├── requirements.txt          # Danh sách thư viện Python cần thiết
├── .env                      # Biến môi trường (bảo mật, không push lên git)
├── .gitignore                # Các file/thư mục bị bỏ qua
└── README.md                 # Tài liệu hướng dẫn chung 

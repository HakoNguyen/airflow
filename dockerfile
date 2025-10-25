# Extend official Airflow image
FROM apache/airflow:3.0.6

# Switch to root to install packages
USER root

# Install system deps if needed (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Install Python dependencies
RUN pip install --no-cache-dir \
    openmeteo-requests \
    requests-cache \
    retry-requests \
    pandas \
    numpy \
    boto3 \
    psycopg2-binary \
    supabase

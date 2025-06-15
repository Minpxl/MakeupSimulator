FROM python:3.8-slim

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    libgtk2.0-dev \
    libboost-all-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 프로젝트 전체 복사
COPY . .

# 실행 명령 (Gradio 앱)
CMD ["python", "Gradio/quick_start/gradio_makeup_transfer.py"]

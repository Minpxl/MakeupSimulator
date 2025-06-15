FROM python:3.8-slim

# 시스템 빌드 도구 및 라이브러리 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgtk2.0-dev \
    libboost-all-dev \
    pkg-config \
    libx11-dev \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements 복사 및 pip 최신화 후 설치
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 프로젝트 전체 복사
COPY . .

# 앱 실행 명령어 (포트 설정은 앱 코드 내에서)
CMD ["python", "Gradio/quick_start/gradio_makeup_transfer.py"]

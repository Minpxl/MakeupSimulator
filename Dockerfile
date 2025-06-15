FROM python:3.8-slim

# 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /app

# pip 업그레이드
RUN pip install --upgrade pip

# dlib 미리 설치
RUN pip install dlib==19.24.2

# 이후 나머지 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt || true  # dlib은 위에서 설치했으므로 실패 무시

# 소스 코드 복사
COPY . .

# 앱 실행
CMD ["python", "Gradio/quick_start/gradio_makeup_transfer.py"]

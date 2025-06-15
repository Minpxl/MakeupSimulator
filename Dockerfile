FROM python:3.8.5

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
    wget \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /app

# dlib 미리 설치
RUN pip install --upgrade pip && pip install dlib==19.24.2

# 이후 requirements.txt 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 코드 복사
COPY . .

# 포트 명시 (Render용)
ENV PORT=7860

# 앱 실행 명령
CMD ["python", "Gradio/quick_start/gradio_makeup_transfer.py"]

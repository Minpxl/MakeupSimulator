FROM python:3.8

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# pip 업그레이드
RUN pip install --upgrade pip

# dlib 설치 (requirements.txt에서는 빼야 함)
RUN pip install dlib==19.24.2

# 나머지 패키지 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 소스코드 복사
COPY . .

CMD ["python", "Gradio/quick_start/gradio_makeup_transfer.py"]

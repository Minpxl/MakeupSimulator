FROM python:3.8

WORKDIR /app

# 시스템 패키지 설치 및 dlib 빌드에 필요한 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    wget \
    unzip \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# 최신 CMake 설치 (기존 cmake 제거 후 최신 버전 설치)
RUN apt-get remove -y cmake && \
    wget https://github.com/Kitware/CMake/releases/download/v3.26.4/cmake-3.26.4-linux-x86_64.sh && \
    mkdir /opt/cmake && \
    sh cmake-3.26.4-linux-x86_64.sh --skip-license --prefix=/opt/cmake && \
    ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake && \
    rm cmake-3.26.4-linux-x86_64.sh

# pip 업그레이드
RUN pip install --upgrade pip

# dlib 설치 (이제 CMake 버전 문제 없음)
RUN pip install dlib==19.24.2

# 프로젝트 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 소스 복사
COPY . .

CMD ["python", "Gradio/quick_start/gradio_makeup_transfer.py"]

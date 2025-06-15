FROM python:3.8

WORKDIR /app

# 기본 의존성 설치 + 최신 CMake 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 최신 CMake 수동 설치
RUN wget https://github.com/Kitware/CMake/releases/download/v3.26.4/cmake-3.26.4-linux-x86_64.sh && \
    mkdir /opt/cmake && \
    sh cmake-3.26.4-linux-x86_64.sh --skip-license --prefix=/opt/cmake && \
    ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake && \
    rm cmake-3.26.4-linux-x86_64.sh

# pip 업그레이드
RUN pip install --upgrade pip

# dlib 설치
RUN pip install dlib==19.24.2

# 나머지 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 소스 코드 복사
COPY . .

CMD ["python", "Gradio/quick_start/gradio_makeup_transfer.py"]

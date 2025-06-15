FROM python:3.8

WORKDIR /app

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    unzip \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# CMake 최신 버전 수동 설치
RUN wget https://github.com/Kitware/CMake/releases/download/v3.26.4/cmake-3.26.4-linux-x86_64.sh && \
    mkdir /opt/cmake && \
    sh cmake-3.26.4-linux-x86_64.sh --skip-license --prefix=/opt/cmake && \
    ln -sf /opt/cmake/bin/cmake /usr/local/bin/cmake && \
    ln -sf /opt/cmake/bin/ccmake /usr/local/bin/ccmake && \
    ln -sf /opt/cmake/bin/cpack /usr/local/bin/cpack && \
    ln -sf /opt/cmake/bin/cmake-gui /usr/local/bin/cmake-gui && \
    ln -sf /opt/cmake/bin/ctest /usr/local/bin/ctest && \
    rm cmake-3.26.4-linux-x86_64.sh

# cmake 경로 확인
RUN cmake --version && which cmake

# pip 업그레이드
RUN pip install --upgrade pip

# dlib 설치
RUN pip install dlib==19.24.2

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 프로젝트 복사
COPY . .

CMD ["python", "Gradio/quick_start/gradio_makeup_transfer.py"]

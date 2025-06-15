FROM python:3.8

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    unzip \
    python3-dev \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev

# 최신 CMake 수동 설치
RUN wget https://github.com/Kitware/CMake/releases/download/v3.26.4/cmake-3.26.4-linux-x86_64.tar.gz && \
    tar -zxvf cmake-3.26.4-linux-x86_64.tar.gz && \
    mv cmake-3.26.4-linux-x86_64 /opt/cmake && \
    ln -sf /opt/cmake/bin/cmake /usr/local/bin/cmake

RUN cmake --version

RUN pip install dlib==19.24.2

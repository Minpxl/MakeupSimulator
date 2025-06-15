FROM python:3.8.5

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    unzip \
    python3-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    curl \
    pkg-config \
    ninja-build \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 최신 CMake 설치 (3.26.4)
RUN wget https://github.com/Kitware/CMake/releases/download/v3.26.4/cmake-3.26.4-linux-x86_64.tar.gz && \
    tar -zxvf cmake-3.26.4-linux-x86_64.tar.gz && \
    mv cmake-3.26.4-linux-x86_64 /opt/cmake && \
    ln -sf /opt/cmake/bin/* /usr/local/bin/ && \
    cmake --version

# dlib clone 및 병렬 빌드
RUN git clone --branch v19.24 --depth 1 https://github.com/davisking/dlib.git /opt/dlib && \
    cd /opt/dlib && \
    mkdir build && cd build && \
    cmake .. -G Ninja && \
    cmake --build . -- -j$(nproc) && \
    cd ../ && \
    python3 setup.py install

# 빌드 확인용
RUN which cmake && cmake --version

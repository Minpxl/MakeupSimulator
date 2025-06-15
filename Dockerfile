FROM python:3.8.5

# 필수 빌드 도구
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
    pkg-config

# 최신 cmake 설치
RUN wget https://github.com/Kitware/CMake/releases/download/v3.26.4/cmake-3.26.4-linux-x86_64.tar.gz && \
    tar -zxvf cmake-3.26.4-linux-x86_64.tar.gz && \
    mv cmake-3.26.4-linux-x86_64 /opt/cmake && \
    ln -sf /opt/cmake/bin/* /usr/local/bin/ && \
    cmake --version
# Clone and build dlib manually
RUN git clone --branch v19.24 --depth 1 https://github.com/davisking/dlib.git /opt/dlib && \
    cd /opt/dlib && \
    mkdir build && cd build && \
    cmake .. && \
    cmake --build . -- -j$(nproc) && \
    cd ../ && \
    python3 setup.py install



RUN which cmake && cmake --version

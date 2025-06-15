# Python 3.8 기반 공식 이미지 사용
FROM python:3.8

# 시스템 의존성 설치
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

# 작업 디렉토리 생성
WORKDIR /app

# pip 최신화
RUN pip install --upgrade pip

# dlib 먼저 설치
RUN pip install dlib==19.24.2

# 프로젝트 의존성 설치 (dlib은 requirements.txt에서 제거해야 함!)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 프로젝트 코드 복사
COPY . .

# 서버용 환경 변수
ENV PORT=7860

# 실행 명령어 (예시)
CMD ["python", "Gradio/quick_start/gradio_makeup_transfer.py"]

FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (SQLite, 타임존)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Asia/Seoul

# 의존성 먼저 설치 (캐시 레이어 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY bot/ ./bot/

# 데이터 디렉토리 생성
RUN mkdir -p data

# 비root 사용자로 실행
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# 봇 실행
CMD ["python", "-m", "bot.main"]

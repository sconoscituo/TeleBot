# TeleBot

개인 AI 비서 텔레그램 봇. Gemini AI 기반으로 대화, 일정관리, 날씨, 뉴스 요약, 지출 기록, 모닝 브리핑을 제공합니다.

## 기능

- **AI 채팅**: Gemini 1.5 Flash 기반 자연어 대화
- **일정 관리**: 일정 추가/조회/리마인더 (Google Calendar 연동 선택)
- **날씨**: OpenWeatherMap 기반 현재 날씨 조회
- **뉴스**: RSS 피드 수집 + AI 요약
- **지출 기록**: 일별/월별 지출 내역 관리
- **모닝 브리핑**: 매일 아침 날씨 + 일정 + 뉴스 자동 전송

## 기술 스택

| 영역 | 기술 |
|------|------|
| 봇 프레임워크 | python-telegram-bot 20.x |
| AI | Google Gemini 1.5 Flash |
| 날씨 | OpenWeatherMap API |
| 뉴스 | RSS 피드 (연합뉴스, 전자신문, 한겨레) |
| 데이터베이스 | SQLite (로컬) |
| 스케줄러 | APScheduler |
| 컨테이너 | Docker |

## 수익 구조

개인 사용 / 오픈소스 프로젝트입니다. 별도 수익 모델 없이 자유롭게 사용하세요.

## 명령어 목록

| 명령어 | 설명 |
|--------|------|
| `/start` | 봇 시작 및 도움말 표시 |
| `/help` | 사용 가능한 명령어 목록 |
| `/chat <메시지>` | AI와 자유 대화 |
| `/schedule` | 일정 관리 메뉴 |
| `/add_schedule` | 새 일정 추가 |
| `/list_schedule` | 등록된 일정 목록 조회 |
| `/reminder` | 리마인더 설정 |
| `/memo` | 메모 관리 메뉴 |
| `/add_memo <내용>` | 메모 추가 |
| `/search_memo <키워드>` | 메모 검색 |
| `/weather` | 현재 날씨 조회 (기본: 서울) |
| `/news` | 최신 뉴스 AI 요약 |
| `/briefing_on` | 모닝 브리핑 구독 |
| `/briefing_off` | 모닝 브리핑 구독 해제 |
| `/expense <금액> <설명>` | 지출 기록 |
| `/expense_today` | 오늘 지출 내역 조회 |
| `/expense_month` | 이번 달 지출 요약 |

## 설치 및 실행

### 사전 요구사항

- Python 3.11+
- Telegram Bot Token ([BotFather](https://t.me/botfather)에서 발급)
- Google Gemini API Key
- OpenWeatherMap API Key (날씨 기능 사용 시)

### 1. 저장소 클론

```bash
git clone https://github.com/sconoscituo/TeleBot.git
cd TeleBot
```

### 2. 가상환경 설정

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 환경 변수 설정 (.env)

프로젝트 루트에 `.env` 파일을 생성합니다:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
DATABASE_PATH=data/assistant.db
GOOGLE_CALENDAR_CREDENTIALS_PATH=  # 선택 사항
```

### 4. 봇 실행

```bash
python -m bot.main
```

### Docker로 실행

```bash
# .env 파일 준비 후
docker compose up -d
```

## 환경 변수 목록

| 변수 | 필수 | 설명 |
|------|------|------|
| `TELEGRAM_BOT_TOKEN` | 필수 | BotFather에서 발급받은 봇 토큰 |
| `GEMINI_API_KEY` | 필수 | Google AI Studio에서 발급 |
| `OPENWEATHER_API_KEY` | 선택 | 날씨 기능 사용 시 필요 |
| `DATABASE_PATH` | 선택 | SQLite DB 경로 (기본: `data/assistant.db`) |
| `GOOGLE_CALENDAR_CREDENTIALS_PATH` | 선택 | Google Calendar OAuth2 인증 파일 경로 |

## 프로젝트 구조

```
TeleBot/
├── bot/
│   ├── main.py          # 봇 진입점
│   ├── config.py        # 환경변수 설정
│   ├── handlers/        # 명령어 핸들러
│   ├── services/        # AI, 날씨, 뉴스 서비스
│   ├── database/        # SQLite 모델 및 쿼리
│   └── utils/           # 공통 유틸리티
├── tests/               # 테스트
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 테스트

```bash
pip install pytest
pytest tests/ -v
```

## 라이선스

MIT

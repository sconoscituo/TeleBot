# TeleBot 설정 가이드

## 프로젝트 소개

텔레그램 봇 기반의 개인 AI 비서입니다. Gemini AI를 활용해 대화, 날씨 조회, 뉴스 요약, 일정 관리, 메모, 지출 기록, 주식/암호화폐 시세 조회 등 다양한 기능을 텔레그램 채팅으로 이용할 수 있습니다.

---

## 1. 필요한 API 키 / 환경변수

| 변수명 | 설명 | 발급 URL |
|--------|------|----------|
| `TELEGRAM_BOT_TOKEN` | 텔레그램 봇 토큰 | [@BotFather](https://t.me/BotFather) |
| `GEMINI_API_KEY` | Google Gemini AI API 키 | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `OPENWEATHER_API_KEY` | 날씨 데이터 API 키 | [OpenWeatherMap](https://home.openweathermap.org/api_keys) |
| `DATABASE_PATH` | SQLite DB 경로 (선택) | 기본값: `data/assistant.db` |
| `GOOGLE_CALENDAR_CREDENTIALS_PATH` | Google Calendar OAuth2 credentials 파일 경로 (선택) | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |

---

## 2. API 키 발급 방법

### TELEGRAM_BOT_TOKEN — 텔레그램 봇 생성 (상세)

1. 스마트폰 또는 PC에서 **텔레그램 앱 설치** ([iOS](https://apps.apple.com/app/telegram-messenger/id686449807) / [Android](https://play.google.com/store/apps/details?id=org.telegram.messenger) / [데스크톱](https://desktop.telegram.org/))
2. 텔레그램 앱에서 검색창에 **`@BotFather`** 검색 후 공식 계정 선택 (파란 체크 아이콘)
3. `/start` 명령어 입력 후 `/newbot` 입력
4. 봇 이름 입력 (예: `My Assistant Bot`)
5. 봇 사용자명 입력 — 반드시 `bot`으로 끝나야 함 (예: `myassistant_bot`)
6. BotFather가 **HTTP API Token** 발급 — 이 값이 `TELEGRAM_BOT_TOKEN`
7. (선택) `/setcommands`로 명령어 목록 등록, `/setdescription`으로 봇 소개 작성

### GEMINI_API_KEY

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 접속
2. Google 계정으로 로그인
3. **"Create API key"** 클릭
4. 발급된 키를 복사

### OPENWEATHER_API_KEY

1. [OpenWeatherMap 회원가입](https://home.openweathermap.org/users/sign_up) 후 로그인
2. 상단 메뉴 **"API keys"** 클릭
3. 기본 키 복사 (또는 **"Generate"**로 신규 발급)
4. 발급 후 약 10분~2시간 활성화 대기

---

## 3. GitHub Secrets 설정

GitHub 레포지토리 → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름 | 값 |
|------------|-----|
| `TELEGRAM_BOT_TOKEN` | BotFather에서 발급받은 토큰 |
| `GEMINI_API_KEY` | Google AI Studio API 키 |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API 키 |

---

## 4. 로컬 개발 환경 설정

### 사전 요구사항

- Python 3.11 이상
- pip

### 설치 순서

```bash
# 1. 저장소 클론
git clone https://github.com/sconoscituo/TeleBot.git
cd TeleBot

# 2. 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경변수 파일 생성
cp .env.example .env
```

### .env 파일 편집

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
GEMINI_API_KEY=AIzaSy...
OPENWEATHER_API_KEY=abc123...
DATABASE_PATH=data/assistant.db
```

---

## 5. 실행 방법

### 로컬 직접 실행

```bash
# 가상환경 활성화 후
python -m bot.main
```

### Docker로 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

---

## 6. 주요 기능 사용법

텔레그램 앱에서 봇을 검색하거나 BotFather가 알려준 링크(`t.me/봇사용자명`)로 봇 채팅방 열기.

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/start` | 봇 시작 및 도움말 표시 | `/start` |
| `/help` | 전체 명령어 목록 | `/help` |
| `/chat` | Gemini AI와 자유 대화 | `/chat 오늘 할 일 정리해줘` |
| `/weather` | 날씨 조회 | `/weather 서울` |
| `/news` | 최신 뉴스 AI 요약 | `/news` |
| `/add_schedule` | 일정 추가 | `/add_schedule 2025-03-21 14:00 회의` |
| `/list_schedule` | 일정 목록 조회 | `/list_schedule` |
| `/reminder` | 리마인더 설정 | `/reminder 30 약 먹기` |
| `/add_memo` | 메모 추가 | `/add_memo 아이디어 정리` |
| `/search_memo` | 메모 검색 | `/search_memo 아이디어` |
| `/expense` | 지출 기록 | `/expense 5000 점심` |
| `/expense_today` | 오늘 지출 조회 | `/expense_today` |
| `/expense_month` | 이번 달 지출 요약 | `/expense_month` |
| `/stock` | 주식 시세 조회 | `/stock AAPL` |
| `/crypto` | 암호화폐 시세 조회 | `/crypto BTC` |
| `/translate` | AI 번역 | `/translate Hello World` |
| `/briefing_on` | 모닝 브리핑 구독 | `/briefing_on` |
| `/briefing_off` | 모닝 브리핑 해제 | `/briefing_off` |

### 모닝 브리핑

`/briefing_on` 명령어 입력 시 매일 오전 정해진 시간에 날씨 + 뉴스 + 오늘 일정을 자동으로 요약 전송합니다.

### 음성 메시지

텍스트 대신 음성 메시지를 보내면 Gemini AI가 음성을 인식해 응답합니다.

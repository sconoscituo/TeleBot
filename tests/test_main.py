"""
TeleBot 봇 설정 로드 테스트
"""
import os
import sys
import pytest

# bot 패키지를 import 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_config_class_importable():
    """Config 클래스가 정상적으로 import 되는지 확인"""
    from bot.config import Config
    assert Config is not None


def test_config_has_required_attributes():
    """Config 클래스에 필수 속성이 존재하는지 확인"""
    from bot.config import Config
    assert hasattr(Config, "TELEGRAM_BOT_TOKEN")
    assert hasattr(Config, "GEMINI_API_KEY")
    assert hasattr(Config, "DATABASE_PATH")


def test_config_has_bot_commands():
    """BOT_COMMANDS 속성이 존재하고 비어있지 않은지 확인"""
    from bot.config import Config
    assert hasattr(Config, "BOT_COMMANDS")
    assert len(Config.BOT_COMMANDS) > 0


def test_config_bot_commands_format():
    """BOT_COMMANDS 각 항목이 (command, description) 형식인지 확인"""
    from bot.config import Config
    for item in Config.BOT_COMMANDS:
        assert len(item) == 2, f"명령어 항목은 2개 요소여야 합니다: {item}"
        assert isinstance(item[0], str)
        assert isinstance(item[1], str)


def test_config_default_values():
    """기본값이 올바르게 설정되는지 확인 (환경변수 미설정 시)"""
    from bot.config import Config
    assert Config.GEMINI_MODEL == "gemini-1.5-flash"
    assert Config.DEFAULT_CITY == "Seoul"
    assert Config.TIMEZONE == "Asia/Seoul"


def test_config_validate_raises_without_tokens():
    """필수 환경변수 미설정 시 validate()가 ValueError를 발생시키는지 확인"""
    from bot.config import Config
    original_token = Config.TELEGRAM_BOT_TOKEN
    original_key = Config.GEMINI_API_KEY

    Config.TELEGRAM_BOT_TOKEN = ""
    Config.GEMINI_API_KEY = ""

    with pytest.raises(ValueError):
        Config.validate()

    # 복원
    Config.TELEGRAM_BOT_TOKEN = original_token
    Config.GEMINI_API_KEY = original_key

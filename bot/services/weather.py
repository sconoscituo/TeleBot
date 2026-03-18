"""
OpenWeatherMap API를 이용한 날씨 조회 서비스
"""
import logging

import httpx

from bot.config import config

logger = logging.getLogger(__name__)

# 날씨 상태 이모지 매핑
WEATHER_EMOJI: dict[str, str] = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
    "Dust": "💨",
    "Sand": "💨",
    "Smoke": "💨",
    "Tornado": "🌪️",
}


async def get_weather(city: str = config.DEFAULT_CITY) -> str:
    """
    도시명으로 현재 날씨 조회 후 포맷된 문자열 반환
    """
    if not config.OPENWEATHER_API_KEY:
        return "날씨 기능을 사용하려면 OPENWEATHER_API_KEY를 설정해주세요."

    url = f"{config.OPENWEATHER_BASE_URL}/weather"
    params = {
        "q": city,
        "appid": config.OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "kr",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        main = data["main"]
        weather = data["weather"][0]
        wind = data.get("wind", {})
        clouds = data.get("clouds", {})

        condition = weather["main"]
        emoji = WEATHER_EMOJI.get(condition, "🌡️")
        description = weather["description"]
        temp = main["temp"]
        feels_like = main["feels_like"]
        temp_min = main["temp_min"]
        temp_max = main["temp_max"]
        humidity = main["humidity"]
        wind_speed = wind.get("speed", 0)
        cloudiness = clouds.get("all", 0)
        city_name = data.get("name", city)
        country = data.get("sys", {}).get("country", "")

        return (
            f"{emoji} **{city_name}, {country} 현재 날씨**\n\n"
            f"🌡 기온: {temp:.1f}°C (체감 {feels_like:.1f}°C)\n"
            f"📊 최저 {temp_min:.1f}°C / 최고 {temp_max:.1f}°C\n"
            f"💧 습도: {humidity}%\n"
            f"💨 풍속: {wind_speed} m/s\n"
            f"☁️ 구름: {cloudiness}%\n"
            f"📝 상태: {description}"
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"'{city}' 도시를 찾을 수 없습니다. 도시명을 영어로 입력해주세요. (예: Seoul, Busan)"
        logger.error("날씨 API 오류: %s", e)
        return f"날씨 정보를 가져오는 중 오류가 발생했습니다: {e.response.status_code}"
    except Exception as e:
        logger.error("날씨 조회 예외: %s", e)
        return f"날씨 조회 중 예외가 발생했습니다: {e}"

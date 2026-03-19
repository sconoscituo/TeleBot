"""텔레봇 구독 플랜"""
from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"   # 월 2,900원

PLAN_LIMITS = {
    PlanType.FREE: {"daily_ai_calls": 10, "weather_history": False, "stock_alerts": False},
    PlanType.PRO:  {"daily_ai_calls": 200, "weather_history": True,  "stock_alerts": True},
}

PLAN_PRICES_KRW = {
    PlanType.FREE: 0,
    PlanType.PRO: 2900,
}

def check_limit(plan: str, feature: str, used: int) -> bool:
    """기능 사용 가능 여부 확인"""
    limits = PLAN_LIMITS.get(PlanType(plan), PLAN_LIMITS[PlanType.FREE])
    limit = limits.get(feature)
    if isinstance(limit, bool):
        return limit
    return used < limit

def get_plan_limits(plan: PlanType) -> dict:
    return PLAN_LIMITS[plan]

def get_plan_price(plan: PlanType) -> int:
    return PLAN_PRICES_KRW[plan]

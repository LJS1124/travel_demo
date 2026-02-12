import math
from typing import Any

from .models import DayPlan, TravelRequest


DESTINATION_DATA = {
    "北京": {
        "spots": ["故宫", "天坛", "颐和园", "南锣鼓巷", "798艺术区"],
        "transport_per_person": 1200,
        "hotel_per_night": 480,
        "ticket_per_day_per_person": 140,
        "meal_per_day_per_person": 180,
    },
    "上海": {
        "spots": ["外滩", "豫园", "上海博物馆", "武康路", "迪士尼小镇"],
        "transport_per_person": 1100,
        "hotel_per_night": 520,
        "ticket_per_day_per_person": 160,
        "meal_per_day_per_person": 200,
    },
    "成都": {
        "spots": ["宽窄巷子", "锦里", "杜甫草堂", "大熊猫基地", "都江堰"],
        "transport_per_person": 1000,
        "hotel_per_night": 420,
        "ticket_per_day_per_person": 130,
        "meal_per_day_per_person": 170,
    },
}

REQUIRED_FIELDS = ["destination", "days", "travelers", "budget_cny"]


def _normalize_request(raw: dict[str, Any]) -> TravelRequest:
    return TravelRequest(
        destination=str(raw["destination"]).strip(),
        days=int(raw["days"]),
        travelers=int(raw["travelers"]),
        budget_cny=float(raw["budget_cny"]),
        preferences=list(raw.get("preferences", [])),
    )


def _validate_request(raw: dict[str, Any]) -> list[str]:
    missing = [field for field in REQUIRED_FIELDS if field not in raw]
    if missing:
        return missing

    try:
        if int(raw["days"]) < 1:
            missing.append("days>=1")
    except (TypeError, ValueError):
        missing.append("days:int")

    try:
        if int(raw["travelers"]) < 1:
            missing.append("travelers>=1")
    except (TypeError, ValueError):
        missing.append("travelers:int")

    try:
        if float(raw["budget_cny"]) <= 0:
            missing.append("budget_cny>0")
    except (TypeError, ValueError):
        missing.append("budget_cny:number")

    destination = str(raw.get("destination", "")).strip()
    if not destination:
        missing.append("destination:non-empty")
    return missing


def _build_itinerary(req: TravelRequest) -> list[dict[str, Any]]:
    city_data = DESTINATION_DATA.get(req.destination, DESTINATION_DATA["北京"])
    spots = city_data["spots"]
    itinerary: list[dict[str, Any]] = []

    for day in range(1, req.days + 1):
        base = (day - 1) * 2
        morning = spots[base % len(spots)]
        afternoon = spots[(base + 1) % len(spots)]
        evening = "本地特色美食 + 自由活动"
        day_plan = DayPlan(day=day, morning=morning, afternoon=afternoon, evening=evening)
        itinerary.append(day_plan.to_dict())

    return itinerary


def _estimate_price(req: TravelRequest) -> dict[str, float]:
    city_data = DESTINATION_DATA.get(req.destination, DESTINATION_DATA["北京"])
    nights = max(req.days - 1, 1)

    transport = city_data["transport_per_person"] * req.travelers
    hotel = city_data["hotel_per_night"] * nights
    tickets = city_data["ticket_per_day_per_person"] * req.days * req.travelers
    meals = city_data["meal_per_day_per_person"] * req.days * req.travelers
    subtotal = transport + hotel + tickets + meals
    service_fee = math.ceil(subtotal * 0.08)
    total = subtotal + service_fee

    return {
        "transport": float(transport),
        "hotel": float(hotel),
        "tickets": float(tickets),
        "meals": float(meals),
        "service_fee": float(service_fee),
        "total": float(total),
    }


def _evaluate_risk(req: TravelRequest, total_price: float) -> tuple[list[str], bool]:
    risk_flags: list[str] = []
    handoff_to_human = False

    if total_price > req.budget_cny:
        risk_flags.append("budget_exceeded")
        if total_price > req.budget_cny * 1.2:
            handoff_to_human = True

    if req.days <= 1:
        risk_flags.append("tight_schedule")

    if req.travelers >= 8:
        risk_flags.append("large_group_manual_review")
        handoff_to_human = True

    if req.destination not in DESTINATION_DATA:
        risk_flags.append("destination_fallback_template")

    return risk_flags, handoff_to_human


def generate_plan(raw_request: dict[str, Any]) -> dict[str, Any]:
    missing_fields = _validate_request(raw_request)
    if missing_fields:
        return {
            "status": "need_more_info",
            "missing_fields": missing_fields,
            "message": "请求信息不完整或不合法，请补充后重试。",
        }

    req = _normalize_request(raw_request)
    itinerary = _build_itinerary(req)
    price_breakdown = _estimate_price(req)
    risk_flags, handoff_to_human = _evaluate_risk(req, price_breakdown["total"])

    return {
        "status": "ok",
        "request_summary": {
            "destination": req.destination,
            "days": req.days,
            "travelers": req.travelers,
            "budget_cny": req.budget_cny,
            "preferences": req.preferences,
        },
        "itinerary": itinerary,
        "price_breakdown": price_breakdown,
        "risk_flags": risk_flags,
        "handoff_to_human": handoff_to_human,
    }

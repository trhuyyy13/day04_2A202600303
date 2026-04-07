from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from langchain_core.tools import tool

# ============================================================================
# MOCK DATA — Dữ liệu giả lập hệ thống du lịch
# Lưu ý: Giá cả có logic (VD: cuối tuần đắt hơn, hạng cao hơn đắt hơn)
# Sinh viên cần đọc hiểu data để debug test cases.
# ============================================================================

FLIGHTS_DB: Dict[Tuple[str, str], List[Dict[str, Any]]] = {
    ("Hà Nội", "Đà Nẵng"): [
        {
            "airline": "Vietnam Airlines",
            "departure": "06:00",
            "arrival": "07:20",
            "price": 1_450_000,
            "class": "economy",
        },
        {
            "airline": "Vietnam Airlines",
            "departure": "14:00",
            "arrival": "15:20",
            "price": 2_800_000,
            "class": "business",
        },
        {
            "airline": "VietJet Air",
            "departure": "08:30",
            "arrival": "09:50",
            "price": 890_000,
            "class": "economy",
        },
        {
            "airline": "Bamboo Airways",
            "departure": "11:00",
            "arrival": "12:20",
            "price": 1_200_000,
            "class": "economy",
        },
    ],
    ("Hà Nội", "Phú Quốc"): [
        {
            "airline": "Vietnam Airlines",
            "departure": "07:00",
            "arrival": "09:15",
            "price": 2_100_000,
            "class": "economy",
        },
        {
            "airline": "VietJet Air",
            "departure": "10:00",
            "arrival": "12:15",
            "price": 1_350_000,
            "class": "economy",
        },
        {
            "airline": "VietJet Air",
            "departure": "16:00",
            "arrival": "18:15",
            "price": 1_100_000,
            "class": "economy",
        },
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {
            "airline": "Vietnam Airlines",
            "departure": "06:00",
            "arrival": "08:10",
            "price": 1_600_000,
            "class": "economy",
        },
        {
            "airline": "VietJet Air",
            "departure": "07:30",
            "arrival": "09:40",
            "price": 950_000,
            "class": "economy",
        },
        {
            "airline": "Bamboo Airways",
            "departure": "12:00",
            "arrival": "14:10",
            "price": 1_300_000,
            "class": "economy",
        },
        {
            "airline": "Vietnam Airlines",
            "departure": "18:00",
            "arrival": "20:10",
            "price": 3_200_000,
            "class": "business",
        },
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {
            "airline": "Vietnam Airlines",
            "departure": "09:00",
            "arrival": "10:20",
            "price": 1_300_000,
            "class": "economy",
        },
        {
            "airline": "VietJet Air",
            "departure": "13:00",
            "arrival": "14:20",
            "price": 780_000,
            "class": "economy",
        },
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {
            "airline": "Vietnam Airlines",
            "departure": "08:00",
            "arrival": "09:00",
            "price": 1_100_000,
            "class": "economy",
        },
        {
            "airline": "VietJet Air",
            "departure": "15:00",
            "arrival": "16:00",
            "price": 650_000,
            "class": "economy",
        },
    ],
}

HOTELS_DB: Dict[str, List[Dict[str, Any]]] = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ],
}


def _format_vnd(amount: int) -> str:
    s = f"{int(amount):,}".replace(",", ".")
    return f"{s}đ"


def _parse_int_money(raw: str) -> int:
    cleaned = raw.strip().lower()
    cleaned = cleaned.replace("vnd", "").replace("đ", "")
    cleaned = cleaned.replace(" ", "")
    cleaned = cleaned.replace("_", "")
    cleaned = cleaned.replace(".", "")
    if not cleaned or not cleaned.isdigit():
        raise ValueError(f"Số tiền không hợp lệ: {raw!r}")
    return int(cleaned)


@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.

    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')

    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    Nếu không tìm thấy tuyến bay, trả về thông báo không có chuyến.
    """

    key = (origin, destination)
    flights = FLIGHTS_DB.get(key)
    note = ""

    if flights is None:
        reverse_key = (destination, origin)
        flights = FLIGHTS_DB.get(reverse_key)
        if flights is None:
            return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."
        note = f"(Không có tuyến {origin} → {destination} trong DB, đang hiển thị tuyến {destination} → {origin} để tham khảo)\n"

    flights_sorted = sorted(flights, key=lambda f: int(f.get("price", 0)))
    lines = [note + f"Các chuyến bay {origin} → {destination}:" if not note else note + f"Các chuyến bay (tham khảo):"]

    for idx, f in enumerate(flights_sorted, start=1):
        airline = f.get("airline", "")
        dep = f.get("departure", "")
        arr = f.get("arrival", "")
        price = _format_vnd(int(f.get("price", 0)))
        seat_class = f.get("class", "")
        lines.append(f"{idx}. {airline} | {dep}-{arr} | {seat_class} | {price}")

    return "\n".join(lines)


@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi đêm.

    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VND), mặc định không giới hạn

    Trả về danh sách khách sạn phù hợp với tên, số sao, giá, khu vực, rating.
    """

    hotels = HOTELS_DB.get(city)
    if not hotels:
        return f"Không có dữ liệu khách sạn cho thành phố: {city}."

    filtered = [h for h in hotels if int(h.get("price_per_night", 0)) <= int(max_price_per_night)]
    if not filtered:
        return (
            f"Không tìm thấy khách sạn tại {city} với giá dưới {_format_vnd(int(max_price_per_night))}/đêm. "
            "Hãy thử tăng ngân sách."
        )

    filtered_sorted = sorted(
        filtered,
        key=lambda h: (
            -float(h.get("rating", 0.0)),
            int(h.get("price_per_night", 0)),
        ),
    )

    lines = [f"Khách sạn tại {city} (<= {_format_vnd(int(max_price_per_night))}/đêm):"]
    for idx, h in enumerate(filtered_sorted, start=1):
        name = h.get("name", "")
        stars = h.get("stars", "")
        area = h.get("area", "")
        rating = h.get("rating", "")
        price = _format_vnd(int(h.get("price_per_night", 0)))
        lines.append(f"{idx}. {name} | {stars}★ | {area} | rating {rating} | {price}/đêm")

    return "\n".join(lines)


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.

    Tham số:
    - total_budget: tổng ngân sách ban đầu (VND)
    - expenses: chuỗi mô tả các khoản chi, mỗi khoản cách nhau bởi dấu phẩy,
      định dạng 'tên_khoản:số_tiền' (VD: 'vé_máy_bay:890000,khách_sạn:650000')

    Trả về bảng chi tiết các khoản chi và số tiền còn lại.
    Nếu vượt ngân sách, cảnh báo rõ ràng số tiền thiếu.
    """

    if expenses is None:
        expenses = ""

    raw = expenses.strip()
    items: List[Tuple[str, int]] = []

    if raw:
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        for part in parts:
            if ":" not in part:
                return (
                    "Sai định dạng expenses. Dùng dạng 'tên_khoản:số_tiền' và ngăn cách bằng dấu phẩy. "
                    "VD: 'vé_máy_bay:890000,khách_sạn:650000'"
                )
            name, money = part.split(":", 1)
            name = name.strip()
            if not name:
                return "Sai định dạng expenses: tên_khoản không được để trống."
            try:
                amount = _parse_int_money(money)
            except ValueError:
                return (
                    "Sai định dạng số tiền trong expenses. "
                    "Chỉ dùng chữ số (có thể có dấu . hoặc _), ví dụ: 1450000 hoặc 1.450.000"
                )
            items.append((name, amount))

    total_spent = sum(amount for _, amount in items)
    remaining = int(total_budget) - int(total_spent)

    lines: List[str] = ["Bảng chi phí:"]
    if items:
        for name, amount in items:
            pretty_name = re.sub(r"[_\-]+", " ", name).strip()
            lines.append(f"- {pretty_name}: {_format_vnd(amount)}")
    else:
        lines.append("- (chưa có khoản chi nào)")

    lines.append("---")
    lines.append(f"Tổng chi: {_format_vnd(total_spent)}")
    lines.append(f"Ngân sách: {_format_vnd(int(total_budget))}")

    if remaining >= 0:
        lines.append(f"Còn lại: {_format_vnd(remaining)}")
    else:
        lines.append(f"Vượt ngân sách: {_format_vnd(-remaining)} (cần điều chỉnh giảm chi phí)")

    return "\n".join(lines)

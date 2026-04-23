from __future__ import annotations

from typing import Iterable


def normalize_time_value(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(".", ":")
    parts = text.split(":")
    if len(parts) != 2:
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return None
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"


def parse_time_range(value: str | None) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    text = str(value).strip()
    if not text or "-" not in text:
        return None, None
    raw_start, raw_end = text.split("-", 1)
    return normalize_time_value(raw_start), normalize_time_value(raw_end)


def normalize_time_range(start: str | None, end: str | None) -> str | None:
    normalized_start = normalize_time_value(start)
    normalized_end = normalize_time_value(end)
    if not normalized_start or not normalized_end:
        return None
    return f"{normalized_start}-{normalized_end}"


def time_to_minutes(value: str | None) -> int | None:
    normalized = normalize_time_value(value)
    if not normalized:
        return None
    hours, minutes = normalized.split(":")
    return int(hours) * 60 + int(minutes)


def ranges_overlap(
    start_a: str | None,
    end_a: str | None,
    start_b: str | None,
    end_b: str | None,
) -> bool:
    a_start = time_to_minutes(start_a)
    a_end = time_to_minutes(end_a)
    b_start = time_to_minutes(start_b)
    b_end = time_to_minutes(end_b)
    if None in (a_start, a_end, b_start, b_end):
        return False
    return a_start < b_end and b_start < a_end


def range_from_start_and_duration(start: str, duration_minutes: int) -> tuple[str | None, str | None]:
    start_minutes = time_to_minutes(start)
    if start_minutes is None:
        return None, None
    end_minutes = start_minutes + duration_minutes
    end_hours = end_minutes // 60
    end_remainder = end_minutes % 60
    return normalize_time_value(start), f"{end_hours:02d}:{end_remainder:02d}"


def build_half_hour_slots(start: str, end: str) -> list[str]:
    start_minutes = time_to_minutes(start)
    end_minutes = time_to_minutes(end)
    if start_minutes is None or end_minutes is None or end_minutes <= start_minutes:
        return []
    slots: list[str] = []
    current = start_minutes
    while current < end_minutes:
        slots.append(f"{current // 60:02d}:{current % 60:02d}")
        current += 30
    return slots


def compress_time_slots(slots: Iterable[str]) -> tuple[str | None, str | None]:
    normalized = sorted(
        {normalize_time_value(slot) for slot in slots if normalize_time_value(slot)},
        key=lambda value: time_to_minutes(value) or 0,
    )
    if not normalized:
        return None, None
    start = normalized[0]
    last = normalized[-1]
    last_minutes = time_to_minutes(last)
    if last_minutes is None:
        return start, None
    end_minutes = last_minutes + 30
    return start, f"{end_minutes // 60:02d}:{end_minutes % 60:02d}"

from __future__ import annotations

import re
from typing import Any, Optional


_TITLE_PREFIXES = {
    "mr",
    "mrs",
    "ms",
    "miss",
    "dr",
    "prof",
    "นาย",
    "นาง",
    "นางสาว",
    "อ",
    "อาจารย์",
    "ผศ",
    "รศ",
    "ศ",
    "ดร",
}

_PLACEHOLDER_LECTURERS = {
    "คณาจารย์",
    "faculty",
    "staff",
    "unknown",
    "n/a",
    "-",
}


def clean_whitespace(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    text = re.sub(r"\s+", " ", text)
    return text or None


def normalize_room_code(value: Any) -> Optional[str]:
    text = clean_whitespace(value)
    if not text:
        return None

    text = text.upper()
    match = re.match(r"^([A-Z]+)\s*([0-9].*)$", text)
    if match:
        suffix = re.sub(r"\s+", " ", match.group(2)).strip()
        text = f"{match.group(1)} {suffix}"

    return text


def room_building_from_code(value: Any) -> Optional[str]:
    room_code = normalize_room_code(value)
    if not room_code:
        return None

    match = re.match(r"^([A-Z]+)", room_code)
    if match:
        return match.group(1)

    return room_code.split(" ", 1)[0]


def normalize_person_name(value: Any) -> Optional[str]:
    text = clean_whitespace(value)
    if not text:
        return None

    text = text.replace(".", " ").replace(",", " ")
    parts = [part for part in re.split(r"\s+", text) if part]
    while parts and parts[0].casefold() in _TITLE_PREFIXES:
        parts.pop(0)

    if not parts:
        return None

    return " ".join(parts).casefold()


def is_placeholder_lecturer(value: Any) -> bool:
    text = clean_whitespace(value)
    if not text:
        return False

    normalized = text.casefold()
    if normalized in _PLACEHOLDER_LECTURERS:
        return True

    placeholder_markers = ("placeholder", "to be announced", "unassigned")
    return any(marker in normalized for marker in placeholder_markers)

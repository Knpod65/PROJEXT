from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List
import io
import re

import pandas as pd
from fastapi import HTTPException, UploadFile


COLUMN_ALIASES = {
    "COURESNO": "COURSENO",
    "ROOM_CAP": "CAPACITY",
}


def _unsupported_file_error() -> HTTPException:
    return HTTPException(
        status_code=400,
        detail="Cannot read file โ€” unsupported format or corrupted",
    )


def _normalize_column_name(name: Any) -> str:
    text = str(name or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text.upper()


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [
        COLUMN_ALIASES.get(_normalize_column_name(column), _normalize_column_name(column))
        for column in normalized.columns
    ]
    return normalized


def _normalize_scalar(value: Any) -> Any:
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass

    if hasattr(value, "item") and not isinstance(value, (str, bytes, dict, list, tuple, set)):
        try:
            value = value.item()
        except Exception:
            pass

    if isinstance(value, str):
        value = re.sub(r"\s+", " ", value).strip()
        return value or None

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def _dataframe_to_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for row_number, record in enumerate(df.to_dict(orient="records")):
        normalized_record = {
            key: _normalize_scalar(value)
            for key, value in record.items()
        }
        rows.append({"_row": row_number, **normalized_record})
    return rows


def _read_csv(content: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")


def _read_xlsx(content: bytes, sheet_name: str | int | None = None) -> pd.DataFrame:
    effective_sheet = 0 if sheet_name is None else sheet_name
    return pd.read_excel(io.BytesIO(content), engine="openpyxl", sheet_name=effective_sheet)


def _read_xls(content: bytes, sheet_name: str | int | None = None) -> pd.DataFrame:
    try:
        effective_sheet = 0 if sheet_name is None else sheet_name
        return pd.read_excel(io.BytesIO(content), engine="xlrd", sheet_name=effective_sheet)
    except Exception:
        tables = pd.read_html(io.BytesIO(content), encoding="utf-8")
        if not tables:
            raise _unsupported_file_error()
        return tables[0]


def _parse_content(filename: str, content: bytes, sheet_name: str | int | None = None) -> pd.DataFrame:
    normalized_filename = filename.lower()
    if not normalized_filename:
        raise _unsupported_file_error()

    try:
        if normalized_filename.endswith(".csv"):
            df = _read_csv(content)
        elif normalized_filename.endswith(".xlsx"):
            df = _read_xlsx(content, sheet_name=sheet_name)
        elif normalized_filename.endswith(".xls"):
            df = _read_xls(content, sheet_name=sheet_name)
        else:
            raise _unsupported_file_error()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Cannot read file โ€” unsupported format or corrupted",
        ) from exc

    return normalize_column_names(df)


def read_file_by_type(file: UploadFile, sheet_name: str | int | None = None) -> List[Dict[str, Any]]:
    content = file.file.read()
    df = _parse_content(file.filename or "", content, sheet_name=sheet_name)
    return _dataframe_to_rows(df)


def read_path_by_type(path: str | Path, sheet_name: str | int | None = None) -> List[Dict[str, Any]]:
    source_path = Path(path)
    df = _parse_content(source_path.name, source_path.read_bytes(), sheet_name=sheet_name)
    return _dataframe_to_rows(df)

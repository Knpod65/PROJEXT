def error_detail(
    detail: str,
    message_key: str,
    params: dict | None = None,
) -> dict:
    return {
        "detail": detail,
        "message_key": message_key,
        "params": params or {},
    }
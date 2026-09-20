from __future__ import annotations

import io
import json
from pathlib import Path

import pandas as pd


ALIASES = {
    "timestamp": ["timestamp", "time", "datetime", "date", "createTime", "CreateTime"],
    "sender": ["sender", "sender_name", "senderName", "nickname", "displayName"],
    "content": ["content", "text", "message", "msg", "displayContent", "StrContent"],
    "message_type": ["message_type", "type", "type_name", "msg_type", "localType"],
    "conversation": ["conversation", "conversation_name", "talker", "StrTalker", "chat_name"],
}


def _pick(df: pd.DataFrame, names: list[str]) -> str | None:
    lower = {str(c).lower(): c for c in df.columns}
    for name in names:
        if name in df.columns:
            return name
        if name.lower() in lower:
            return lower[name.lower()]
    return None


def _time(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    if len(values) and numeric.notna().mean() > 0.8:
        median = numeric.dropna().abs().median()
        unit = "ms" if median > 10_000_000_000 else "s"
        return pd.to_datetime(numeric, unit=unit, errors="coerce")
    return pd.to_datetime(values, errors="coerce")


def normalize_messages(df: pd.DataFrame, default_conversation: str = "") -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    t = _pick(df, ALIASES["timestamp"])
    s = _pick(df, ALIASES["sender"])
    c = _pick(df, ALIASES["content"])
    mt = _pick(df, ALIASES["message_type"])
    conv = _pick(df, ALIASES["conversation"])

    out["timestamp"] = _time(df[t]) if t else pd.NaT
    out["sender"] = df[s].fillna("Unknown").astype(str) if s else "Unknown"
    out["content"] = df[c].fillna("").astype(str) if c else ""
    out["message_type"] = df[mt].fillna("text").astype(str) if mt else "text"
    out["conversation"] = (
        df[conv].fillna(default_conversation).astype(str) if conv else default_conversation
    )
    out["content"] = out["content"].str.replace(r"\s+", " ", regex=True).str.strip()
    return out.sort_values("timestamp", na_position="last").reset_index(drop=True)


def _decode(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def parse_uploaded_file(filename: str, data: bytes) -> pd.DataFrame:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(io.StringIO(_decode(data)))
    elif suffix == ".json":
        payload = json.loads(_decode(data))
        if isinstance(payload, dict):
            payload = next(
                (payload[k] for k in ("messages", "data", "records", "items") if isinstance(payload.get(k), list)),
                [payload],
            )
        frame = pd.json_normalize(payload)
    else:
        raise ValueError("MVP 当前优先支持 CSV / JSON；TXT / HTML 适配会在下一版补上。")
    return normalize_messages(frame)

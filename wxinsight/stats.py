from __future__ import annotations

import re

import jieba.analyse
import pandas as pd


STOPWORDS = {
    "这个", "那个", "就是", "然后", "可以", "还是", "一个", "什么",
    "没有", "不是", "我们", "你们", "他们", "自己", "已经", "因为",
    "所以", "但是", "如果", "感觉", "好的", "收到", "知道", "一下",
}


def compute_metrics(df: pd.DataFrame) -> dict:
    valid = df["timestamp"].dropna()
    active_days = int(valid.dt.date.nunique()) if not valid.empty else 0
    return {
        "message_count": int(len(df)),
        "participant_count": int(df["sender"].nunique()),
        "active_days": active_days,
        "avg_messages_per_day": len(df) / max(active_days, 1),
        "start_at": valid.min().strftime("%Y-%m-%d %H:%M") if not valid.empty else None,
        "end_at": valid.max().strftime("%Y-%m-%d %H:%M") if not valid.empty else None,
    }


def daily_activity(df: pd.DataFrame) -> pd.DataFrame:
    timed = df.dropna(subset=["timestamp"]).copy()
    if timed.empty:
        return pd.DataFrame({"date": [], "messages": []})
    timed["date"] = timed["timestamp"].dt.date
    return timed.groupby("date", as_index=False).size().rename(columns={"size": "messages"})


def hourly_activity(df: pd.DataFrame) -> pd.DataFrame:
    timed = df.dropna(subset=["timestamp"]).copy()
    if timed.empty:
        return pd.DataFrame({"hour": list(range(24)), "messages": [0] * 24})
    timed["hour"] = timed["timestamp"].dt.hour
    grouped = timed.groupby("hour").size().reindex(range(24), fill_value=0)
    return grouped.rename("messages").reset_index()


def sender_activity(df: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    return (
        df.groupby("sender").size().sort_values(ascending=False).head(limit)
        .rename("messages").reset_index()
    )


def top_keywords(df: pd.DataFrame, limit: int = 25) -> pd.DataFrame:
    text = "\n".join(df["content"].fillna("").astype(str))
    text = re.sub(r"https?://\S+", " ", text)
    if len(text.strip()) < 20:
        return pd.DataFrame(columns=["keyword", "score"])
    pairs = jieba.analyse.extract_tags(text, topK=limit * 3, withWeight=True)
    cleaned = [
        (word.strip(), float(score))
        for word, score in pairs
        if len(word.strip()) >= 2 and word.strip() not in STOPWORDS
    ][:limit]
    return pd.DataFrame(cleaned, columns=["keyword", "score"])

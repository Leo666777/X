from __future__ import annotations

import pandas as pd
import streamlit as st

from wxinsight.parsers import parse_uploaded_file
from wxinsight.stats import (
    compute_metrics,
    daily_activity,
    hourly_activity,
    sender_activity,
    top_keywords,
)


st.set_page_config(page_title="WxInsight", page_icon="💬", layout="wide")
st.title("💬 WxInsight")
st.caption("微信聊天记录本地解析、统计与导出。")

uploaded = st.file_uploader("上传聊天记录", type=["csv", "json"])
df: pd.DataFrame | None = None

if uploaded is not None:
    try:
        df = parse_uploaded_file(uploaded.name, uploaded.getvalue())
    except Exception as exc:
        st.error(f"解析失败：{exc}")

if df is not None and not df.empty:
    st.success(f"已解析 {len(df):,} 条消息")
    st.subheader("数据预览")
    st.dataframe(df.head(200), use_container_width=True, hide_index=True)

    st.download_button(
        "下载规范化 CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="wechat_messages_normalized.csv",
        mime="text/csv",
    )

    st.subheader("本地统计")
    metrics = compute_metrics(df)
    a, b, c, d = st.columns(4)
    a.metric("消息数", f"{metrics['message_count']:,}")
    b.metric("参与者", metrics["participant_count"])
    c.metric("活跃天数", metrics["active_days"])
    d.metric("日均消息", f"{metrics['avg_messages_per_day']:.1f}")

    if metrics["start_at"]:
        st.caption(f"时间范围：{metrics['start_at']} → {metrics['end_at']}")

    left, right = st.columns(2)
    with left:
        st.markdown("#### 每日消息趋势")
        st.line_chart(daily_activity(df), x="date", y="messages")
        st.markdown("#### 发送者消息量")
        st.bar_chart(sender_activity(df), x="sender", y="messages")
    with right:
        st.markdown("#### 24 小时活跃分布")
        st.bar_chart(hourly_activity(df), x="hour", y="messages")
        st.markdown("#### 高频关键词")
        words = top_keywords(df)
        if words.empty:
            st.info("文本内容不足。")
        else:
            st.bar_chart(words, x="keyword", y="score")

    st.info("所有统计都在当前运行机器本地完成。")

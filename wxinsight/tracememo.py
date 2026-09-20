from __future__ import annotations

from typing import Any

import pandas as pd
import requests

from .parsers import normalize_messages


class TraceMemoError(RuntimeError):
    pass


class TraceMemoClient:
    def __init__(self, base_url: str = "http://127.0.0.1:6131", token: str = "", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        return headers

    def health(self) -> dict[str, Any]:
        return self._get("/api/v1/health", auth=False)

    def _get(self, path: str, params: dict[str, Any] | None = None, auth: bool = True) -> dict[str, Any]:
        headers = self._headers() if auth else {"Accept": "application/json"}
        try:
            response = requests.get(
                self.base_url + path,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise TraceMemoError(
                "无法连接 TraceMemo，请确认应用和 Local HTTP API 已启动。"
            ) from exc

        if response.status_code == 401:
            raise TraceMemoError("TraceMemo 返回 401，请检查 API Center 中的 Token。")
        if response.status_code == 503:
            raise TraceMemoError("TraceMemo 数据库尚未就绪，请先完成微信数据连接。")
        if not response.ok:
            raise TraceMemoError(
                f"TraceMemo 请求失败：HTTP {response.status_code} - {response.text[:300]}"
            )
        try:
            return response.json()
        except ValueError as exc:
            raise TraceMemoError("TraceMemo 返回的不是有效 JSON。") from exc

    def chatlog(self, talker: str, time_range: str | None = None) -> pd.DataFrame:
        params: dict[str, str] = {"talker": talker}
        if time_range:
            params["time"] = time_range
        payload = self._get("/api/v1/chatlog", params=params)
        messages = payload.get("messages")
        if not isinstance(messages, list):
            raise TraceMemoError("响应中没有 messages 数组，可能是 API 版本发生变化。")
        return normalize_messages(pd.json_normalize(messages), default_conversation=talker)

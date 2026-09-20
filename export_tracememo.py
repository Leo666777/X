from __future__ import annotations

import argparse
import os
from pathlib import Path

from wxinsight.tracememo import TraceMemoClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Export one TraceMemo conversation to normalized CSV.")
    parser.add_argument("--talker", required=True, help="Contact or group name")
    parser.add_argument("--time", default=None, help="Date or range, e.g. 2026-09-01~2026-09-20")
    parser.add_argument("--base-url", default="http://127.0.0.1:6131")
    parser.add_argument("--out", default="wechat_messages.csv")
    args = parser.parse_args()

    token = os.getenv("TRACEMEMO_API_TOKEN", "")
    if not token:
        raise SystemExit("Set TRACEMEMO_API_TOKEN in your local environment first.")

    client = TraceMemoClient(base_url=args.base_url, token=token)
    frame = client.chatlog(talker=args.talker, time_range=args.time)

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"Exported {len(frame)} messages to {output}")


if __name__ == "__main__":
    main()

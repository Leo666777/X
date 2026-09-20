# WxInsight

一个本地优先的微信聊天记录导出与分析 MVP。

## 现在能做什么

- 从 TraceMemo Local HTTP API 拉取指定联系人 / 群聊聊天记录
- 保存为统一 CSV：`timestamp,sender,content,message_type,conversation`
- 上传 CSV / JSON 到本地 Streamlit 页面
- 查看：
  - 消息总量
  - 参与者数量
  - 活跃天数
  - 每日消息趋势
  - 24 小时活跃分布
  - 发送者消息量
  - 中文高频关键词
- 导出规范化 CSV，继续交给 ChatGPT / Codex / 本地模型做更深层分析

## 为什么不自己重新做微信数据库破解

调研后，现有项目已经把微信 4.x 的本地数据读取和导出做得更成熟：

- TraceMemo: https://github.com/Wxw-Gu/TraceMemo
- WeFlow: https://github.com/iminc/WeFlow
- WeChatMsg: https://github.com/little-KaoKao/WeChatMsg

其中 TraceMemo 已提供 Local HTTP API，默认监听：

```text
http://127.0.0.1:6131
```

并提供：

```text
GET /api/v1/health
GET /api/v1/contact
GET /api/v1/recent_chat
GET /api/v1/chatlog
```

除 health 外的数据接口需要 Bearer Token。

PyWxDump 原作者已在 2025-10 说明因合规风险停止维护并移除核心代码，所以本项目不以它作为底层依赖。

## 架构

```text
微信 PC
  ↓
TraceMemo / WeFlow
  ↓
结构化聊天数据
  ↓
WxInsight
  ├─ 字段规范化
  ├─ 本地统计
  ├─ 可视化
  └─ 导出规范化 CSV
        ↓
   ChatGPT / Codex / 本地模型
```

## 安装

需要 Python 3.10+。

```bash
git clone https://github.com/Leo666777/X.git
cd X

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

## 方式 A：直接从 TraceMemo 导出

先在 TraceMemo 中：

1. 完成你自己的微信数据连接
2. 打开 API Center
3. 启动 Local HTTP API
4. 复制 Token

然后只在你自己的本机终端设置环境变量，不要把 Token 写进 Git：

Windows PowerShell：

```powershell
$env:TRACEMEMO_API_TOKEN="YOUR_TOKEN"
```

macOS / Linux：

```bash
export TRACEMEMO_API_TOKEN="YOUR_TOKEN"
```

导出一个会话：

```bash
python export_tracememo.py --talker "张三" --out data/zhangsan.csv
```

指定时间范围：

```bash
python export_tracememo.py \
  --talker "技术交流群" \
  --time "2026-09-01~2026-09-20" \
  --out data/group.csv
```

## 方式 B：使用 TraceMemo / WeFlow 已导出的文件

MVP 当前优先支持：

- CSV
- JSON

运行分析页面：

```bash
streamlit run app.py
```

然后上传聊天记录文件即可。

## 支持的常见字段

时间字段会自动尝试识别：

```text
timestamp
time
datetime
date
createTime
CreateTime
```

发送者：

```text
sender
sender_name
senderName
nickname
displayName
```

消息内容：

```text
content
text
message
msg
displayContent
StrContent
```

会话：

```text
conversation
conversation_name
talker
StrTalker
chat_name
```

## 隐私原则

- 不把微信数据库提交到仓库
- 不把 TraceMemo Token 提交到仓库
- 默认统计只在本机运行
- 只处理你有权访问和分析的聊天记录
- 需要 AI 深度分析时，建议先缩小聊天范围，再决定是否发送给云端模型

## 下一步

优先级：

1. TraceMemo 联系人 / 群聊选择器
2. TXT / HTML 导出格式适配
3. WeFlow HTTP API 直连
4. SQLite 本地聊天仓库
5. 跨聊天 RAG 检索
6. 重要事件 / 决定 / 承诺 / 待办时间线
7. 群聊成员画像
8. 年度报告

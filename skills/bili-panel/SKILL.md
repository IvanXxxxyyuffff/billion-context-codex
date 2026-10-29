---
name: bili-panel
description: "billion-context 看板：会话上下文管理实时统计面板。当用户要看板/dashboard/上下文管理情况/上下文压缩/token统计/缓存命中率时使用。调用 mcp__bili__acp_status 和 mcp__bili__acp_cache 工具获取数据，渲染中文统计面板。Use this skill WHENEVER the user asks for dashboard/看板/上下文管理/压缩情况/token统计/缓存命中率/上下文用量, or wants to check billion-context compression status."
version: 1.0.0
user-invocable: true
argument-hint: "[summary|full] [session_id]"
---

# billion-context 看板（bili-panel）

一句话：**从 `mcp__bili__*` 工具拉实时数据 → 渲染统计面板**。数据源头是 bili 代理（`http://127.0.0.1:8790`），工具不可用时兜底走 HTTP 端点。

## 何时触发

| 用户说 | 动作 |
|---|---|
| 看板 / dashboard / 面板 | 渲染完整面板 |
| 上下文管理情况 / 压缩情况 | 渲染完整面板 |
| token 统计 / 用量 | 面板 + 逐会话表 |
| 缓存命中率 / cache hit | 面板 + `acp_cache` 详情 |
| 压缩了多少 / 省了多少 | 面板 + 节省量高亮 |
| acp 状态 / acp_status | 直接透传工具输出 |

## 数据获取（按优先级）

### 首选：MCP 工具

```text
mcp__bili__acp_status      → 上下文用量、可压缩区间、会话状态
mcp__bili__acp_cache       → 缓存命中率账本（detail="summary"）
mcp__bili__acp_cache detail="full" → 完整账本（用户要细看时）
```

### 兜底：HTTP 端点（工具挂了或未加载时）

```bash
curl -s http://127.0.0.1:8790/__bili/overview | python3 -c "
import json,sys
d = json.load(sys.stdin)['overview']
print(f\"sessions: {d.get('sessions')}\")
print(f\"live: {d.get('live')}\")
print(f\"requests: {d.get('requests'):,}\")
print(f\"input tokens: {d.get('inputTokens'):,}\")
print(f\"cached: {d.get('cachedTokens'):,}\")
print(f\"hit rate: {d.get('hitPct')}%\")
print(f\"blocks: {d.get('blocks')}\")
print(f\"tokens saved: {d.get('tokensSaved'):,}\")
print(f\"cost USD: \${d.get('costUsdTotal'):.2f}\")
print(f\"saved USD: \${d.get('savedUsdTotal'):.2f}\")
"

# 逐会话明细
curl -s http://127.0.0.1:8790/__bili/sessions | python3 -c "
import json,sys
d = json.load(sys.stdin)
for s in d.get('sessions', [])[:15]:
    title = (s.get('title') or 'untitled')[:40]
    print(f\"{s['id'][-12:]}  {title:42s}  {s.get('requests',0):>6} req  {s.get('contextTokens',0):>8} tok  {s.get('cacheHitPct',0):>3}%  {s.get('blocks',0):>4} folds\")
"
```

代理没跑时的启动命令：

```bash
export PATH="$HOME/.local/bin:$PATH"
bili start --port 8790 &
sleep 3
curl -s http://127.0.0.1:8790/__bili/health
```

## 面板渲染格式

用户没特别说明时，按这个结构输出：

```markdown
## 📊 billion-context 看板

### 概览

| 指标 | 数值 |
|---|---|
| 活跃会话 | N live / M total |
| 总请求数 | NNN,NNN |
| 总输入 token | N,NNN,NNN,NNN |
| 命中缓存 | N,NNN,NNN,NNN（NN%） |
| 压缩块 | N,NNN |
| 节省 token | N,NNN,NNN |
| 实际花费 | $NNN.NN |
| 因压缩节省 | $N,NNN.NN |

### 缓存健康度

> ✅ HEALTHY（95–97% 为健康）/ ⚠️ 低于 85% 需查归因

主要流失原因（按 `acp_cache` 拆分）：
- 新内容：NN%
- 压缩回付：N%
- TTL/客户端重写：N%

### 最近会话（TOP 10）

| 会话 | 请求 | 上下文 | 命中率 | 折叠数 |
|---|---|---|---|---|
| （逐会话填入） | | | | |

### 下一步建议

（若命中率 < 85%：给出归因分析；若压缩块为 0：说明压缩未触发；若正常：无建议）
```

## 面板规则

1. **全部真实数据**——工具返回什么就渲染什么，不编造数值。
2. **代理没跑**就给启动命令，不渲染假面板。
3. **`acp_cache` summary 够用**，只有用户明确要细看才用 `full`。
4. **逐会话表**只列 TOP 10（按 `lastSeen` 倒序），避免刷屏。
5. **token 数用千位分隔符**，节省金额保留 2 位小数。
6. **健康度判定**：`hitPct` ≥ 85% → ✅；< 85% → ⚠️ + 归因建议。
7. 会话标题截断到 40 字符，ID 只显示最后 12 位。

## 工具不可用时的降级

| 情况 | 动作 |
|---|---|
| `mcp__bili__*` 工具未出现 | 兜底 curl HTTP 端点 |
| 代理未启动 | 输出启动命令 + 等用户确认后重试 |
| 端口不是 8790 | 提示用户确认 `bili start --port N` 的 N，改用该端口 |
| 配置文件里没配端口 | 默认 8787 |

## 与主仓库的关系

- 主仓库 README：安装说明 + 架构
- 本技能：Codex 会话内的看板入口
- Web UI（`http://127.0.0.1:8790/__bili/`）：浏览器端完整面板（折线图 / 配置编辑器）

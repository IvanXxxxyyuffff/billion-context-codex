# billion-context-codex

[中文](#中文) | [English](#english)

<a id="english"></a>

## English

**billion-context for Codex** — context compression plugin + dashboard skill for the OpenAI Codex desktop app.

Ported from [Tyan66666/billion-context-dsh](https://github.com/Tyan66666/billion-context-dsh) (DSH adaptation of [ranxianglei/billion-context](https://github.com/ranxianglei/billion-context)), adapted for Codex desktop.

### What you get

| Component | What it does | Source |
|---|---|---|
| `bili` proxy | Compression engine — the model calls `compress`/`decompress` to fold conversation ranges into high-fidelity summaries | billion-context npm package |
| MCP tools bridge | Exposes 7 ACP tools natively in Codex via `[mcp_servers.bili]` | `billion-context/dist/mcp.js` |
| `bili-panel` skill | Model-invocable dashboard skill — ask "看板 / dashboard / 上下文管理" and the model calls `acp_status`/`acp_cache` and renders a live stats panel | this repo |

### Tools exposed

| Tool | Purpose |
|---|---|
| `compress` | Model folds consumed ranges into summaries |
| `decompress` | Restore folded content (per-block / per-range / to-file) |
| `search_context` | Search compressed blocks by keyword |
| `acp_status` | Context usage + compressible ranges |
| `acp_cache` | Prompt-cache hit-rate ledger (new content / comp re-pay / TTL miss split) |
| `acp_retrieve` | Retrieve full text of a CCR-stored tool result |
| `acp_read_original_image` | Read the full-res image of a downscaled message |

### Install

```bash
# 1. install billion-context (provides `bili` proxy + MCP bridge)
npm install -g billion-context --prefix=~/.local
export PATH="$HOME/.local/bin:$PATH"

# 2. install the MCP bridge into Codex
bili plugin install codex

# 3. start the proxy (keep it running)
bili start --port 8790 &

# 4. install the dashboard skill
mkdir -p ~/.codex/skills/bili-panel
curl -sL https://raw.githubusercontent.com/IvanXxxxyyuffff/billion-context-codex/main/skills/bili-panel/SKILL.md \
  -o ~/.codex/skills/bili-panel/SKILL.md

# 5. restart Codex → tools appear under mcp__bili__*
```

### Verify

```bash
curl -s http://127.0.0.1:8790/__bili/health
# {"ok":true,...}

curl -s http://127.0.0.1:8790/__bili/plugin/manifest | python3 -c "import json,sys; [print(t['name']) for t in json.load(sys.stdin)['tools']['anthropic']]"
# compress / decompress / search_context / acp_status / acp_cache / acp_retrieve / acp_read_original_image
```

### Dashboard

In any Codex session, say: **看板** / **dashboard** / **上下文管理情况** — the skill makes the model call `acp_status` + `acp_cache` and render a stats panel. Or open the built-in web UI directly: `http://127.0.0.1:8790/__bili/`.

The proxy's web UI also shows: session list with per-session tokens/folds/hit-rate, live log, config editor, cache attribution charts.

### Configuration

`~/.config/billion-context/billion-context.json` — key fields for Codex:

```json
{
  "compress": {
    "modelContextLimit": 1000000,
    "maxContextLimit": "25%",
    "emergencyThresholdPercent": "85%",
    "nudgeGrowthTokens": 60000,
    "minCompressRangeChars": 20000,
    "outputHeadroomMaxPct": 0.1
  },
  "providers": {
    "http://127.0.0.1:3425/v1": {
      "models": {
        "trae-cn/glm-5.3-flash-max": { "context": 1000000, "output": 64000 }
      }
    }
  }
}
```

### Credits

- [ranxianglei/billion-context](https://github.com/ranxianglei/billion-context) — the engine (acp-kernel)
- [Tyan66666/billion-context-dsh](https://github.com/Tyan66666/billion-context-dsh) — the DSH adaptation this port is modeled after

---

<a id="中文"></a>

## 中文

**billion-context for Codex** — 上下文压缩插件 + 看板技能，适配 OpenAI Codex 桌面端。

从 [Tyan66666/billion-context-dsh](https://github.com/Tyan66666/billion-context-dsh)（[ranxianglei/billion-context](https://github.com/ranxianglei/billion-context) 的 DSH 适配版）移植到 Codex。

### 组件

| 组件 | 作用 | 来源 |
|---|---|---|
| `bili` 代理 | 压缩内核——模型自主调用 `compress`/`decompress` 把已消费区间折叠成高保真摘要 | billion-context npm 包 |
| MCP 工具桥 | 经 `[mcp_servers.bili]` 在 Codex 里原生暴露 7 个 ACP 工具 | `billion-context/dist/mcp.js` |
| `bili-panel` 技能 | 模型可调的看板技能——说"看板 / dashboard / 上下文管理"时，模型调 `acp_status`/`acp_cache` 渲染实时统计面板 | 本仓库 |

### 暴露的工具

| 工具 | 用途 |
|---|---|
| `compress` | 模型把已消费区间折叠成摘要 |
| `decompress` | 恢复折叠内容（按块 / 按区间 / 落盘文件） |
| `search_context` | 关键词搜索压缩块 |
| `acp_status` | 上下文用量 + 可压缩区间 |
| `acp_cache` | Prompt-cache 命中率账本（新内容 / 压缩回付 / TTL 失效拆分） |
| `acp_retrieve` | 取回 CCR 落盘工具结果的完整原文 |
| `acp_read_original_image` | 读取被降采样消息的原始全分辨率图片 |

### 安装

```bash
# 1. 安装 billion-context（提供 `bili` 代理 + MCP 桥）
npm install -g billion-context --prefix=~/.local
export PATH="$HOME/.local/bin:$PATH"

# 2. 把 MCP 桥装进 Codex
bili plugin install codex

# 3. 启动代理（保持常驻）
bili start --port 8790 &

# 4. 安装看板技能
mkdir -p ~/.codex/skills/bili-panel
curl -sL https://raw.githubusercontent.com/IvanXxxxyyuffff/billion-context-codex/main/skills/bili-panel/SKILL.md \
  -o ~/.codex/skills/bili-panel/SKILL.md

# 5. 重启 Codex → 工具以 mcp__bili__* 出现
```

### 验证

```bash
curl -s http://127.0.0.1:8790/__bili/health
# {"ok":true,...}

curl -s http://127.0.0.1:8790/__bili/plugin/manifest | python3 -c "import json,sys; [print(t['name']) for t in json.load(sys.stdin)['tools']['anthropic']]"
# compress / decompress / search_context / acp_status / acp_cache / acp_retrieve / acp_read_original_image
```

### 看板

在任何 Codex 会话里说：**看板** / **dashboard** / **上下文管理情况** —— 技能让模型调用 `acp_status` + `acp_cache` 渲染统计面板。或直接开内置 Web UI：`http://127.0.0.1:8790/__bili/`。

代理的 Web UI 还能看到：会话列表（逐会话 token/折叠数/命中率）、实时日志、配置编辑器、缓存归因图表。

### 配置

`~/.config/billion-context/billion-context.json` —— Codex 相关的关键字段见上方英文节。

### 致谢

- [ranxianglei/billion-context](https://github.com/ranxianglei/billion-context) — 压缩内核（acp-kernel）
- [Tyan66666/billion-context-dsh](https://github.com/Tyan66666/billion-context-dsh) — 本移植的蓝本

---

## bili-panel 独立插件（v1.0.0）

`marketplace/` 目录是 bili-panel 独立插件市场根。它与 teamboard 完全独立、有自己的压缩漏斗图标。

安装：把 `marketplace/` 指到本地路径，或把仓库克隆到本地后在 `~/.codex/config.toml` 里追加：

```toml
[plugins."bili-panel@bili-local"]
enabled = true

[marketplaces.bili-local]
source_type = "local"
source = "<repo>/marketplace"
```

重启 Codex 后，侧边栏出现「bili 看板」（自带压缩漏斗图标）；对话里喊「打开 bili 看板」也能内嵌打开。

启动 bili 代理：

```bash
export PATH="$HOME/.local/bin:$PATH"
bili start --port 8790
```

指标：会话 / 请求 / 输入 token / 缓存命中率 / 压缩块 / 节省 token / 花费 / 压缩节省（USD）+ 近期会话列表。

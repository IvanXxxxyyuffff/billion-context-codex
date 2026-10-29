---
name: bili-panel
description: billion-context 上下文管理看板。当用户问「上下文管理 / token 用量 / 缓存命中率 / 压缩块 / bili 看板」或要打开 bili 看板时使用。
---

# bili 看板

数据来自本地 bili 代理（默认 `http://127.0.0.1:8790`，可用 `BILI_URL` 覆盖）。
服务没起时先确认：

```bash
curl -s -m 3 http://127.0.0.1:8790/__bili/status >/dev/null && echo up || echo down
export PATH="$HOME/.local/bin:$PATH" && bili start --port 8790
```

## 工具

| 工具 | 用途 |
|---|---|
| `bili_panel` | 内嵌打开看板：会话 / token / 缓存命中率 / 压缩块 / 节省量 / 近期会话 |
| `bili_api` | 只读代理 `/__bili/*`（面板内部取数用） |

## 会话入口

- 侧边栏「bili 看板」全局入口
- 对话里说「打开 bili 看板」即可内嵌

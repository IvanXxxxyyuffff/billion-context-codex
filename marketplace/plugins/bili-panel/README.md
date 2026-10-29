# bili-panel

billion-context 上下文管理看板（独立 Codex 插件）。

- 数据源：本地 bili 代理（默认 `http://127.0.0.1:8790`，可用环境变量 `BILI_URL` 覆盖）
- 入口：侧边栏全局入口 + 对话内嵌（`bili_panel` 工具）
- 指标：会话 / 请求 / 输入 token / 缓存命中率 / 压缩块 / 节省 token / 花费 / 压缩节省（USD）
- 近期会话：live 状态、请求量、上下文 token、缓存命中率、模型

## 启动 bili 代理

```bash
export PATH="$HOME/.local/bin:$PATH"
bili start --port 8790
```

## 安装到 Codex

在 `~/.codex/config.toml` 里追加：

```toml
[plugins."bili-panel@bili-local"]
enabled = true

[marketplaces.bili-local]
source_type = "local"
source = "/Users/mac/Documents/Codex/2026-10-29/gh-billion-context-co/outputs/bili-panel-plugin"
```

重启 Codex 桌面端后生效。

## 图标

压缩漏斗：4 条逐层收窄的横条（lime → mint → violet → sky），寓意上下文折叠压缩。

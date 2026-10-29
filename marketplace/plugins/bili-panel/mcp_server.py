#!/usr/bin/env python3
"""bili-panel MCP server (stdio). 独立插件：billion-context 上下文管理看板。

只读薄封装：
- bili_panel  : 侧边栏/对话内嵌入口（global + thread entrypoint）
- bili_api    : 只读代理 GET /__bili/*（面板沙箱 CSP 禁直连 127.0.0.1）
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

BILI = os.environ.get("BILI_URL", "http://127.0.0.1:8790").rstrip("/")
NAME = "bili-panel"
HERE = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(HERE, "VERSION"), encoding="utf-8") as _f:
        VERSION = _f.read().strip() or "1.0.0"
except OSError:
    VERSION = "1.0.0"
UI_URI = "ui://bili-panel/panel4"
UI_FILE = os.path.join(HERE, "ui", "panel.html")
UI_MIME = "text/html;profile=mcp-app"

# 本机代理环境下 urllib 默认把 127.0.0.1 交给代理 → 永远超时
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def bili_http(path):
    """GET bili 代理的 __bili 端点（只读）。"""
    req = urllib.request.Request(BILI + path, method="GET")
    try:
        with _OPENER.open(req, timeout=15) as r:
            raw = r.read()
        return json.loads(raw) if raw[:1] in (b"{", b"[") else raw.decode()
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            out = json.loads(raw) if raw[:1] in (b"{", b"[") else {"error": raw.decode()}
        except Exception:
            out = {"error": raw.decode(errors="replace")[:300]}
        if isinstance(out, dict):
            out.setdefault("status", e.code)
        return out
    except urllib.error.URLError as e:
        return {"error": f"bili 代理 {BILI} 连不上（{getattr(e, 'reason', e)}）。"
                         f"先启动：export PATH=$HOME/.local/bin:$PATH && bili start --port 8790 &",
                "status": 0, "offline": True}
    except TimeoutError:
        return {"error": f"bili 代理 {BILI} 15s 没响应", "status": 0}


def _fmt_pct(v):
    try:
        return f"{float(v):.1f}%"
    except (TypeError, ValueError):
        return str(v or "-")


def summarize_overview(d):
    """把 /__bili/overview 的 overview 部分压成 markdown 摘要 + 返回原始 dict。"""
    o = (d or {}).get("overview") or {}
    lines = [
        "## 📊 billion-context 上下文管理看板", "",
        "| 指标 | 数值 |",
        "|---|---|",
        f"| 会话 | {o.get('live', 0)} live / {o.get('sessions', 0):,} total |",
        f"| 总请求数 | {o.get('requests', 0):,} |",
        f"| 输入 token | {o.get('inputTokens', 0):,} |",
        f"| 缓存命中 | {o.get('cachedTokens', 0):,}（{_fmt_pct(o.get('hitPct'))}） |",
        f"| 压缩块 | {o.get('blocks', 0):,} |",
        f"| 节省 token | {o.get('tokensSaved', 0):,} |",
        f"| 实际花费 | ${o.get('costUsdTotal', 0):.2f} |",
        f"| 压缩节省 | ${o.get('savedUsdTotal', 0):.2f} |",
        "",
    ]
    hit = o.get("hitPct") or 0
    lines.append(f"健康度：{'✅ HEALTHY' if hit >= 85 else '⚠️ 低于 85%，查归因'}")
    protos = o.get("byProtocol") or []
    if protos:
        lines += ["", "## 协议分布"]
        for p in protos:
            lines.append(f"- {p.get('protocol', '?')}：{p.get('sessions', 0)} 会话 / "
                         f"{p.get('requests', 0):,} 请求 / 命中 {p.get('hitPct', 0)}%")
    recents = o.get("recent") or []
    if recents:
        lines += ["", "## 近期会话"]
        for s in recents[:8]:
            live = "🟢" if s.get("live") else "⚪"
            title = (s.get("title") or s.get("id", ""))[:40]
            lines.append(f"- {live} {title}｜{s.get('requests', 0):,} 请求｜"
                         f"上下文 {s.get('contextTokens', 0):,} tok｜命中 {s.get('cacheHitPct', '-')}%")
    lines += ["", f"Web UI: {BILI}/__bili/"]
    return "\n".join(lines), o


TOOLS = [
    {"name": "bili_panel", "title": "bili 看板",
     "description": "打开 billion-context 上下文管理看板：会话数 / token 用量 / 缓存命中率 / 压缩块 / 节省量 / 近期会话。数据源是 bili 代理（默认 127.0.0.1:8790）。",
     "inputSchema": {"type": "object", "properties": {}},
     "_meta": {"ui": {"resourceUri": UI_URI, "visibility": ["model", "app"]},
               "openai/ui": {"entrypoints": [{"type": "thread"}, {"type": "global"}]}}},
    {"name": "bili_api", "title": "bili 数据代理",
     "description": "内部工具：只读代理访问 billion-context 代理的 __bili 端点（overview / sessions / status），供内嵌看板取数（沙箱 CSP 禁直连 127.0.0.1）",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "以 /__bili 开头的路径，如 /__bili/overview 或 /__bili/sessions"}},
         "required": ["path"]}},
]


def call(name, args):
    if name == "bili_api":
        path = args.get("path") or "/__bili/overview"
        if not path.startswith("/__bili"):
            return "rejected", {"data": None, "error": "only /__bili paths"}
        try:
            out = bili_http(path)
        except Exception as e:  # noqa: BLE001
            return "error", {"data": None, "error": str(e)}
        return "ok", {"data": out}

    if name == "bili_panel":
        d = bili_http("/__bili/overview")
        if isinstance(d, dict) and d.get("error") and not d.get("overview"):
            return f"bili 代理不可用：{d['error']}", d
        text, o = summarize_overview(d)
        return text, {"bili": o, "bili_url": BILI + "/__bili/"}

    raise RuntimeError(f"未知工具：{name}")


def reply(rid, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": rid, "result": result},
                                ensure_ascii=False) + "\n")
    sys.stdout.flush()


def error(rid, code, msg):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": rid,
                                 "error": {"code": code, "message": msg}}, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _safe_stdio():
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main():
    _safe_stdio()
    log(f"[bili-panel-mcp] start, bili={BILI}")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid, method = msg.get("id"), msg.get("method")
        if method == "initialize":
            icon = ""
            try:
                with open(os.path.join(HERE, "assets", "logo.svg"), "rb") as f:
                    icon = "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()
            except OSError:
                pass
            info = {"name": NAME, "version": VERSION}
            if icon:
                info["icons"] = [{"src": icon, "mimeType": "image/svg+xml", "sizes": ["any"]}]
            reply(rid, {"protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
                        "capabilities": {"tools": {"listChanged": False},
                                         "resources": {"listChanged": False, "subscribe": False}},
                        "serverInfo": info})
        elif method == "notifications/initialized":
            continue
        elif method == "ping":
            reply(rid, {})
        elif method == "resources/list":
            reply(rid, {"resources": [{"uri": UI_URI, "name": "bili 看板",
                                       "description": "billion-context 上下文管理：token/缓存/压缩",
                                       "mimeType": UI_MIME,
                                       "_meta": {"openai/widgetCSP": {
                                           "frame_domains": [BILI],
                                           "connect_domains": [BILI],
                                           "base_uri_domains": [BILI]}}}]})
        elif method == "resources/templates/list":
            reply(rid, {"resourceTemplates": []})
        elif method == "resources/read":
            uri = (msg.get("params") or {}).get("uri", "")
            if uri != UI_URI:
                error(rid, -32602, f"unknown resource: {uri}")
                continue
            try:
                html = open(UI_FILE, encoding="utf-8").read()
            except OSError as e:
                error(rid, -32603, f"cannot read ui: {e}")
                continue
            # 首屏数据内嵌：沙箱 CSP 禁 fetch，SDK 连接也慢 —— 服务端直接把 overview 烤进 HTML
            try:
                snapshot = bili_http("/__bili/overview")
                baked = json.dumps(snapshot, ensure_ascii=False).replace("</", "<\\/")
            except Exception:
                baked = "null"
            html = html.replace("@@OVERVIEW_JSON@@", baked)
            reply(rid, {"contents": [{
                "uri": UI_URI, "mimeType": UI_MIME, "text": html,
                "_meta": {
                    "openai/widgetHeightHint": 820,
                    "openai/widgetMinFrameHeight": 420,
                    "openai/widgetCSP": {
                        "frame_domains": [BILI],
                        "connect_domains": [BILI],
                        "base_uri_domains": [BILI],
                    },
                    "openai/ui": {"preferredDisplayMode": "inline"},
                },
            }]})
        elif method == "tools/list":
            reply(rid, {"tools": TOOLS})
        elif method == "tools/call":
            params = msg.get("params", {})
            try:
                text, struct = call(params.get("name"), params.get("arguments") or {})
                reply(rid, {"content": [{"type": "text", "text": text}],
                            "structuredContent": struct, "isError": False})
            except Exception as e:  # noqa: BLE001
                reply(rid, {"content": [{"type": "text", "text": f"出错：{e}"}], "isError": True})
        elif rid is not None:
            error(rid, -32601, f"method not found: {method}")


if __name__ == "__main__":
    main()

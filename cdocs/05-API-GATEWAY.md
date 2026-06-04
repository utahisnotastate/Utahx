# 第 5 部分：高级 API 网关

**读者：** 后端工程师与 API 负责人  
**代码仓库：** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## 为何需要 Utahx 网关层

Nginx 按 **精确 URL** 缓存。路径相同但请求体不同的两次调用仍可能两次打穿后端。Utahx **语义缓存** 对 **路径 + 请求体** 做指纹，逻辑相同的 API 调用从 RAM 即时返回。

该层位于 **边缘**，在应用 worker 池之前执行。

---

## 组件

| 类 | 文件 | 角色 |
|----|------|------|
| `SemanticMemoryCore` | `utahx_cache.py` | SHA-256 保险库：指纹 → (字节, 过期时间) |
| `SemanticCacheMiddleware` | `utahx_cache.py` | 可缓存请求的 HTTP 中间件 |

---

## 缓存规则

| 规则 | 值 |
|------|-----|
| 方法 | `GET`、`HEAD` |
| 路径 | `/api/*` 或 `Accept: application/json` |
| 跳过 | 内部路由 `/__utahx/*` |
| 仅缓存 | HTTP **200** |
| 默认 TTL | **60** 秒 |

---

## 响应头

| 头 | 含义 |
|----|------|
| `X-Utahx-Cache: HIT` | 内存命中 |
| `X-Utahx-Cache: MISS` | 回源并已记忆 |

可用于压测与 APM 评估缓存效果。

---

## Python 配置

```python
from utahx_auto import UtahxServer

server = UtahxServer(
    directory=".",
    cache_ttl_seconds=300,
    enable_semantic_cache=True,
)
server.start(port=8080)
```

关闭缓存：

```python
UtahxServer(directory=".", enable_semantic_cache=False)
```

---

## 直接使用缓存 API

```python
from utahx_cache import SemanticMemoryCore

cache = SemanticMemoryCore(time_to_live_seconds=120)
cache.memorize("/api/user", b"id=1", b'{"name":"Ada"}')
assert cache.retrieve("/api/user", b"id=1") is not None
```

---

## 完整边缘栈（v1.2）

```
HTTP 请求
    │
    ▼
HumanIntrospectionMiddleware     ← 友好错误
    │
    ▼
FluidTrafficMiddleware           ← 负载下粘度控制
    │
    ▼
SemanticCacheMiddleware          ← API RAM 缓存
    │
    ▼
PrefetchInjectMiddleware         ← HTML 预取（非 JSON API）
    │
    ▼
应用（静态 / 代理 / 自动启动后端）
```

---

## 容量规划

| 因素 | 建议 |
|------|------|
| 内存 | 每条缓存保存完整响应直至 TTL |
| 基数 | 请求体种类越多，命中率越低 |
| 失效 | 当前仅 TTL；发布后可缩短 TTL |
| 多 Pod | 每 Pod 独立缓存；集群级请用 Redis |

---

## 测试

```bash
python -m unittest test_utahx_cache -v
```

---

## 相关章节

- [第 3 部分 — 迁移](03-MIGRATION-GUIDE.md)  
- [第 4 部分 — 企业扩展](04-ENTERPRISE-SCALING.md)

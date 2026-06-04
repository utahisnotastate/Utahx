# 第 3 部分：技术迁移指南

**读者：** DevOps、SRE、后端工程师  
**代码仓库：** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

Utahx 用一条 CLI 替代 Nginx **配置文件**。安装后大多数迁移在 **60 秒内** 完成。

---

## 安装

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
pip install -e .
```

### 要求

- Python **3.11+**
- `requirements.txt` 中的依赖（FastAPI、Uvicorn、httpx、cryptography）
- 可选 ACME：`pip install -e ".[secure]"`

验证：

```bash
python -m unittest discover -v
```

---

## 场景 A：反向代理（Node.js、Python、Go）

### 之前：Nginx

```nginx
server {
    listen 80;
    server_name example.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

另需 `sites-available`、符号链接、`nginx -t`、reload。

### 之后：Utahx

```bash
cd /path/to/your/app
utahx start --proxy 5000 --domain example.com --email ops@example.com
```

| 设置 | 行为 |
|------|------|
| 监听 | 有 `--domain` 时用 **443** + TLS；本地无域名时为 **8080** |
| 上游 | `http://127.0.0.1:5000` |
| 边缘保护 | FluidTrafficMiddleware |
| HTML | 对 HTML 响应注入预取脚本 |

应用需已在目标端口监听（例如 Flask 5000）。

---

## 场景 B：静态站或 SPA（React、Vue、HTML）

### 之前：Nginx

`root`、`try_files $uri /index.html`、手动缓存头。

### 之后：Utahx

```bash
cd ./dist
utahx start --static --domain example.com
```

| 设置 | 行为 |
|------|------|
| 模式 | 强制静态文件服务 |
| SPA | 检测到 SPA 标记时，未知路径回退到 `index.html` |
| 预取 | `/__utahx/prefetch/*` 与客户端脚本 |

---

## 场景 C：零配置（Magic Butler）

```bash
cd /path/to/project
utahx start
```

识别顺序：

1. `package.json` → Node.js  
2. `requirements.txt` 或 `main.py` → Python  
3. `index.html` → 静态  
4. 否则 → 安全静态回退  

---

## 中间件与请求流

```
客户端
  → HumanIntrospectionMiddleware   （友好 404/502/500）
  → FluidTrafficMiddleware         （粘度 / Reynolds）
  → SemanticCacheMiddleware        （API RAM 缓存）
  → PrefetchInjectMiddleware       （HTML 预取注入）
  → 静态 | 反向代理 | 自动后端
```

---

## 语义预取 API

| 端点 | 方法 | 用途 |
|------|------|------|
| `/__utahx/prefetch/manifest?path=/` | GET | 当前页链接图 |
| `/__utahx/prefetch/signal` | POST | 指针遥测 → 排序 URL |
| `/__utahx/prefetch/utahx.js` | GET | 浏览器引导脚本 |

服务端模块：`utahx_prefetch.SemanticPrefetchEngine`

---

## 语义缓存

| 响应头 | 含义 |
|--------|------|
| `X-Utahx-Cache: HIT` | 来自内存 |
| `X-Utahx-Cache: MISS` | 回源并写入缓存 |

默认 TTL：**60** 秒。配置：`UtahxServer(cache_ttl_seconds=120)`。

---

## TLS 与证书

```bash
utahx start --domain example.com --email admin@example.com
```

- 生产 ACME：安装 `utahx[secure]`，确保 80 端口 HTTP-01 可达  
- 开发回退：`.utahx/vault/` 中的 ECDSA 证书  
- 测试 CA：加 `--staging`  

---

## Windows 流程

1. 将项目与 `utahx.cmd` 放在同一文件夹。  
2. 双击（交互式域名提示）。  
3. 构建 exe：`.\scripts\build_utahx_exe.ps1`

---

## 环境变量

| 变量 | 用途 |
|------|------|
| `UTAHX_STATELESS` | 容器中设为 `1` |
| `UTAHX_PORT` | 容器监听端口（Docker 默认 **8080**） |

---

## 命令速查

| 命令 | 场景 |
|------|------|
| `utahx start` | 自动识别项目 |
| `utahx start --static --domain example.com` | SPA / 静态构建目录 |
| `utahx start --proxy 5000 --domain example.com` | 已有应用监听 5000 |
| `utahx start --domain example.com --email ops@example.com` | TLS + ACME 账户 |
| `utahx start --port 9000` | 自定义端口 |

---

## 相关章节

- [第 4 部分 — 企业扩展](04-ENTERPRISE-SCALING.md)  
- [第 5 部分 — API 网关](05-API-GATEWAY.md)  
- [第 6 部分 — 商业化](06-MONETIZATION.md)  
- [文档索引](README.md)

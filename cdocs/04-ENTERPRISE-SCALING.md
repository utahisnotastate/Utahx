# 第 4 部分：企业级扩展（Docker 与 Kubernetes）

**读者：** DevOps 与平台工程师  
**代码仓库：** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## 类比：克隆工厂

单个 Utahx 可应对日常负载。流量爆发时，将 Utahx 封入 **Docker** 容器，由 **Kubernetes** 在 CPU 升高时自动克隆实例，无需手工给每台 VM 复制 Nginx 配置。

---

## 设计原则

| 原则 | 实现 |
|------|------|
| **无状态 Pod** | `UTAHX_STATELESS=1`，不依赖本地磁盘 |
| **水平扩展** | HPA：CPU 70% 时从 3 扩至 100 |
| **精简镜像** | 基于 `python:3.11-slim` |
| **运行时零配置** | 容器内 CLI 启动服务 |

流体指标与语义缓存存于各 Pod 内存。集群级共享缓存请用 Utahx Cloud 或外部 Redis（见第 6 部分）。

---

## Docker

### 构建

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
docker build -t utahisnotastate/utahx:latest .
```

### 运行（单容器）

```bash
mkdir site && echo '<h1>Hello</h1>' > site/index.html
docker run --rm -p 8080:8080 \
  -v "$(pwd)/site:/app/site:ro" \
  -w /app/site \
  utahisnotastate/utahx:latest
```

访问 `http://localhost:8080`。

### Docker Compose

```bash
docker compose up --build
```

在 `docker-compose.yml` 中将站点目录挂载到 `/app/site`。

---

## Kubernetes

清单文件：`deploy/utahx_kubernetes_scale.yaml`

| 资源 | 用途 |
|------|------|
| `Service` (LoadBalancer) | 端口 **80** → Pod **8080** |
| `Deployment` | 默认 **3** 副本 |
| `HorizontalPodAutoscaler` | **3–100** 副本，**70%** CPU |

### 部署

```bash
kubectl apply -f deploy/utahx_kubernetes_scale.yaml
kubectl get pods -l app=utahx
kubectl get hpa utahx-auto-scaler
```

### 生产建议

- 在云负载均衡器终结 TLS，或将 TLS Secret 挂载进 Pod  
- 通过 Volume/ConfigMap 挂载站点，或让 Utahx 代理独立应用 Service  
- 按 SLO 调整 CPU/内存 request 与 limit  
- 使用清单中已定义的存活/就绪探针  

---

## CI/CD

工作流 `.github/workflows/ci.yml` 在每次 push 时运行完整 Python 测试。

推荐发布流水线：

1. 运行测试  
2. `docker build` 并推送 registry  
3. `kubectl set image` 更新 Deployment  

---

## 可观测性

| 信号 | 位置 |
|------|------|
| 流体湍流 | Utahx 日志（`Turbulence detected`） |
| 缓存 | 响应头 `X-Utahx-Cache` |
| TLS | `UtahxSecurity` 日志 |
| 版本 | 启动时 `UtahxRegistry` 日志 |

---

## 故障排查

| 现象 | 检查项 |
|------|--------|
| Pod CrashLoop | 容器端口 8080；站点挂载路径正确 |
| SPA 403/404 | 使用 `utahx start --static`；存在 `index.html` |
| 开发环境 TLS 警告 | vault 自签证书属预期；生产用真实 ACME |
| HPA 不扩容 | Metrics Server；是否设置 CPU requests |

---

## 下一步

- [第 5 部分 — API 网关](05-API-GATEWAY.md)  
- [第 6 部分 — 商业化](06-MONETIZATION.md)

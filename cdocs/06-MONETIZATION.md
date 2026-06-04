# 第 6 部分：商业化蓝图（Utahx Cloud）

**读者：** 创始人、市场、企业销售  
**代码仓库：** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## 战略概览

Utahx 开源消除开发者对 Nginx 的痛苦。**Utahx Cloud Control** 对企业仍愿付费的能力收费：可视化、全球策略、托管扩展与支持。

```
免费 OSS（GitHub）  →  开发者采用  →  Cloud 订阅
```

---

## 产品：Utahx Cloud Control

### 套餐

| 套餐 | 价格 | 包含 |
|------|------|------|
| **Hobbyist** | 免费 | 本地 Utahx、社区支持、基础日志 |
| **Pro** | $99/月（规划） | 仪表盘、邮件告警、30 天指标 |
| **Enterprise** | $499/月 | 威胁拦截 UI、全球流量图、一键 GKE/EKS 部署、Redis 共享缓存、SSO、SLA |

### 痛点 → 付费功能

| 采购方痛点 | Cloud 功能 |
|------------|------------|
| “全球是否正常？” | 全球流量热力图 |
| “立刻关停” | API 密钥中央 kill switch |
| “不想写 YAML 扩容” | 一键应用 `utahx_kubernetes_scale.yaml` |
| “API 为何慢？” | 缓存命中率与粘度时间线 |
| “合规” | 审计导出、RBAC、SSO |

---

## 上市 playbook

### 阶段 1（第 1–2 周）

1. 发布仓库：[github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)  
2. 落地页标题：*「Nginx 已死。零配置、防崩溃的 Web 引擎。」*  
3. CTA：README 中的 `git clone` + `utahx start`  
4. 演示：502 前后对比视频  

### 阶段 2（第 3–8 周）

- 镜像发布到 GHCR  
- DevRel 文章：“60 秒完成迁移”  
- 通过 GitHub Issues 收集反馈  

### 阶段 3（第 3 个月起）

- Cloud 仪表盘内测  
- `UTAHX_CLOUD_API_KEY` 代理（路线图）  
- 面向已用 Kubernetes 的团队做 Enterprise 外拓  

---

## 技术挂钩（路线图）

```bash
export UTAHX_CLOUD_API_KEY=utx_live_xxxxxxxx
utahx start --domain example.com
```

计划中的匿名遥测：

- RPS 与粘度事件  
- 语义缓存命中率  
- TLS 续期状态  
- 托管 K8s 下的 Pod 数量  

---

## 收入模型

| 来源 | 模式 |
|------|------|
| 开源 | MIT，无许可费 |
| Cloud | 按组织月订阅 |
| 托管单元 | 专用 K8s 命名空间用量加价 |
| Enterprise | 年合同 + 支持 + 合规包 |

---

## 竞争定位

| 竞品 | Utahx OSS | Utahx Cloud |
|------|-----------|-------------|
| Nginx + Certbot | 零配置、流体路由 | 仪表盘 + 托管扩展 |
| Cloudflare（部分重叠） | 可自托管 | 边缘 + 本地混合 |
| Traefik | 更易上手 | Enterprise 策略 UI |

---

## 文档

- [简体中文索引](README.md)  
- [English docs](../docs/README.md)  
- [Русская документация](../tdocs/README.md)

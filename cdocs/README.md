# Utahx 文档（简体中文）

Utahx SOTA  Web 引擎官方文档。

**代码仓库：** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## 文档目录

| 部分 | 文档 | 适用读者 |
|------|------|----------|
| 1 | [01-CHILD-PROTOCOL.md](01-CHILD-PROTOCOL.md) | 初学者与非技术人员 |
| 2 | [02-BUSINESS-GUIDE.md](02-BUSINESS-GUIDE.md) | 创始人、产品负责人、运营 |
| 3 | [03-MIGRATION-GUIDE.md](03-MIGRATION-GUIDE.md) | DevOps、SRE、后端工程师 |
| 4 | [04-ENTERPRISE-SCALING.md](04-ENTERPRISE-SCALING.md) | Docker 与 Kubernetes |
| 5 | [05-API-GATEWAY.md](05-API-GATEWAY.md) | API 负责人与后端开发 |
| 6 | [06-MONETIZATION.md](06-MONETIZATION.md) | 商业化与 Utahx Cloud |
| 7 | [07-AEGIS-PROTOCOL.md](07-AEGIS-PROTOCOL.md) | Aegis TCP 加固 |

---

## 建议阅读顺序

1. **第一次建站？** 从第 1 部分开始。  
2. **关心业务与收入？** 阅读第 2 部分，再看第 3 部分。  
3. **要替换 Nginx？** 直接看第 3 部分。  
4. **需要百万级扩展？** 第 4、5 部分。  
5. **围绕 Utahx 做产品公司？** 第 6 部分。

---

## Utahx 替代什么

一条 CLI 即可替代手动的 **Nginx 配置**、**Certbot 流程**、基础 **反向代理** 与僵硬的 **连接数限制**：

- 流体流量平滑（不粗暴断开连接）
- 零配置项目自动识别
- 自主 TLS 证书
- 可读性强的错误页面
- HTML 站点语义预取
- JSON API 语义内存缓存
- 生产级 Docker 与 Kubernetes 清单

---

## 快速链接

- [安装与首次运行](03-MIGRATION-GUIDE.md#安装)
- [Docker 与 Kubernetes](04-ENTERPRISE-SCALING.md)
- [API 缓存网关](05-API-GATEWAY.md)
- [命令速查](03-MIGRATION-GUIDE.md#命令速查)

---

## 其他语言（独立目录）

| 语言 | 索引 |
|------|------|
| English | [../docs/README.md](../docs/README.md) |
| Русский | [../tdocs/README.md](../tdocs/README.md) |
| Eesti | [../edocs/README.md](../edocs/README.md) |
| Suomi | [../fdocs/README.md](../fdocs/README.md) |

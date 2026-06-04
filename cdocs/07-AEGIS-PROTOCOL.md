# 第 7 部分：Aegis 协议（边缘加固）

**读者：** 安全工程师、SRE  
**代码仓库：** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)  
**模块：** `utahx_core_aegis.py`

---

## 为何需要 Aegis

「Hello World」是周末项目。**恶意互联网**需要企业级工程：Slowloris、连接洪水、异常客户端、滚动重启不踢掉活跃用户。

Aegis 是 Utahx 在流体路由之上的 **TCP 加固层**。

---

## 类比：餐厅恶作剧

| 威胁 | 无 Aegis | 有 Aegis |
|------|----------|----------|
| **Slowloris** | 队列 卡死 | 5 秒读超时 |
| **怪异客户端** | 工作线程挂起 | 超时与隔离 |
| **连接洪水** | 内存耗尽 | 信号量上限（默认 1000） |
| **重启** | 全断 | 软关闭：最多 30 秒 drain |

---

## 三重防护

1. **计时器** — 默认 `network_timeout=5.0`  
2. **连接上限** — 默认 `max_connections=1000`  
3. **软关闭** — `SIGINT`/`SIGTERM`，`drain_timeout=30.0`

---

## 使用

```bash
python utahx_core_aegis.py
```

`start_utahx` 默认启用 Aegis；`aegis=False` 可回退旧版路由器。

---

## 日志

默认写入 `utahx_access.log` 并输出到控制台。

---

## 测试

```bash
python -m unittest test_utahx_aegis -v
```

---

## 相关

- [第 3 部分](03-MIGRATION-GUIDE.md)  
- [索引](README.md)

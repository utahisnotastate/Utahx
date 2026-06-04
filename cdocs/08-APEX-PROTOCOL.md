# 第 8 部分：Apex 协议（机器人与零停机部署）

**代码仓库：** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

## 两大场景

| 场景 | Apex 方案 |
|------|-----------|
| 爬虫/机器人洪流 | **图灵收费站** — 密码挑战；浏览器通过，脚本失败 |
| 后端重启 | **冷冻停滞** — 最多 **15 秒** 重试，避免瞬时 502 |

## 使用

```bash
utahx start --proxy 5000 --domain example.com
python utahx_apex_core.py
```

[索引](README.md) · [Aegis](07-AEGIS-PROTOCOL.md)

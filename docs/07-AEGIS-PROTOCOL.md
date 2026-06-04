# Part 7: Aegis Protocol (Edge-Case Hardening)

**Audience:** Security engineers, SRE, veteran systems engineers  
**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)  
**Module:** `utahx_core_aegis.py`

---

## Why Aegis exists

A weekend project serves `Hello World`. Enterprise engineering survives a **malicious internet**: Slowloris, connection floods, half-open clients, and rolling restarts without dropping active users.

Aegis is Utahx’s **TCP hardening layer** on top of the fluid router.

---

## The analogy: restaurant pranksters

| Attack / behavior | Without Aegis | With Aegis |
|-------------------|---------------|------------|
| **Slowloris** (one byte every 10s) | Butler waits forever; queue dies | 5s read timeout; client removed |
| **Weird client** (garbage stream) | Worker hangs | Timeout + fault isolation |
| **Connection flood** | RAM exhaustion | Semaphore cap (default 1000) |
| **Restart** | Lights off; clients cut | Soft close: 30s drain, then exit |

---

## Three defenses (implementation)

### 1. The timer (network timeout)

- Default **5.0 seconds** per read/write/drain and backend connect  
- Neutralizes slow-drip exhaustion  

```python
network_timeout=5.0  # HardenedFluidRouter
```

### 2. The VIP line (connection boundary)

- `asyncio.Semaphore(max_connections)` — default **1000**  
- When full, new TCP connections are dropped immediately (protects RAM)  

```python
max_connections=1000
```

### 3. Soft close (graceful shutdown)

- `SIGINT` / `SIGTERM` trigger `shutdown()`  
- Stop accepting new clients (`is_shutting_down`)  
- Wait up to **30 seconds** for active handlers to finish  
- Then close the asyncio server  

```python
drain_timeout=30.0
```

---

## Usage

### TCP mode (Aegis on by default)

```bash
python utahx_core.py
# or
python -c "import asyncio; from utahx_core import start_utahx; asyncio.run(start_utahx(8080, 5000))"
```

### Direct Aegis entry

```bash
python utahx_core_aegis.py
```

### Disable Aegis (legacy fluid-only router)

```python
import asyncio
from utahx_core import start_utahx

asyncio.run(start_utahx(8080, 5000, aegis=False))
```

### Custom limits

```python
from utahx_core_aegis import start_hardened_server
import asyncio

asyncio.run(
    start_hardened_server(
        8080,
        5000,
        max_connections=500,
        network_timeout=3.0,
        drain_timeout=45.0,
        log_path=".utahx/utahx_access.log",
    ),
)
```

---

## Logging

Aegis configures dual handlers:

- **File:** `utahx_access.log` (default)  
- **Console:** stdout  

Format: `%(asctime)s - [UTAHX] - %(levelname)s - [%(name)s] - %(message)s`

---

## Architecture

```
TCP Client
    │
    ▼
HardenedFluidRouter.handle_client
    ├── shutdown guard
    ├── connection semaphore
    ├── Fluid viscosity (Reynolds / utahx_core.FluidRouter)
    ├── backend connect (wait_for timeout)
    └── _bridge_streams (per-chunk read/drain timeout)
```

HTTP mode (`utahx_auto`) uses middleware-level fluid + cache; use **TCP Aegis** when proxying raw streams or running `utahx_core` standalone.

---

## Environment variables (recommended)

| Variable | Purpose |
|----------|---------|
| `UTAHX_AEGIS` | Set `0` to force legacy router in wrappers (if implemented in CLI) |
| `UTAHX_MAX_CONNECTIONS` | Override connection cap (future CLI hook) |

---

## Tests

```bash
python -m unittest test_utahx_aegis test_utahx -v
```

---

## Related

- [Part 3 — Migration](03-MIGRATION-GUIDE.md)  
- [Part 4 — Enterprise Scaling](04-ENTERPRISE-SCALING.md)  
- [Documentation index](README.md)

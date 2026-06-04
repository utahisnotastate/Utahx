# Часть 7: Протокол Aegis (защита от краевых случаев)

**Аудитория:** Инженеры по безопасности, SRE  
**Репозиторий:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)  
**Модуль:** `utahx_core_aegis.py`

---

## Зачем нужен Aegis

«Hello World» — проект на выходные. **Враждебный интернет** — корпоративная инженерия: Slowloris, лавина соединений, «странные» клиенты, перезапуск без обрыва активных сессий.

Aegis — **усиление TCP** поверх жидкого роутера Utahx.

---

## Аналогия: розыгрыши в ресторане

| Угроза | Без Aegis | С Aegis |
|--------|-----------|---------|
| **Slowloris** | Очередь встаёт | Таймаут чтения 5 с |
| **Странный клиент** | Зависание воркера | Таймаут + изоляция |
| **Лавина TCP** | Исчерпание RAM | Семафор (по умолчанию 1000) |
| **Рестарт** | Обрыв всех | Мягкое закрытие: до 30 с drain |

---

## Три защиты

1. **Таймер** — `network_timeout=5.0` на connect/read/drain  
2. **Лимит соединений** — `max_connections=1000`  
3. **Мягкое закрытие** — `SIGINT`/`SIGTERM`, `drain_timeout=30.0`

---

## Использование

```bash
python utahx_core_aegis.py
```

TCP через `start_utahx` — Aegis **включён по умолчанию**:

```python
import asyncio
from utahx_core import start_utahx
asyncio.run(start_utahx(8080, 5000, aegis=False))  # legacy
```

---

## Логи

Файл `utahx_access.log` + консоль.

---

## Тесты

```bash
python -m unittest test_utahx_aegis -v
```

---

## Связанные разделы

- [Часть 3](03-MIGRATION-GUIDE.md)  
- [Индекс](README.md)

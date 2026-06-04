# Часть 5: Продвинутый API-шлюз

**Аудитория:** Бэкенд-инженеры и владельцы API  
**Репозиторий:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Зачем нужен шлюз Utahx

Nginx кэширует по **точному URL**. Два запроса с одним путём, но разным телом, могут дважды нагрузить бэкенд. **Семантический кэш** Utahx строит отпечаток **путь + тело** и отдаёт повтор из RAM.

Слой работает на **краю** сети — до пула воркеров приложения.

---

## Компоненты

| Класс | Файл | Роль |
|-------|------|------|
| `SemanticMemoryCore` | `utahx_cache.py` | Хранилище: отпечаток → (байты, срок) |
| `SemanticCacheMiddleware` | `utahx_cache.py` | HTTP middleware |

---

## Правила кэширования

| Правило | Значение |
|---------|----------|
| Методы | `GET`, `HEAD` |
| Пути | `/api/*` или `Accept: application/json` |
| Исключения | `/__utahx/*` |
| Сохранение | Только ответы **200** |
| TTL по умолчанию | **60** секунд |

---

## Заголовки ответа

| Заголовок | Значение |
|-----------|----------|
| `X-Utahx-Cache: HIT` | Из памяти |
| `X-Utahx-Cache: MISS` | С бэкенда, затем запомнен |

---

## Настройка в Python

```python
from utahx_auto import UtahxServer

server = UtahxServer(
    directory=".",
    cache_ttl_seconds=300,
    enable_semantic_cache=True,
)
server.start(port=8080)
```

Отключить кэш:

```python
UtahxServer(directory=".", enable_semantic_cache=False)
```

---

## Прямой API кэша

```python
from utahx_cache import SemanticMemoryCore

cache = SemanticMemoryCore(time_to_live_seconds=120)
cache.memorize("/api/user", b"id=1", b'{"name":"Ada"}')
```

---

## Полный стек края (v1.2)

```
HTTP-запрос
    │
    ▼
HumanIntrospectionMiddleware     ← понятные ошибки
    │
    ▼
FluidTrafficMiddleware           ← вязкость под нагрузкой
    │
    ▼
SemanticCacheMiddleware          ← кэш API
    │
    ▼
PrefetchInjectMiddleware         ← предзагрузка HTML
    │
    ▼
Приложение (статика / прокси / автозапуск)
```

---

## Планирование ёмкости

| Фактор | Рекомендация |
|--------|--------------|
| Память | Хранится полный ответ до истечения TTL |
| Уникальность тел | Высокая кардинальность снижает hit rate |
| Инвалидация | Сейчас только TTL; после деплоя уменьшите TTL |
| Несколько подов | Кэш в каждом поде; для кластера — Redis |

---

## Тесты

```bash
python -m unittest test_utahx_cache -v
```

---

## Связанные разделы

- [Часть 3 — Миграция](03-MIGRATION-GUIDE.md)  
- [Часть 4 — Масштабирование](04-ENTERPRISE-SCALING.md)

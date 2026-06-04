# Часть 3: Техническое руководство по миграции

**Аудитория:** DevOps, SRE, бэкенд-инженеры  
**Репозиторий:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

Utahx заменяет файлы конфигурации Nginx одной командой CLI. Большинство миграций занимает **меньше 60 секунд** после установки.

---

## Установка

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
pip install -e .
```

### Требования

- Python **3.11+**
- Зависимости из `requirements.txt`
- Опционально ACME: `pip install -e ".[secure]"`

Проверка:

```bash
python -m unittest discover -v
```

---

## Сценарий A: обратный прокси (Node.js, Python, Go)

### Было: Nginx

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

Плюс `sites-available`, симлинки, `nginx -t`, перезагрузка.

### Стало: Utahx

```bash
cd /path/to/your/app
utahx start --proxy 5000 --domain example.com --email ops@example.com
```

| Параметр | Поведение |
|----------|-----------|
| Порт | **443** с TLS при `--domain`; **8080** локально без домена |
| Бэкенд | `http://127.0.0.1:5000` |
| Защита на краю | FluidTrafficMiddleware |
| HTML | Внедрение скрипта предзагрузки |

Приложение должно уже слушать указанный порт.

---

## Сценарий B: статика или SPA (React, Vue, HTML)

### Было: Nginx

`root`, `try_files $uri /index.html`, ручные заголовки кэша.

### Стало: Utahx

```bash
cd ./dist
utahx start --static --domain example.com
```

| Параметр | Поведение |
|----------|-----------|
| Режим | Принудительная статика |
| SPA | Неизвестные пути → `index.html` при маркерах SPA |
| Предзагрузка | `/__utahx/prefetch/*` и клиентский скрипт |

---

## Сценарий C: нулевая конфигурация

```bash
cd /path/to/project
utahx start
```

Порядок определения:

1. `package.json` → Node.js  
2. `requirements.txt` или `main.py` → Python  
3. `index.html` → статика  
4. Иначе → безопасная статика  

---

## Цепочка middleware

```
Клиент
  → HumanIntrospectionMiddleware   (понятные 404/502/500)
  → FluidTrafficMiddleware         (вязкость / Reynolds)
  → SemanticCacheMiddleware        (кэш API в RAM)
  → PrefetchInjectMiddleware       (предзагрузка HTML)
  → Статика | прокси | автобэкенд
```

---

## API предзагрузки

| Endpoint | Метод | Назначение |
|----------|-------|------------|
| `/__utahx/prefetch/manifest?path=/` | GET | Граф ссылок страницы |
| `/__utahx/prefetch/signal` | POST | Телеметрия указателя → URL |
| `/__utahx/prefetch/utahx.js` | GET | Клиентский скрипт |

Модуль: `utahx_prefetch.SemanticPrefetchEngine`

---

## Семантический кэш

| Заголовок | Значение |
|-----------|----------|
| `X-Utahx-Cache: HIT` | Ответ из RAM |
| `X-Utahx-Cache: MISS` | Запрос к бэкенду, ответ запомнен |

TTL по умолчанию: **60** сек. Настройка: `UtahxServer(cache_ttl_seconds=120)`.

---

## TLS

```bash
utahx start --domain example.com --email admin@example.com
```

- Продакшен ACME: пакет `utahx[secure]`, доступность HTTP-01 на порту 80  
- Разработка: ECDSA в `.utahx/vault/`  
- Тестовый CA: флаг `--staging`  

---

## Windows

1. Скопируйте проект и `utahx.cmd` в одну папку.  
2. Двойной щелчок (интерактивный вопрос о домене).  
3. Сборка `utahx.exe`: `.\scripts\build_utahx_exe.ps1`

---

## Переменные окружения

| Переменная | Назначение |
|------------|------------|
| `UTAHX_STATELESS` | `1` в контейнерах |
| `UTAHX_PORT` | Порт в Docker (по умолчанию **8080**) |

---

## Краткий справочник

| Команда | Случай |
|---------|--------|
| `utahx start` | Автоопределение проекта |
| `utahx start --static --domain example.com` | SPA / статика |
| `utahx start --proxy 5000 --domain example.com` | Приложение на порту 5000 |
| `utahx start --domain example.com --email ops@example.com` | TLS + ACME |
| `utahx start --port 9000` | Свой порт |

---

## Связанные разделы

- [Часть 4 — Масштабирование](04-ENTERPRISE-SCALING.md)  
- [Часть 5 — API-шлюз](05-API-GATEWAY.md)  
- [Часть 6 — Монетизация](06-MONETIZATION.md)  
- [Оглавление](README.md)

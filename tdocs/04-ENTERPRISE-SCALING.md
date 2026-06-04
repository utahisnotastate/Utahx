# Часть 4: Корпоративное масштабирование (Docker и Kubernetes)

**Аудитория:** DevOps и платформенные инженеры  
**Репозиторий:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Аналогия: фабрика клонов

Один экземпляр Utahx справляется с обычной нагрузкой. При вирусном трафике экземпляры упаковывают в **Docker**, а **Kubernetes** клонирует их при росте CPU. Не нужно вручную копировать конфиги Nginx на каждую машину.

---

## Принципы

| Принцип | Реализация |
|---------|------------|
| **Без состояния** | `UTAHX_STATELESS=1`, без обязательного диска |
| **Горизонтальное масштабирование** | HPA: 3–100 подов при 70% CPU |
| **Лёгкий образ** | База `python:3.11-slim` |
| **Без конфига при старте** | CLI внутри контейнера |

Кэш и метрики жидкости — в RAM каждого пода. Общий кэш — Redis или Utahx Cloud (часть 6).

---

## Docker

### Сборка

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
docker build -t utahisnotastate/utahx:latest .
```

### Запуск

```bash
mkdir site && echo '<h1>Привет</h1>' > site/index.html
docker run --rm -p 8080:8080 \
  -v "$(pwd)/site:/app/site:ro" \
  -w /app/site \
  utahisnotastate/utahx:latest
```

Откройте `http://localhost:8080`.

### Docker Compose

```bash
docker compose up --build
```

---

## Kubernetes

Файл: `deploy/utahx_kubernetes_scale.yaml`

| Ресурс | Назначение |
|--------|------------|
| `Service` (LoadBalancer) | Порт **80** → **8080** в поде |
| `Deployment` | **3** реплики по умолчанию |
| `HorizontalPodAutoscaler` | **3–100** реплик при **70%** CPU |

### Развёртывание

```bash
kubectl apply -f deploy/utahx_kubernetes_scale.yaml
kubectl get pods -l app=utahx
kubectl get hpa utahx-auto-scaler
```

### Продакшен

- TLS на балансировщике облака или через Secret в поде  
- Контент сайта через Volume/ConfigMap  
- Настройте лимиты CPU/RAM под ваши SLO  
- Используйте готовые пробы liveness/readiness из манифеста  

---

## CI/CD

Workflow `.github/workflows/ci.yml` гоняет все unit-тесты при push.

Рекомендуемый релиз:

1. Тесты  
2. `docker build` и push в registry  
3. Обновление образа в Deployment  

---

## Наблюдаемость

| Сигнал | Где смотреть |
|--------|--------------|
| Турбулентность трафика | Логи Utahx |
| Кэш | Заголовок `X-Utahx-Cache` |
| TLS | Логгер `UtahxSecurity` |
| Версия | Лог `UtahxRegistry` при старте |

---

## Устранение неполадок

| Симптом | Проверить |
|---------|-----------|
| CrashLoop пода | Порт 8080, корректный mount сайта |
| 404 на SPA | `utahx start --static`, есть `index.html` |
| Предупреждение TLS в dev | Самоподписанный vault; в проде — ACME |
| HPA не масштабирует | Metrics Server, задан requests CPU |

---

## Дальше

- [Часть 5 — API-шлюз](05-API-GATEWAY.md)  
- [Часть 6 — Монетизация](06-MONETIZATION.md)

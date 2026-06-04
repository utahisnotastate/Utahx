# Документация Utahx (русский)

Официальная документация веб-движка Utahx SOTA.

**Репозиторий:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Карта документации

| Часть | Документ | Для кого |
|-------|----------|----------|
| 1 | [01-CHILD-PROTOCOL.md](01-CHILD-PROTOCOL.md) | Новички и нетехнические пользователи |
| 2 | [02-BUSINESS-GUIDE.md](02-BUSINESS-GUIDE.md) | Владельцы бизнеса и продуктов |
| 3 | [03-MIGRATION-GUIDE.md](03-MIGRATION-GUIDE.md) | DevOps, SRE, инженеры |
| 4 | [04-ENTERPRISE-SCALING.md](04-ENTERPRISE-SCALING.md) | Docker и Kubernetes |
| 5 | [05-API-GATEWAY.md](05-API-GATEWAY.md) | Владельцы API и бэкенд |
| 6 | [06-MONETIZATION.md](06-MONETIZATION.md) | Продажи и монетизация Utahx Cloud |
| 7 | [07-AEGIS-PROTOCOL.md](07-AEGIS-PROTOCOL.md) | Aegis, защита TCP |
| 8 | [08-APEX-PROTOCOL.md](08-APEX-PROTOCOL.md) | Apex, боты и zero-downtime |

---

## Рекомендуемый порядок чтения

1. **Впервые запускаете сайт?** — Часть 1.  
2. **Нужен бизнес-эффект?** — Части 2 и 3.  
3. **Заменяете Nginx?** — Часть 3.  
4. **Масштаб на миллионы пользователей?** — Части 4 и 5.  
5. **Строите продукт на базе Utahx?** — Часть 6.

---

## Что заменяет Utahx

Один CLI и набор модулей вместо ручной настройки **Nginx**, **Certbot**, простого **reverse proxy** и жёстких лимитов соединений:

- Сглаживание трафика (без обрыва соединений)
- Автоопределение типа проекта
- Автономный TLS
- Понятные страницы ошибок
- Семантическая предзагрузка HTML
- Семантический кэш API в RAM
- Готовые манифесты Docker и Kubernetes

---

## Быстрые ссылки

- [Установка и первый запуск](03-MIGRATION-GUIDE.md#установка)
- [Docker и Kubernetes](04-ENTERPRISE-SCALING.md)
- [Шлюз API и кэш](05-API-GATEWAY.md)
- [Справочник команд](03-MIGRATION-GUIDE.md#краткий-справочник)

---

## Другие языки (отдельные папки)

На каждой странице **только один язык**.

| Язык | Индекс |
|------|--------|
| English | [../docs/README.md](../docs/README.md) |
| 简体中文 | [../cdocs/README.md](../cdocs/README.md) |
| Eesti | [../edocs/README.md](../edocs/README.md) |
| Suomi | [../fdocs/README.md](../fdocs/README.md) |

# Часть 8: Протокол Apex (боты и деплой без простоя)

**Репозиторий:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

## Две проблемы

| Инцидент | Решение Apex |
|----------|--------------|
| Скрейперы и боты | **Turing Tollbooth** — криптозадача; браузеры проходят, `curl`/скрипты нет |
| Рестарт backend | **Cryogenic Stasis** — до **15 с** повторов вместо мгновенного 502 |

## Использование

```bash
utahx start --proxy 5000 --domain example.com
python utahx_apex_core.py
```

[Индекс](README.md) · [Aegis](07-AEGIS-PROTOCOL.md)

# pdf2md

Пакетная обработка PDF документов через LlamaCloud SDK с веб-интерфейсом.

## 📦 Установка

- **Установить зависимости**:
  ```bash
  pip install fastapi uvicorn llama-cloud>=2.1 nest_asyncio --break-system-packages
  ```
- **Получить API‑ключ** (начинается с `llx-`):
  - Зарегистрируйтесь на https://cloud.llamaindex.ai/
  - Сгенерируйте новый ключ в разделе **API Keys**
  - Сохраните его в файл `~/.openclaw/llama-cloud-api-key.txt` (chmod 600)

## 🚀 Запуск

```bash
uvicorn backend:app --host 0.0.0.0 --port 8080
```
или через скрипт:
```bash
./start.sh
```

Доступно по адресу `http://localhost:8080` (или `http://<ваш_IP>:8080`).

## 🌐 Функционал

- **Drag‑and‑drop** загрузка PDF‑файлов
- **Пакетная обработка** с прогресс‑баром
- **Статус в реальном времени** (ожидание → обработка → готово/ошибка)
- **Скачивание** готового Markdown‑файла
- **Очистка** старых файлов (`cleanup.sh`)

## 📂 Структура проекта

```
pdf2md/
├─ backend.py          # FastAPI‑сервер
├─ index.html          # Веб‑интерфейс
├─ requirements.txt    # Зависимости
├─ install_deps.py     # Установка зависимостей
├─ start.sh           # Запуск сервера
├─ uploads/            # Загруженные PDF (авто‑удаление)
├─ output/            # Готовый Markdown
└─ .gitignore
```

## 🔧 Настройка для продакшена

- Поместить проект на сервер (datayoga24.ru) в путь `/home/user1/.openclaw/workspace/pdf2md`.
- Добавить маршрутизацию в Caddy:
  ```caddy
  datayoga24.ru {
      handle /parce* {
          reverse_proxy localhost:8080
      }
  }
  ```
- Убедиться, что используются порты из диапазона **8000‑9000**.

## 🛡️ Безопасность

- API‑ключ хранится **только в файле** `~/.openclaw/llama-cloud-api-key.txt`.
- Ключ **не попадает** в публичный репозиторий (добавлен в .gitignore).

## 📜 Лицензия

Использует LlamaCloud API от LlamaIndex (бесплатный тариф — 1000 страниц/день).

---
**Версия:** 1.0 **Дата:** 2026‑05‑08
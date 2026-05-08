# LlamaCloud PDF Parser

Пакетная обработка PDF документов через LlamaParse API с веб-интерфейсом.

## 📦 Установка

### 1. Установите зависимости

```bash
cd /home/user1/.openclaw/workspace/projects/parce
python3 install_deps.py
```

Или вручную:

```bash
pip install fastapi uvicorn llama-cloud>=2.1 nest_asyncio --break-system-packages
```

### 2. Получите API ключ

1. Зайдите на [https://cloud.llamaindex.ai/](https://cloud.llamaindex.ai/)
2. Создайте аккаунт (бесплатно)
3. Перейдите в **API Keys** → **Generate New Key**
4. Скопируйте ключ (начинается с `llx-...`)

### 3. Настройте API ключ

```bash
# Создайте файл с API ключом
echo "llx-ВАШ_КЛЮЧ_ЗДЕСЬ" > ~/.openclaw/llama-cloud-api-key.txt

# Или установите как переменную окружения
export LLAMA_CLOUD_API_KEY="llx-ВАШ_КЛЮЧ_ЗДЕСЬ"
```

## 🚀 Запуск

```bash
cd /home/user1/.openclaw/workspace/projects/parce
./start.sh
```

## 🌐 Доступ

После запуска откройте в браузере:

```
http://localhost:8080
```

Для доступа с другого устройства в локальной сети:

```
http://ВАШ_IP:8080
```

## 📖 Использование

1. **Загрузка файлов**
   - Перетащите PDF файлы в зону загрузки
   - Или нажмите "Нажмите для загрузки"
   - Максимум 10 файлов за раз

2. **Обработка**
   - Нажмите "Обработать все файлы"
   - Отслеживайте прогресс в реальном времени
   - Статусы: Ожидание → Обработка → Готово/Ошибка

3. **Скачивание результата**
   - После завершения нажмите "Скачать Markdown"
   - Файл будет сохранён с исходным именем + `.md`

## 🏗️ Архитектура

```
frontend/ (index.html)
    ↓ HTTP requests
backend/ (backend.py)
    ↓ LlamaCloud SDK
llama-cloud API
```

### Структура проекта

```
parce/
├── index.html          # Веб-интерфейс
├── backend.py          # FastAPI сервер
├── start.sh           # Скрипт запуска
├── install_deps.py    # Установка зависимостей
├── requirements.txt   # Зависимости Python
├── uploads/           # Загруженные PDF (авто-удаление)
└── output/            # Обработанные Markdown файлы
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint |
| `/status` | GET | Статус всех задач |
| `/status/{hash}` | GET | Статус конкретной задачи |
| `/upload` | POST | Загрузка и обработка файла |
| `/download/{hash}` | GET | Скачивание результата |
| `/cancel/{hash}` | DELETE | Отмена задачи |

## ⚙️ Настройка для продакшена

### 1. Поместите на сервер (datayoga24.ru)

```bash
# На сервере
cd /home/user1/.openclaw/workspace/projects/parce
./install_deps.py
./start.sh
```

### 2. Настройте Caddy (если нужен внешний доступ)

Добавьте в `/etc/caddy/Caddyfile`:

```caddy
datayoga24.ru {
    handle /parce* {
        reverse_proxy localhost:8080
    }
}
```

Перезагрузите Caddy:

```bash
sudo systemctl reload caddy
```

### 3. Порт

По умолчанию: `8080` (из диапазона 8000-9000 на Cloud.ru)

## 🐛 Устранение проблем

### "LLAMA_CLOUD_API_KEY not set"

```bash
# Проверьте файл с ключом
cat ~/.openclaw/llama-cloud-api-key.txt

# Убедитесь, что переменная доступна
echo $LLAMA_CLOUD_API_KEY
```

### CORS ошибки в браузере

Проверьте, что сервер запущен и порт 8080 открыт:

```bash
curl http://localhost:8080
```

### Ошибки при загрузке больших файлов

Увеличьте лимиты в `backend.py`:

```python
app = FastAPI(
    title="LlamaCloud PDF Parser",
    limits=limits.Limits(max_request_size=100_000_000)  # 100MB
)
```

## 📄 Лицензия

Используется LlamaCloud API от LlamaIndex.
Free tier: 1000 страниц/день.

## 🙏 Благодарности

- [LlamaIndex](https://llamaindex.ai/) за LlamaParse API
- FastAPI за отличный веб-фреймворк

---

**Версия:** 1.0  
**Дата:** 2026-05-08

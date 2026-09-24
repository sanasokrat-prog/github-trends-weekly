# GitHub Trends Weekly

Автоматический сбор трендовых репозиториев GitHub за неделю и отправка в Telegram.

## 📅 Расписание

Каждый **понедельник в 09:00 Екатеринбург (UTC+5)** = 04:00 UTC.

## 🚀 Настройка

### 1. Создайте Telegram-бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Придумайте имя и username для бота
4. Скопируйте полученный токен (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Узнайте свой chat_id

1. Откройте [@userinfobot](https://t.me/userinfobot) в Telegram
2. Отправьте `/start`
3. Бот пришлёт ваш chat_id (число, например `123456789`)

### 3. Добавьте секреты в GitHub

1. Откройте репозиторий: https://github.com/sanasokrat-prog/github-trends-weekly
2. Перейдите в **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret** и добавьте:

| Name | Value |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | Токен из шага 1 |
| `TELEGRAM_CHAT_ID` | Ваш chat_id из шага 2 |

### 4. Запустите вручную (опционально)

1. Перейдите во вкладку **Actions**
2. Выберите workflow **GitHub Trends Weekly**
3. Нажмите **Run workflow** → **Run workflow**

## 📁 Структура

```
.github/workflows/trends.yml  # Workflow для GitHub Actions
scripts/collect_trends.py     # Скрипт сбора и отправки
README.md                     # Эта инструкция
```

## 🔧 Как это работает

1. GitHub Actions запускается по расписанию (cron) или вручную
2. Скрипт скачивает страницу https://github.com/trending?since=weekly
3. Парсит репозитории и распределяет по категориям:
   - 🤖 AI-агенты и автоматизация
   - 🎬 Создание контента
   - 🚀 Вайбкодинг и AI-продукты
4. Форматирует сообщение и отправляет в Telegram
5. При ошибке соединения делает 2 повторные попытки через 10 минут

## 📝 Примечания

- Скрипт использует BeautifulSoup для парсинга HTML
- Форматирование сообщения — Markdown для Telegram
- Повторные попытки: максимум 2, интервал 10 минут

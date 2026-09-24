#!/usr/bin/env python3
"""
Сбор GitHub Trends за неделю и отправка в Telegram.
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GITHUB_TRENDING_URL = "https://github.com/trending?since=weekly"
MAX_RETRIES = 2
RETRY_DELAY = 600

CATEGORIES = {
    "ai_agents": {"keywords": ["agent", "claude", "codex", "automation", "memory", "plugin", "skill", "ai"], "title": "🤖 AI-агенты и автоматизация"},
    "content_creation": {"keywords": ["video", "edit", "graphic", "voice", "telegram", "content", "presentation"], "title": "🎬 Создание контента"},
    "vibecoding": {"keywords": ["website", "app", "bot", "business", "tool", "saas", "no-code", "builder"], "title": "🚀 Вайбкодинг и AI-продукты"}
}

def fetch_trending_page(max_retries=MAX_RETRIES):
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(GITHUB_TRENDING_URL, timeout=30)
            response.raise_for_status()
            return response.text
        except (requests.RequestException, requests.Timeout) as e:
            if attempt < max_retries:
                print(f"Ошибка соединения (попытка {attempt + 1}/{max_retries + 1}): {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise
    return None

def parse_trending_repos(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    repos = []
    repo_cards = soup.select('article.Box-row')
    for card in repo_cards:
        try:
            title_elem = card.select_one('h2 a')
            if not title_elem: continue
            name_with_owner = title_elem.get('href', '').strip('/')
            repo_name = title_elem.get_text(strip=True)
            description_elem = card.select_one('p')
            description = description_elem.get_text(strip=True) if description_elem else ""
            star_elem = card.select_one('a[href*="stargazers"]')
            stars_total = 0
            if star_elem:
                stars_text = star_elem.get_text(strip=True)
                stars_total = int(stars_text.replace(',', '').replace('.', '') or 0)
            stars_fork_elem = card.select_one('.f6.color-fg-muted > a:last-child')
            stars_growth = 0
            stars_growth_text = ""
            if stars_fork_elem:
                growth_text = stars_fork_elem.get_text(strip=True)
                match = re.search(r'([\d,.]+[kK]?)\s*stars?', growth_text)
                if match:
                    stars_growth_text = match.group(1)
                    stars_growth = int(float(stars_growth_text.replace('k','').replace(',','').replace('.','')) * (1000 if 'k' in stars_growth_text.lower() else 1))
            language_elem = card.select_one('span[itemprop="programmingLanguage"]')
            language = language_elem.get_text(strip=True) if language_elem else ""
            repos.append({"name": repo_name, "full_name": name_with_owner, "url": f"https://github.com/{name_with_owner}", "description": description, "stars_total": stars_total, "stars_growth": stars_growth, "stars_growth_text": stars_growth_text, "language": language})
        except Exception as e:
            print(f"Ошибка при парсинге карточки: {e}")
            continue
    return repos

def categorize_repos(repos):
    categorized = {key: [] for key in CATEGORIES.keys()}
    for repo in repos:
        text = f"{repo['name'].lower()} {repo['description'].lower()}"
        for cat_key, cat_data in CATEGORIES.items():
            if any(kw in text for kw in cat_data["keywords"]):
                categorized[cat_key].append(repo)
                break
    for cat_key in categorized:
        categorized[cat_key] = sorted(categorized[cat_key], key=lambda x: x["stars_growth"], reverse=True)[:3]
    return categorized

def format_telegram_message(categorized_repos, all_repos):
    date_str = datetime.now().strftime("%d.%m.%Y")
    message = f"📊 **GitHub Trends за неделю** ({date_str})\n\n"
    message += "Привет! Вот подборка самых горячих проектов с GitHub за последние 7 дней.\n\n"
    message += f"Всего трендовых проектов: {len(all_repos)}\n\n---\n\n"
    for cat_key, cat_data in CATEGORIES.items():
        repos = categorized_repos.get(cat_key, [])
        if not repos: continue
        message += f"{cat_data['title']}\n\n"
        for i, repo in enumerate(repos, 1):
            message += f"{i}. **{repo['name']}**\n"
            message += f"   Прирост звёзд: +{repo['stars_growth_text']} за неделю\n"
            desc = repo['description'][:150] + "..." if len(repo['description']) > 150 else repo['description']
            if desc: message += f"   {desc}\n"
            message += f"   🔗 https://github.com/{repo['full_name']}\n\n"
        message += "---\n\n"
    message += "🎯 **Что попробовать первым:**\n"
    if categorized_repos.get("ai_agents"):
        message += f"• {categorized_repos['ai_agents'][0]['name']} — для автоматизации задач\n"
    if categorized_repos.get("vibecoding"):
        message += f"• {categorized_repos['vibecoding'][0]['name']} — для быстрого создания сайтов\n"
    message += "\n_Следующий выпуск — в понедельник в 09:00 (Екатеринбург)._"
    return message

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не настроены")
        print(message)
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        print(f"✅ Сообщение отправлено в Telegram")
        return True
    except requests.RequestException as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        return False

def main():
    print(f"🚀 Запуск сбора GitHub Trends ({datetime.now().isoformat()})")
    try:
        html = fetch_trending_page()
    except Exception as e:
        print(f"❌ Не удалось получить страницу: {e}")
        return
    all_repos = parse_trending_repos(html)
    print(f"📦 Найдено трендовых проектов: {len(all_repos)}")
    categorized = categorize_repos(all_repos)
    message = format_telegram_message(categorized, all_repos)
    send_telegram_message(message)
    print("✅ Готово!")

if __name__ == "__main__":
    main()

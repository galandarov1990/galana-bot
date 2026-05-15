import os
import json
import requests
import anthropic
from datetime import datetime, timedelta

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_channel_stats():
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    r = requests.get(url).json()
    return r["items"][0]

def get_latest_videos():
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={CHANNEL_ID}&maxResults=5&order=date&type=video&key={YOUTUBE_API_KEY}"
    r = requests.get(url).json()
    video_ids = ",".join([i["id"]["videoId"] for i in r["items"]])
    url2 = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_ids}&key={YOUTUBE_API_KEY}"
    return requests.get(url2).json()["items"]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"})

def analyze_with_claude(stats, videos):
    subs = stats["statistics"]["subscriberCount"]
    views = stats["statistics"]["viewCount"]
    video_count = stats["statistics"]["videoCount"]
    
    videos_info = "\n".join([
        f"- {v['snippet']['title']}: {v['statistics'].get('viewCount', 0)} просмотров, {v['statistics'].get('likeCount', 0)} лайков"
        for v in videos[:5]
    ])
    
    prompt = f"""Ты AI-менеджер YouTube канала @galanalife. Канал о жизни Али, работающего на круизном лайнере, с 3D-анимацией.

Цель: вирусный охват через Shorts, путь к монетизации (1000 подписчиков + 4000 часов).

Текущая статистика:
- Подписчики: {subs} / 1000
- Просмотры всего: {views}
- Видео: {video_count}

Последние видео:
{videos_info}

Прогресс к монетизации:
- Подписчики: {subs}/1000 ({round(int(subs)/10)}%)
- Часов просмотров: примерно {round(int(views)*5/60)} / 4000

Напиши ежедневный отчёт в Telegram. Включи:
1. Прогресс бар к монетизации
2. Анализ последних видео
3. Конкретную рекомендацию что снять сегодня для вирусного охвата через Shorts
4. Мотивирующее слово

Используй эмодзи. Будь конкретным и честным."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def main():
    stats = get_channel_stats()
    videos = get_latest_videos()
    report = analyze_with_claude(stats, videos)
    send_telegram(report)
    print("Отчёт отправлен!")

if __name__ == "__main__":
    main()

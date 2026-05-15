import os
import requests

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

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

def analyze_with_gemini(stats, videos):
    subs = stats["statistics"]["subscriberCount"]
    views = stats["statistics"]["viewCount"]
    video_count = stats["statistics"]["videoCount"]
    hours = round(int(views) * 5 / 60)

    videos_info = "\n".join([
        f"- {v['snippet']['title']}: {v['statistics'].get('viewCount', 0)} просмотров, {v['statistics'].get('likeCount', 0)} лайков"
        for v in videos[:5]
    ])

    prompt = f"""Ты AI-менеджер YouTube канала @galanalife. Канал об Али, работающем на круизном лайнере, с 3D-анимацией.

Цель: вирусный охват через Shorts, путь к монетизации (1000 подписчиков + 4000 часов).

Текущая статистика:
- Подписчики: {subs} / 1000
- Просмотры всего: {views}
- Видео: {video_count}
- Примерно часов просмотров: {hours} / 4000

Последние видео:
{videos_info}

Напиши ежедневный отчёт для Telegram. Включи:
1. Прогресс к монетизации с прогресс-барами
2. Анализ какие видео работают лучше
3. Конкретную рекомендацию что снять сегодня для вирусного охвата через Shorts
4. Мотивирующее слово

Используй эмодзи. Будь честным и конкретным. Пиши на русском."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, json=body).json()
    return r["candidates"][0]["content"]["parts"][0]["text"]

def main():
    stats = get_channel_stats()
    videos = get_latest_videos()
    report = analyze_with_gemini(stats, videos)
    send_telegram(report)
    print("Отчёт отправлен!")

if __name__ == "__main__":
    main()

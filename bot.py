import os
import requests

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_channel_stats():
    url = "https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id=" + CHANNEL_ID + "&key=" + YOUTUBE_API_KEY
    r = requests.get(url).json()
    return r["items"][0]

def get_latest_videos():
    url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=" + CHANNEL_ID + "&maxResults=5&order=date&type=video&key=" + YOUTUBE_API_KEY
    r = requests.get(url).json()
    video_ids = ",".join([i["id"]["videoId"] for i in r["items"]])
    url2 = "https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id=" + video_ids + "&key=" + YOUTUBE_API_KEY
    return requests.get(url2).json()["items"]

def send_telegram(text):
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"})

def analyze_with_gemini(stats, videos):
    subs = stats["statistics"]["subscriberCount"]
    views = stats["statistics"]["viewCount"]
    video_count = stats["statistics"]["videoCount"]
    hours = round(int(views) * 5 / 60)

    videos_info = ""
    for v in videos[:5]:
        title = v["snippet"]["title"]
        vc = v["statistics"].get("viewCount", 0)
        lc = v["statistics"].get("likeCount", 0)
        videos_info += "- " + title + ": " + str(vc) + " просмотров, " + str(lc) + " лайков\n"

    prompt = "Ты AI-менеджер YouTube канала @galanalife. Канал об Али на круизном лайнере с 3D-анимацией.\n"
    prompt += "Цель: вирусный охват через Shorts, монетизация (1000 подп + 4000 часов).\n\n"
    prompt += "Статистика:\n"
    prompt += "- Подписчики: " + str(subs) + " / 1000\n"
    prompt += "- Просмотры: " + str(views) + "\n"
    prompt += "- Видео: " + str(video_count) + "\n"
    prompt += "- Часов просмотров: " + str(hours) + " / 4000\n\n"
    prompt += "Последние видео:\n" + videos_info + "\n"
    prompt += "Напиши ежедневный отчёт для Telegram на русском с эмо

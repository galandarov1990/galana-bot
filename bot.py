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
        videos_info += "- " + title + ": " + str(vc) + " prosm, " + str(lc) + " lajkov\n"

    prompt = "Ty AI-menedzher YouTube kanala @galanalife.\n"
    prompt += "Cel: virusnyj ohvat cherez Shorts, monetizaciya (1000 podp + 4000 chasov).\n\n"
    prompt += "Statistika:\n"
    prompt += "- Podpischiki: " + str(subs) + " / 1000\n"
    prompt += "- Prosmotry: " + str(views) + "\n"
    prompt += "- Video: " + str(video_count) + "\n"
    prompt += "- Chasov: " + str(hours) + " / 4000\n\n"
    prompt += "Poslednie video:\n" + videos_info + "\n"
    prompt += "Napishi ezhednevnyj otchet dlya Telegram na russkom yazyke s emoji. Vklyuchi:\n"
    prompt += "1. Progress k monetizacii s progress-barami\n"
    prompt += "2. Analiz video\n"
    prompt += "3. Rekomendaciyu chto snyat segodnya dlya Shorts\n"
    prompt += "4. Motiviruyuschee slovo\n"

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, json=body).json()

    if "candidates" in r:
        return r["candidates"][0]["content"]["parts"][0]["text"]
    elif "error" in r:
        return "Oshibka Gemini: " + r["error"]["message"]
    else:
        return str(r)

def main():
    stats = get_channel_stats()
    videos = get_latest_videos()
    report = analyze_with_gemini(stats, videos)
    send_telegram(report)
    print("Otchet otpravlen!")

if __name__ == "__main__":
    main()

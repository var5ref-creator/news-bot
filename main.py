import feedparser
import requests
from googletrans import Translator
from bs4 import BeautifulSoup
import time
import re
import json
import os
from collections import deque

BOT_TOKEN = "PUT_YOUR_TOKEN"
CHAT_ID = -1003751243790

translator = Translator()

feeds = [
    ("🚨BBC", "https://rss.app/feeds/wLHPubZUer1yvhGi.xml"),
    ("🚨Sky Sports", "https://rss.app/feeds/Qi5QR9xw2ULgMPIL.xml"),
    ("🚨Fabrizio Romano", "https://rss.app/feeds/g998P6qr1gyZbrgk.xml")
]

SENT_FILE = "sent_posts.json"

# تحميل البيانات
if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        sent_posts = {k: deque(v, maxlen=3) for k, v in data.items()}
else:
    sent_posts = {source[0]: deque(maxlen=3) for source in feeds}


def translate_ar(text):
    try:
        return translator.translate(text, dest="ar").text
    except:
        return text


def send_to_telegram(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except Exception as e:
        print(e)


# تشغيل مرة واحدة فقط (مهم)
for source_name, RSS_URL in feeds:
    feed = feedparser.parse(RSS_URL)

    if source_name not in sent_posts:
        sent_posts[source_name] = deque(maxlen=3)

    new_posts = []
    for post in feed.entries:
        post_id = post.get("id", post.get("link", post.get("title")))
        if post_id in sent_posts[source_name]:
            break
        new_posts.append(post)

    new_posts = new_posts[:3]

    for post in reversed(new_posts):
        title = translate_ar(post.title)
        text = f"{source_name}\n\n{title}"

        send_to_telegram(text)

        sent_posts[source_name].appendleft(post.get("id", post.get("link", post.get("title"))))


# حفظ
with open(SENT_FILE, "w", encoding="utf-8") as f:
    json.dump({k: list(v) for k, v in sent_posts.items()}, f, ensure_ascii=False)

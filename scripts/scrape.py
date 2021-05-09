import os
import sys
from html.parser import HTMLParser

try:
    import requests
except ImportError as e:
    raise ImportError("'requests' is required to run the scraper")


FOLDER = "data/docs/benchmark/small"


def _handle_data(self, data):
    if data:
        self.text += data + "\n"


HTMLParser.handle_data = _handle_data


def get_html_text(html: str):
    parser = HTMLParser()
    parser.text = ""
    parser.feed(html)
    return parser.text.strip()


try:
    os.mkdir(FOLDER)
except Exception:
    print("dir exists")

urls = []

with open("urls.txt") as f:
    for l in f:
        urls.append(l.strip())

for url in urls:
    try:
        print(url)
        title = url.split("/")[-2]
        r = requests.get(url)
        with open(f"{folder}/{title}.txt", "w+") as f:
            f.write(get_html_text(r.text))
    except Exception as e:
        print(e)

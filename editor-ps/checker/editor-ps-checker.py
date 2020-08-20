#!/usr/bin/env python3
import base64
import binascii
import json
import os
import random
import sys
from faker import Faker
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
SERVICENAME = "editor-ps"
PORT = 20005
SLEEP_TIMEOUT = 5
fake = Faker()


def generate_rand(n=16):
    return binascii.b2a_hex(os.urandom(n)).decode()


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        if isinstance(private, str):
            print(private, file=sys.stderr)
        else:
            print(json.dumps(private), file=sys.stderr)
    print('Exit with code {}'.format(code), file=sys.stderr)
    exit(code)


def error_arg(*args):
    close(CHECKER_ERROR, private="Wrong command {}".format(sys.argv[1]))


def init(*args):
    close(OK)


def info(*args):
    close(OK, "vulns: 1:1:2")


def put(*args):
    team_addr, flag_id, flag, vuln = args[:4]

    password = generate_rand()
    r = requests.post("https://{}:{}/auth".format(team_addr, PORT), data={"password": password}, verify=False)
    if r.status_code != 200:
        close(MUMBLE, "Cannot authorize a new user", password)

    time.sleep(1)
    article_id = generate_rand()
    b64_article_id = base64.b64encode(article_id.encode()).decode()
    r = requests.post("https://{}:{}/addArticle".format(team_addr, PORT), verify=False, data={
        "password": password,
        "title": fake.sentence(nb_words=4),
        "content": fake.sentence(nb_words=20),
        "article_id": b64_article_id.rstrip("=")
    })
    if r.text != b64_article_id:
        close(MUMBLE, "Cannot create an article", {"password": password, "article_id": b64_article_id, "response": r.text})

    time.sleep(1)
    # Put flag to one of the tags
    if vuln == "1":
        tags = [flag] + [fake.word() for _ in range(0, random.randint(0, 3))]
        random.shuffle(tags)
        for tag in tags:
            r = requests.post("https://{}:{}/tagArticle".format(team_addr, PORT), verify=False, data={
                "password": password,
                "article_id": b64_article_id.rstrip("="),
                "tag": tag
            })
            if r.text != "OK":
                close(MUMBLE, "Cannot tag an article", {"password": password, "article_id": b64_article_id, "tag": tag, "response": r.text})
        close(OK, "{}:{}:tag".format(password, b64_article_id))
    # Put flag to the content of an article
    elif vuln == "2":
        article_id = generate_rand()
        b64_article_id = base64.b64encode(article_id.encode()).decode()
        r = requests.post("https://{}:{}/addArticle".format(team_addr, PORT), verify=False, data={
            "password": password,
            "title": fake.sentence(nb_words=4),
            "content": fake.sentence(nb_words=4) + " {} ".format(flag) + fake.sentence(nb_words=4),
            "article_id": b64_article_id.rstrip("=")
        })
        if r.text != b64_article_id:
            close(MUMBLE, "Cannot create an article", {"password": password, "article_id": b64_article_id, "response": r.text})
        close(OK, "{}:{}:content".format(password, b64_article_id))
    # Put flag to an article's comment
    else:
        r = requests.post("https://{}:{}/addComment".format(team_addr, PORT), verify=False, data={
            "password": password,
            "comment": flag,
            "article_id": b64_article_id.rstrip("=")
        })
        if r.text != "OK":
            close(MUMBLE, "Cannot create a comment", {"password": password, "article_id": b64_article_id, "response": r.text})
        close(OK, "{}:{}:comment".format(password, b64_article_id))


def get(*args):
    team_addr, lpb, flag, vuln = args[:4]

    password, article_id, _ = lpb.split(":")

    try:
        r = requests.post("https://{}:{}/listArticles".format(team_addr, PORT), verify=False, data={"password": password})
        articles = r.json()
    except Exception as e:
        close(CORRUPT, "Articles list is broken", {"lpb": lpb, "text": r.text, "exception": str(e)})
    if article_id not in articles:
        close(MUMBLE, "Article is not in the list", lpb)

    if vuln == "1":
        try:
            r = requests.post("https://{}:{}/search".format(team_addr, PORT), verify=False, data={"tag": flag})
            result = r.json()
        except Exception as e:
            close(CORRUPT, "Tag not found", {"lpb": lpb, "text": r.text, "exception": str(e)})
        if "tag" in result and result['tag'] == flag and "articles" in result and article_id in result["articles"]:
            close(OK)
        else:
            close(MUMBLE, "Search result is invalid", {"lpb": lpb, "result": result})
    elif vuln == "2":
        try:
            r = requests.post("https://{}:{}/loadArticle".format(team_addr, PORT), verify=False, data={"password": password, "article_id": article_id.rstrip('=')})
            result = r.json()
        except Exception as e:
            close(CORRUPT, "Article not found", {"lpb": lpb, "text": r.text, "exception": str(e)})
        if "article_id" in result and result['article_id'] == article_id and "content" in result and flag in result["content"]:
            close(OK)
        else:
            close(MUMBLE, "Article body is invalid", {"lpb": lpb, "result": result})
    else:
        try:
            r = requests.post("https://{}:{}/getComments".format(team_addr, PORT), verify=False, data={"password": password, "article_id": article_id.rstrip('=')})
            comments = r.json()
        except Exception as e:
            close(CORRUPT, "Comment not found", {"lpb": lpb, "text": r.text, "exception": str(e)})
        if flag in comments:
            close(OK)
        else:
            close(MUMBLE, "Search result is invalid", {"lpb": lpb, "comments": comments})


def check(*args):
    team_addr = args[0]

    # Check auth
    password = generate_rand()
    r = requests.post("https://{}:{}/auth".format(team_addr, PORT), verify=False, data={"password": password})
    if r.status_code != 200:
        close(MUMBLE, "Cannot authorize a new user", password)

    time.sleep(1)

    # Check article addition
    article_id = generate_rand()
    title = fake.sentence(nb_words=4)
    content = fake.sentence(nb_words=20)
    b64_article_id = base64.b64encode(article_id.encode()).decode()
    r = requests.post("https://{}:{}/addArticle".format(team_addr, PORT), verify=False, data={
        "password": password,
        "title": title,
        "content": content,
        "article_id": b64_article_id.rstrip("=")
    })
    if r.text != b64_article_id:
        close(MUMBLE, "Cannot create an article", {"password": password, "article_id": b64_article_id, "response": r.text})

    time.sleep(1)

    # Check article load
    try:
        r = requests.post("https://{}:{}/loadArticle".format(team_addr, PORT), verify=False, data={"password": password, "article_id": b64_article_id.rstrip('=')})
        result = r.json()
    except Exception as e:
        close(CORRUPT, "Article not found", {"text": r.text, "exception": str(e)})

    if "article_id" not in result or result['article_id'] != b64_article_id or "title" not in result or title != result["title"] or "content" not in result or content != result["content"]:
        close(MUMBLE, "Article body is invalid", {"result": result})

    # Check article list
    try:
        r = requests.post("https://{}:{}/listArticles".format(team_addr, PORT), verify=False, data={"password": password})
        articles = r.json()
    except Exception as e:
        close(CORRUPT, "Articles list is broken", {"text": r.text, "exception": str(e)})
    if b64_article_id not in articles:
        close(MUMBLE, "Article is not in the list", b64_article_id)

    # Check all list
    try:
        r = requests.get("https://{}:{}/listAllArticles".format(team_addr, PORT), verify=False)
        articles = [a.split(":", 1)[0] for a in r.json()]
    except Exception as e:
        close(CORRUPT, "All articles list is broken", {"text": r.text, "exception": str(e)})
    if b64_article_id not in articles:
        close(MUMBLE, "Article is not in the full list", b64_article_id)

    # Check tagging
    tag = fake.word()
    r = requests.post("https://{}:{}/tagArticle".format(team_addr, PORT), verify=False, data={
        "password": password,
        "article_id": b64_article_id.rstrip("="),
        "tag": tag
    })
    if r.text != "OK":
        close(MUMBLE, "Cannot tag an article", {"password": password, "article_id": b64_article_id, "tag": tag, "response": r.text})

    time.sleep(1)

    try:
        r = requests.post("https://{}:{}/search".format(team_addr, PORT), verify=False, data={"tag": tag})
        result = r.json()
    except Exception as e:
        close(CORRUPT, "Tag not found", {"tag": tag, "text": r.text, "exception": str(e)})
    if "tag" not in result or result['tag'] != tag or "articles" not in result or b64_article_id not in result["articles"]:
        close(MUMBLE, "Search result is invalid", {"tag": tag, "result": result})

    # Check commenting
    comment = fake.sentence(nb_words=20)
    r = requests.post("https://{}:{}/addComment".format(team_addr, PORT), verify=False, data={
        "password": password,
        "comment": comment,
        "article_id": b64_article_id.rstrip("=")
    })
    if r.text != "OK":
        close(MUMBLE, "Cannot create a comment", {"password": password, "article_id": b64_article_id, "response": r.text})

    time.sleep(1)
    try:
        r = requests.post("https://{}:{}/getComments".format(team_addr, PORT), verify=False, data={"password": password, "article_id": b64_article_id.rstrip('=')})
        comments = r.json()
    except Exception as e:
        close(CORRUPT, "Comment not found", {"text": r.text, "exception": str(e)})
    if comment not in comments:
        close(MUMBLE, "Search result is invalid", {"comments": comments})

    content2 = fake.sentence(nb_words=15)
    try:
        r = requests.post("https://{}:{}/saveArticle".format(team_addr, PORT), verify=False, data={"password": password, "article_id": b64_article_id.rstrip('='), "content": content2})
        if r.text != "OK":
            close(MUMBLE, "Cannot save article", {"article_id": b64_article_id})
    except Exception as e:
        close(CORRUPT, "Articles save is broken", {"text": r.text, "exception": str(e)})

    time.sleep(1)
    try:
        r = requests.post("https://{}:{}/loadArticle".format(team_addr, PORT), verify=False, data={"password": password, "article_id": b64_article_id.rstrip('=')})
        result = r.json()
    except Exception as e:
        close(CORRUPT, "Article not found", {"text": r.text, "exception": str(e)})
    if "article_id" not in result or result['article_id'] != b64_article_id or "title" not in result or title != result["title"] or "content" not in result or content2 != result["content"]:
        close(MUMBLE, "Article body is invalid", {"new_content": content2, "result": result})

    close(OK)


COMMANDS = {
    'put': put,
    'check': check,
    'get': get,
    'info': info,
    'init': init
}


if __name__ == '__main__':
    try:
        COMMANDS.get(sys.argv[1], error_arg)(*sys.argv[2:])
    except Exception as ex:
        close(CHECKER_ERROR, private="INTERNAL ERROR: {}".format(ex))

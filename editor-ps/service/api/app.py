import base64
import binascii
import hashlib
import json
import os
import os.path
import re
import time
import redis
import consul
from faker import Faker
from flask import Flask, request, abort, jsonify
import OpenSSL
import werkzeug.serving
import ssl

app = Flask(__name__)
c = consul.Consul(host=os.environ.get("CONSUL_HOST", "consul"), port=os.environ.get("CONSUL_PORT", 8500))
r = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), port=os.environ.get("REDIS_PORT", 6379), db=0)
fake = Faker()
app.secret_key = b'663f4709772b2c029a7dd7015ab1fcca'


def random_string(n=16):
    return binascii.b2a_hex(os.urandom(n)).decode()


def auth(password):
    password_md5 = hashlib.md5(password.encode()).hexdigest()
    _, data = c.kv.get(f'users/{password_md5}')
    if data is None:
        userdata = {
            "password": password_md5,
            "articles": []
        }
        c.kv.put(f'users/{password_md5}', json.dumps(userdata))
        return userdata
    else:
        userdata = json.loads(data['Value'].decode())
        if userdata["password"] == password_md5:
            return userdata
        else:
            abort(403, description="Invalid password")


def check_article_id(article_id):
    if not re.match('[a-zA-Z0-9/+]+', article_id):
        abort(400, description=f"Invalid article ID format")
    return article_id + "=" * (4 - len(article_id) % 4)


def update_articles_index(article_id):
    # r.sadd('articles', article_id)
    r.zadd('articles', {article_id: int(time.time())})

@app.route("/", methods=["GET"])
def index():
    return "OK"


@app.route("/auth", methods=["POST"])
def auth_view():
    if 'password' not in request.form:
        abort(400, description=f"Please, provide auth data")
    auth(request.form['password'])
    return "OK"


@app.route("/addArticle", methods=["POST"])
def add_article():
    if 'password' not in request.form:
        abort(400, description=f"Please, provide auth data")
    if 'title' not in request.form or 'content' not in request.form or 'article_id' not in request.form:
        abort(400, description=f"Please, fill title, content and article_id")

    userdata = auth(request.form['password'])
    title = request.form['title']
    content = request.form['content']
    article_id = check_article_id(request.form['article_id'])

    _, data = c.kv.get(f'articles/{article_id}')
    if data is not None:
        abort(400, description=f"Article with id={article_id} already exists")

    result = c.kv.put(f'articles/{article_id}', json.dumps({
        "article_id": article_id,
        "author": userdata["password"],
        "title": title,
        "content": content,
        "tags": []
    }))
    if not result:
        abort(500, description=f"Cannot save article with id={article_id}")

    if article_id not in userdata["articles"]:
        userdata["articles"].append(article_id)
    result = c.kv.put(f'users/{userdata["password"]}', json.dumps(userdata))
    if not result:
        abort(500, description=f"Cannot link article with id={article_id} and current user")

    update_articles_index(f"{article_id}:{title}")

    return article_id


@app.route("/listArticles", methods=["POST"])
def list_articles():
    if 'password' not in request.form:
        abort(400, description=f"Please, provide auth data")
    userdata = auth(request.form['password'])
    return jsonify(userdata["articles"])


@app.route("/loadArticle", methods=["POST"])
def load_article():
    if 'password' not in request.form or 'article_id' not in request.form:
        abort(400, description=f"Please, provide auth data and article_id param")

    userdata = auth(request.form['password'])
    article_id = check_article_id(request.form["article_id"])
    if article_id not in userdata["articles"]:
        abort(403, description=f"The article with id={article_id} doesn't belong you")

    _, data = c.kv.get(f'articles/{article_id}')
    if data is None:
        abort(404, description=f"Article with id={article_id} doesn't exist")

    return data['Value']


@app.route("/saveArticle", methods=["POST"])
def save_article():
    if 'password' not in request.form or 'article_id' not in request.form or 'content' not in request.form:
        abort(400, description=f"Please, provide auth data and article_id, content param")

    userdata = auth(request.form['password'])
    article_id = check_article_id(request.form["article_id"])
    content = request.form["content"]

    if article_id not in userdata["articles"]:
        abort(403, description=f"The article with id={article_id} doesn't belong you")

    _, data = c.kv.get(f'articles/{article_id}')
    if data is None:
        abort(404, description=f"Article with id={article_id} doesn't exist")

    article_data = json.loads(data["Value"])
    article_data["content"] = content
    c.kv.put(f'articles/{article_id}', json.dumps(article_data))

    return "OK"


@app.route("/listAllArticles", methods=["GET"])
def list_all_articles():
    # return jsonify([k.decode() for k in r.smembers("articles")])
    return jsonify([k.decode() for k in r.zrange("articles", -100, -1)])


@app.route("/tagArticle", methods=["POST"])
def tag_article():
    if 'password' not in request.form or 'article_id' not in request.form or 'tag' not in request.form:
        abort(400, description=f"Please, provide auth data and article_id, tag params")

    userdata = auth(request.form['password'])
    tag = request.form['tag']
    article_id = check_article_id(request.form['article_id'])

    if article_id not in userdata["articles"]:
        abort(403, description=f"The article with id={article_id} doesn't belong you")

    _, data = c.kv.get(f'tags/{tag}')
    if data is None:
        c.kv.put(f'tags/{tag}', json.dumps({"tag": tag, "articles": [article_id]}))
        _, data = c.kv.get(f'tags/{tag}')

    tag_info = json.loads(data['Value'])
    if tag != tag_info["tag"]:
        abort(500, description="Malformed tag data")

    if article_id not in tag_info["articles"]:
        tag_info["articles"].append(article_id)

    c.kv.put(f'tags/{tag}', json.dumps(tag_info))

    _, data = c.kv.get(f'articles/{article_id}')
    if data is None:
        abort(404, description=f"Article with id={article_id} doesn't exist")

    article_data = json.loads(data['Value'])
    if tag not in article_data['tags']:
        article_data['tags'].append(tag)
    c.kv.put(f'articles/{article_id}', json.dumps(article_data))

    return "OK"


@app.route("/search", methods=["POST"])
def search():
    if "tag" not in request.form:
        abort(400, description=f"Please, provide tag keyword for search")
    tag = request.form['tag']
    _, data = c.kv.get(f'tags/{tag}')
    if data is None:
        abort(404, description=f"Tag record with id={tag} doesn't exist")
    return data['Value']


@app.route("/addComment", methods=["POST"])
def add_comment():
    if 'password' not in request.form or 'article_id' not in request.form or 'comment' not in request.form:
        abort(400, description=f"Please, provide auth data and article_id, comment params")

    userdata = auth(request.form['password'])
    article_id = check_article_id(request.form['article_id'])
    comment = request.form['comment']

    if article_id not in userdata["articles"]:
        abort(403, description=f"The article with id={article_id} doesn't belong you")

    article_index = base64.b64decode(article_id)
    r.sadd(f"comments_{article_index}", comment)
    return "OK"


@app.route("/getComments", methods=["POST"])
def get_comments():
    if 'password' not in request.form or 'article_id' not in request.form:
        abort(400, description=f"Please, provide auth data and article_id param")

    userdata = auth(request.form['password'])
    article_id = check_article_id(request.form['article_id'])

    if article_id not in userdata["articles"]:
        abort(403, description=f"The article with id={article_id} doesn't belong you")

    article_index = base64.b64decode(article_id)
    return jsonify([k.decode() for k in r.smembers(f"comments_{article_index}")])


if __name__ == "__main__":
    app.run(host=os.environ.get("API_HOST", "0.0.0.0"), port=os.environ.get("API_PORT", 5000), threaded=True, debug=False, ssl_context=("api.crt", "api.key"))

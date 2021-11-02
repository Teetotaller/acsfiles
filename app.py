"""
Задание
Создать веб-приложение используя flask.
Суть приложения - доступ к скачиванию файлов для авторизированного пользователя.

Ожидаемые фичи:
- login. Нужно использовать переменные окружения для доуступа к учетным дынным пользователя(ей)
- logout
- используется templates и подгружается статика (css)
- выводится список файлов, которые можно скачать
- путь к папке берётся из переменной окружения
- Список файлов не виден не авторизованным пользователям
- Авторизованный пользователь может загрузить в папку свой файл используя веб-приложение
- требуемые для работы приложения названия пакетов с их версиями лежат в файле requirements.txt
Обязательно проверить свой программный код с помощью flake8 или black и отформатировать его по соответствующим правилам.
"""

import os
from flask import Flask, request, Response, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask_autoindex import AutoIndex
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

UPLOAD_FOLDER = os.getenv("DIR", "\tmp")
USER = os.getenv("USER", "Superuser")
TOKEN = os.getenv("TOKEN", "secretsecret")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "537gdf8ae677")

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)


# user model
class User(UserMixin):
    def __init__(self, username):
        self.name = username

    def __repr__(self):
        return "%s" % (self.name)

    def get_id(self):
        return self.name


files_index = AutoIndex(app, os.path.abspath(UPLOAD_FOLDER), add_url_rules=False)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
tokens = {TOKEN: USER}


def verify_token(token):
    if token in tokens:
        return tokens[token]


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        token = request.form.get("nm")
        if verify_token(token) != None:
            user = User(verify_token(token))
            login_user(user)
            return redirect(url_for("autoindex"))
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")


@app.route("/files", methods=["POST", "GET"])
@app.route("/files/<path:path>", methods=["POST", "GET"])
@login_required
def autoindex(path="."):
    if request.method == "GET":
        return files_index.render_autoindex(
            path, template_context=dict(SITENAME="Access files")
        )
    else:
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("autoindex"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.errorhandler(401)
def page_not_found(e):
    return Response("<p>Token failed</p>")


@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__ == "__main__":
    app.run()

from flask import Flask, flash, render_template, redirect, request, make_response, Response, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.news import NewsForm
from forms.sleep import SleepForm
from forms.user import RegisterForm, LoginForm
from data.news import News
from data.sleep import Sleep
from data.like import Like
from data.users import User
from data import db_session
import sqlite3
import os
from apscheduler.schedulers.background import BackgroundScheduler

import atexit


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def convert_to_binary_data(filename):
    # Преобразование данных в двоичный формат
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


def write_to_file(data, filename):
    # Преобразование двоичных данных в нужный формат
    with open(filename, 'wb') as file:
        file.write(data)
    print("Данный из blob сохранены в: ", filename, "\n")


def silence():
    print('Alive')
    # return render_template("in_bed.html")


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=silence, trigger="interval", seconds=10)
# scheduler.start()
# atexit.register(lambda: scheduler.shutdown())  # Завершение работы sheduler


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News)
    return render_template("index.html", news=news)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect("/")


# возможно должно добавляться аудио, а не название
@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_music():
    form = NewsForm()
    sp_genre = ['классика', 'рок', 'кантри', 'фонк']
    if form.validate_on_submit():
        a = request.form['file']
        print(a)
        if a:
            con = sqlite3.connect("db/blogs.db")
            cur = con.cursor()
            result = cur.execute(f"""SELECT title FROM news""").fetchall()
            con.close()
            res = [i[0] for i in result]
            if a not in res:  # для добавления уникальных песен
                db_sess = db_session.create_session()
                news = News()
                news.title = a
                # a = os.path.abspath(a)
                # news.file = convert_to_binary_data(a)

                genre = request.form.get("genre")
                print(genre)
                news.genre = genre
                news.content = form.content.data
                current_user.news.append(news)
                db_sess.merge(current_user)
                db_sess.commit()
                return redirect('/')
            else:
                return render_template('news.html', title='Добавление песни', form=form,
                                       message="Уже такая есть")
        else:
            return render_template('news.html', title='Добавление песни', form=form,
                                   message="Загрузите песню")
    return render_template('news.html', title='Добавление песни', form=form, sp_genre=sp_genre)


@app.route('/sleep', methods=['GET', 'POST'])
@login_required
def sleep():
    form = SleepForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        con = sqlite3.connect("db/blogs.db")
        cur = con.cursor()
        g.user = current_user.get_id()
        print(g.user)
        t = str(form.switch_on.data)
        db_sess.add(Sleep(switch_on=t, user_id=g.user))
        cur.execute(f"""INSERT INTO sleep (switch_on, user_id) VALUES (?, ?)""", (t, g.user))
        con.close()

        db_sess.commit()
        return redirect('/')
    return render_template('sleep.html', title='Таймер сна', form=form)


# нельзя удалить лайкнутые песни
@app.route('/favorite', methods=['GET', 'POST'])
@login_required
def favorite():
    db_sess = db_session.create_session()
    like = db_sess.query(Like).filter(Like.user == current_user)
    return render_template('favorite.html', title='Любимое', like=like)


@app.route('/music_delete/<int:id>/<int:name>', methods=['GET', 'POST'])
@login_required
def music_delete(id, name):
    db_sess = db_session.create_session()
    lst = {1: News, 2: Like, '1': '', '2': 'favorite'}
    db_sess.delete(db_sess.query(lst[name]).filter(lst[name].id == id).first())
    db_sess.commit()
    return redirect(f'/{lst[str(name)]}')


@app.route('/music_like/<int:id>', methods=['GET', 'POST'])
@login_required
def music_like(id):
    db_sess = db_session.create_session()

    con = sqlite3.connect("db/blogs.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT title FROM news WHERE id={id}""").fetchone()[0]
    g.user = current_user.get_id()
    result1 = cur.execute(f"""SELECT like FROM like WHERE user_id={g.user}""").fetchall()
    res1 = [i[0] for i in result1]
    print(res1)
    if result not in res1:  # для добавления только уникальных песен
        print(g.user)
        db_sess.add(Like(like=result, user_id=g.user))
        cur.execute(f"""INSERT INTO like (like, user_id) VALUES (?, ?)""", (result, g.user))
    con.close()

    db_sess.commit()
    return redirect('/')


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()


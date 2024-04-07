from flask import Flask, flash, render_template, redirect, request, abort, make_response, Response, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.news import NewsForm
from forms.sleep import SleepForm
from forms.user import RegisterForm, LoginForm
from data.news import News
from data.sleep import Sleep
from data.like import Like
from data.users import User
from data import db_session
from datetime import datetime
import schedule
import sqlite3
import os
from apscheduler.schedulers.background import BackgroundScheduler
import time

import atexit


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# def silence():
#     print(90000)
#     return redirect('/')
#     # return render_template("in_bed.html")
#     # pass


# schedule.every().day.at("20:52").do(silence)
# @app.route("/silence")
def silence():
    print('Alive')
    # return render_template("in_bed.html")
    # window.location.reload()
    return render_template("in_bed.html")


scheduler = BackgroundScheduler()
scheduler.add_job(func=silence, trigger="interval", seconds=10)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route("/")
def index():
    db_sess = db_session.create_session()
    # if current_user.is_authenticated:
    #    news = db_sess.query(News).filter((News.user == current_user) | (News.is_private != True))
    # else:

    # тут достаем время из базы данных
    # надо обновлять страницу, проверяя сколько время
    con = sqlite3.connect("db/blogs.db")
    cur = con.cursor()
    result = cur.execute("""SELECT switch_on FROM sleep WHERE user_id""").fetchone()
    # print(result[0])
    con.close()
    news = db_sess.query(News).filter(News.is_private != True)
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
            email=form.email.data,
            about=form.about.data
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


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_music():
    form = NewsForm()
    if form.validate_on_submit():
        a = request.form['file']
        print(a)
        if a:
            db_sess = db_session.create_session()
            news = News()
            news.title = a
            news.content = form.content.data
            news.is_private = form.is_private.data
            current_user.news.append(news)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        else:
            return render_template('news.html', title='Добавление песни', form=form,
                                   message="Загрузите песню")
    return render_template('news.html', title='Добавление песни', form=form)


@app.route('/sleep', methods=['GET', 'POST'])
@login_required
def sleep():  # занести в бд
    form = SleepForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        sleep = Sleep()
        sleep.switch_on = form.switch_on.data
        print(form.switch_on.data)
        current_user.sleep.append(sleep)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('sleep.html', title='Таймер сна', form=form)


@app.route('/favorite', methods=['GET', 'POST'])
@login_required
def favorite():
    pass


@app.route('/music_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def music_delete(id):  # пользователь может удолять не только свои добавленные песни
    db_sess = db_session.create_session()
    db_sess.delete(db_sess.query(News).first())
    db_sess.commit()
    return redirect('/')


# пока не работает
@app.route('/music_like/<int:id>', methods=['GET', 'POST'])
@login_required
def music_like(id):
    db_sess = db_session.create_session()
    like = Like()

    con = sqlite3.connect("db/blogs.db")
    cur = con.cursor()
    result = cur.execute(f"""SELECT title FROM news WHERE id={id}""").fetchone()[0]
    # print(Like(result[0], current_user))
    print(current_user, result)
    # db_sess.add(Like(like=result[0], user_id=current_user.split()[1]))
    # cur.execute(f"""INSERT INTO like VALUES ({result[0]}, {current_user})""")
    con.close()

    data = Like()
    data.like = result

    # current_user.like.append(like)
    # db_sess.merge(current_user)
    db_sess.commit()
    return redirect('/')


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
# while True:
#     schedule.run_pending()


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


def silence():
    print('Alive')
    # return render_template("in_bed.html")


def sort_songs(name):
    return dict(sorted(name.items(), key=lambda x: x[1], reverse=True))


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=silence, trigger="interval", seconds=10)
# scheduler.start()
# atexit.register(lambda: scheduler.shutdown())  # Завершение работы sheduler


@app.route("/")
def index():
    con = sqlite3.connect("db/blogs.db")
    cur = con.cursor()
    g.user = current_user.get_id()

    if g.user:
        res_top_genres = cur.execute(f"""SELECT genre FROM like WHERE user_id={g.user}""").fetchall()
        top_genre = {}
        genre_rec = []
        # возможно надо занести в функцию
        for i in res_top_genres:
            val = i[0]
            if val in top_genre.keys():
                top_genre[val] = top_genre[val] + 1
            else:
                top_genre[val] = 1
        top_genre = sort_songs(top_genre)
        print(top_genre)  # самые любимые жанры отдельного пользователя

        for i in top_genre.keys():
            uiop = cur.execute(f"""SELECT * FROM news WHERE user_id!={g.user} AND genre='{i}'""").fetchall()
            if uiop:
                res = [i[1] for i in uiop]
                genre_rec += uiop

        # подборка индивидуальных рекомендаций на основе любимых жанров
        con.close()
    else:
        genre_rec = cur.execute(f"""SELECT * FROM news""").fetchall()
    print(genre_rec)

    return render_template("index.html", news=genre_rec)


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
        return redirect('/login')
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
    sp_genre = ['классика', 'рок', 'кантри', 'фонк']
    if form.validate_on_submit():
        a = request.form['file']
        genre = request.form.get("genre")
        print(a)
        if a:
            if genre:
                if form.content.data:
                    con = sqlite3.connect("db/blogs.db")
                    cur = con.cursor()
                    result = cur.execute(f"""SELECT title FROM news""").fetchall()
                    con.close()
                    res = [i[0] for i in result]
                    if a not in res:  # для добавления уникальных песен
                        db_sess = db_session.create_session()
                        news = News()
                        news.title = a

                        print(genre)
                        news.genre = genre
                        news.content = form.content.data
                        current_user.news.append(news)
                        db_sess.merge(current_user)
                        db_sess.commit()
                        return redirect('/mine')
                    else:
                        return render_template('news.html', title='Добавление песни', form=form,
                                               message="Уже такая есть")
                else:
                    return render_template('news.html', title='Добавление песни', form=form,
                                           message="Укажите исполнителя песни")
            else:
                return render_template('news.html', title='Добавление песни', form=form,
                                       message="Укажите жанр песни")
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


@app.route('/favorite', methods=['GET', 'POST'])
@login_required
def favorite():
    db_sess = db_session.create_session()
    like = db_sess.query(Like).filter(Like.user == current_user)
    return render_template('favorite.html', title='Любимое', like=like)


@app.route('/mine', methods=['GET', 'POST'])
@login_required
def mine():
    con = sqlite3.connect("db/blogs.db")
    cur = con.cursor()
    g.user = current_user.get_id()

    my_songs = []
    res_novelty_my = cur.execute(f"""SELECT * FROM news WHERE user_id={g.user}""").fetchall()
    for i in res_novelty_my:
        my_songs.append(i[1])
    print(my_songs)  # песни, что загрузил данный пользователь

    con.close()
    return render_template('shablon.html', spisok=my_songs, name='Мои песни')


@app.route('/novetly', methods=['GET', 'POST'])
@login_required
def novetly():
    con = sqlite3.connect("db/blogs.db")
    cur = con.cursor()
    g.user = current_user.get_id()

    res_novelty_other = cur.execute(f"""SELECT * FROM news WHERE user_id!={g.user}""").fetchall()
    novelty_other = {}
    for i in res_novelty_other:
        novelty_other[i[1]] = i[5]
    novelty_other = sort_songs(novelty_other)
    print(novelty_other)

    con.close()
    return render_template('shablon.html', spisok=novelty_other, name='Новинки')


@app.route('/top', methods=['GET', 'POST'])
@login_required
def top():
    con = sqlite3.connect("db/blogs.db")
    cur = con.cursor()
    g.user = current_user.get_id()

    res_top_songs = cur.execute("""SELECT like FROM like""").fetchall()
    top_songs = {}
    for i in res_top_songs:
        val = i[0]
        if val in top_songs.keys():
            top_songs[val] = top_songs[val] + 1
        else:
            top_songs[val] = 1
    top_songs = sort_songs(top_songs)
    print(top_songs)  # здесь хранятся самые популярные песни

    con.close()
    return render_template('shablon.html',
                           spisok=top_songs.keys(), name='Топ песен', kol=[i for i in range(len(top_songs))])


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
    res_title = cur.execute(f"""SELECT title FROM news WHERE id={id}""").fetchone()[0]
    res_genre = cur.execute(f"""SELECT genre FROM news WHERE id={id}""").fetchone()[0]
    g.user = current_user.get_id()
    res_like = cur.execute(f"""SELECT like FROM like WHERE user_id={g.user}""").fetchall()
    res_lik = [i[0] for i in res_like]
    print(res_lik, res_genre)
    if res_title not in res_lik:  # для добавления только уникальных песен
        print(g.user)
        db_sess.add(Like(like=res_title, genre=res_genre, user_id=g.user))
        cur.execute(f"""INSERT INTO like (like, genre, user_id) VALUES (?, ?, ?)""", (res_title, res_genre, g.user))
    con.close()

    db_sess.commit()
    return redirect('/')


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()


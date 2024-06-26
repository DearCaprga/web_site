from flask import Flask, render_template, redirect, request, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.news import NewsForm
from forms.sleep import SleepForm
from forms.user import RegisterForm, LoginForm
from data.news import News
# from data.sleep import Sleep
from data.like import Like
from data.users import User
from data import db_session
import sqlite3


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def sort_songs(name):
    return dict(sorted(name.items(), key=lambda x: x[1], reverse=True))


@app.route("/")
def index():
    con = sqlite3.connect("db/blogs.db")
    cur = con.cursor()
    g.user = current_user.get_id()
    res_top_genres = []
    if g.user:
        res_top_genres = cur.execute(f"""SELECT genre FROM like WHERE user_id={g.user}""").fetchall()

    if g.user and res_top_genres:
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
        print(top_genre, 'Жанр')  # самые любимые жанры отдельного пользователя

        for i in top_genre.keys():
            uiop = cur.execute(f"""SELECT * FROM news WHERE user_id!={g.user} AND genre='{i}'""").fetchall()
            if uiop:
                genre_rec += uiop
        print(genre_rec, "реки")
        qwert = cur.execute(f"""SELECT * FROM news""").fetchall()
        for i in qwert:
            if i[2] not in top_genre.keys():
                genre_rec.append(i)
        print(genre_rec)
    else:
        genre_rec = cur.execute(f"""SELECT * FROM news""").fetchall()
    print(genre_rec)
    con.close()

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


# @app.route('/sleep', methods=['GET', 'POST'])
# @login_required
# def sleep():
#     form = SleepForm()
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#
#         con = sqlite3.connect("db/blogs.db")
#         cur = con.cursor()
#         g.user = current_user.get_id()
#         print(g.user)
#         t = str(form.switch_on.data)
#         db_sess.add(Sleep(switch_on=t, user_id=g.user))
#         cur.execute(f"""INSERT INTO sleep (switch_on, user_id) VALUES (?, ?)""", (t, g.user))
#         con.close()
#
#         db_sess.commit()
#         return redirect('/')
#     return render_template('sleep.html', title='Таймер сна', form=form)


@app.route('/favorite', methods=['GET', 'POST'])
@login_required
def favorite():
    db_sess = db_session.create_session()
    like = db_sess.query(Like).filter(Like.user == current_user).all()
    return render_template('favorite.html', title='Любимое', like=like)


@app.route('/mine', methods=['GET', 'POST'])
@login_required
def mine():
    db_sess = db_session.create_session()
    mine = db_sess.query(News).filter(News.user == current_user).all()
    return render_template('mine.html', mine=mine)


@app.route('/novetly', methods=['GET', 'POST'])
@login_required
def novetly():
    con = sqlite3.connect("db/blogs.db")
    cur = con.cursor()
    g.user = current_user.get_id()

    res_novetly = cur.execute(f"""SELECT * FROM news WHERE user_id!={g.user}""").fetchall()[::-1]
    print(res_novetly, g.user, 'new')
    return render_template('novetly.html', novetly=res_novetly)


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

    con.close()
    return render_template('top.html', top=top_songs)


@app.route('/music_delete/<int:id>/<int:name>', methods=['GET', 'POST'])
@login_required
def music_delete(id, name):
    db_sess = db_session.create_session()
    lst = {1: News, 2: Like, '1': 'mine', '2': 'favorite'}
    db_sess.delete(db_sess.query(lst[name]).filter(lst[name].id == id).first())
    db_sess.commit()
    return redirect(f'/{lst[str(name)]}')


# надо возвращаться туда, где было, а не на главную
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
    print(res_lik, res_genre, 'like')
    if res_title not in res_lik:  # для добавления только уникальных песен
        print(g.user)
        db_sess.add(Like(like=res_title, genre=res_genre, user_id=g.user))
        cur.execute(f"""INSERT INTO like (like, genre, user_id) VALUES (?, ?, ?)""", (res_title, res_genre, g.user))
    con.close()

    db_sess.commit()
    # print(page, 'page')
    return redirect('/')


@app.route('/support', methods=['GET', 'POST'])
def support():
    return render_template('support.html')


@app.route('/about_us', methods=['GET', 'POST'])
def about_us():
    return render_template('about_us.html')


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()


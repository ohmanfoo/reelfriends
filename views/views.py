# views.py

# import os
import jinja2
import json
import webapp2
import hmac
from lib.vartools import secret
from google.appengine.ext import db
from google.appengine.api import urlfetch
from lib.filmofile import (check_cache, set_fetch_timeout)
from models.models import (Film, MyFilm, User, film_key,)

CACHED = {}
# template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'),
                               autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class OhmanHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def make_secure_val(self, val):
        return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

    def check_secure_val(self, secure_val):
        val = secure_val.split('|')[0]
        if secure_val == self.make_secure_val(val):
            return val

    def set_secure_cookie(self, name, val):
        cookie_val = self.make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'text/json; charset=UTF-8'
        self.write(json_txt)

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and self.check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    # def initialize(self, *a, **kw):
    #     webapp2.RequestHandler.initialize(self, *a, **kw)
    #     uid = self.read_secure_cookie('user_id')
    #     self.user = uid and User.by_id(int(uid))
    #
    #     if self.request.url.endswith('.json'):
    #         self.format = 'json'
    #     else:
    #         self.format = 'html'

    def __init__(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'


def my_top_films(user):
    films = []
    for i in CACHED:
        if i.split('|')[0] == user:
            films.append(CACHED[i])
    return films


def topfilms(user):
    films = []
    for i in CACHED:
        if i.split('|')[0] == str(user):
            films[CACHED[i]] = CACHED[i]
    return films


def top_myfilms(user):
    myfilms = db.GqlQuery("""
                            SELECT * FROM MyFilm
                            WHERE user = :user
                            ORDER BY rating DESC
                            """, user=user)
    myfilms = list(myfilms)
    return myfilms


def top_films(update=False):
    key = 'top_ten'
    if not update and key in CACHED:
        films = CACHED[key]
    else:
        films = db.GqlQuery("""
                            SELECT * FROM Film
                            WHERE ANCESTOR IS :1
                            ORDER BY rating DESC
                            """, film_key())
        films = list(films)
        CACHED[key] = films
    return films


class FilmFront(OhmanHandler):
    def get(self):
        films = Film.all()
        self.render('topfilms.html', films=films)


class AllFilms(OhmanHandler):
    def get(self):
        films = Film.all()
        if self.format == 'html':
            self.render('films.html', films=films,
                        username=self.user.name)
        else:
            return self.render_json([film.as_dict() for film in films])


class MyFilms(OhmanHandler):
    def get(self):
        if not self.user:
            self.redirect('/signup-login')
        myfilms = MyFilm.all()
        if self.format == 'html':
            self.render('myfilms.html', myfilms=myfilms,
                        username=self.user.name)
        else:
            return self.render_json([myfilm.as_dict() for myfilm in myfilms])

    def post(self):
        def saveFilm(film_obj, user=False):
            if user:
                film_obj.put()
                user_title = film_obj.user + '|' + film_obj.title
                CACHED[user_title] = film_obj.as_dict()
                return
            else:
                film_obj.put()
                CACHED[title] = [film_obj]
                return

        if not self.user:
            self.redirect('/')

        if self.format == 'json':
            title = self.request.get('title')
            val = self.request.cookies.get('user_id').split('|')[0]
            user = User.by_id(int(val)).name
            rating = self.request.get('rating')
            blurb = self.request.get('blurb')
            if title and user:
                mytitle_check = MyFilm.by_name(title)
                title_check = Film.by_name(title)
                if not mytitle_check:
                    myfilm = MyFilm(parent=film_key(),
                                    title=title,
                                    user=user,
                                    rating=rating,
                                    blurb=blurb)
                    saveFilm(myfilm, True)
                    if not title_check:
                        set_fetch_timeout(60000)
                        urlfetch.set_default_fetch_deadline(60000)
                        search = check_cache(title)
                        if search[1] and search[0]:
                            rating = search[0][1]
                            blurb = search[1]
                            film = Film(parent=film_key(),
                                        title=title,
                                        rating=rating,
                                        blurb=blurb)
                            saveFilm(film)
                            top_films(True)
                            return self.render_json(myfilm.as_dict())
                        else:
                            myfilm = Film(title='none',
                                          rating='none',
                                          blurb='none')
                            return self.render_json(myfilm.as_dict())
                    else:
                        return self.render_json(myfilm.as_dict())
                else:
                    film = mytitle_check
                    return self.render_json(myfilm.as_dict())
            else:
                self.error(404)
                return


class FilmPage(OhmanHandler):
    def get(self, film_id):
        key = db.Key.from_path('Film', int(film_id), parent=film_key())
        film = db.get(key)
        if not film:
            self.error(404)
            return
        if self.format == 'html':
            self.render('permalink.html', post=film)
        else:
            return self.render_json(film.as_dict())


class MyFilmPage(OhmanHandler):
    def get(self, film_id):
        key = db.Key.from_path('MyFilm', int(film_id), parent=film_key())
        film = db.get(key)
        if not film:
            self.error(404)
            return
        if self.format == 'html':
            self.render('permalink.html', post=film)
        else:
            return self.render_json(film.as_dict())


class NewMyFilm(OhmanHandler):
    def get(self):
        if self.user:
            self.render("/admin/newmyfilm.html")
        else:
            self.redirect("/admin/login-form")

    def post(self):
        if not self.user:
            self.redirect("/")
        title = self.request.get('title')
        val = self.request.cookies.get('user_id').split('|')[0]
        user = User.by_id(int(val)).name
        rating = self.request.get('rating')
        blurb = self.request.get('blurb')
        if title:
            title_check = MyFilm.by_name(title)
            if not title_check:
                set_fetch_timeout(60000)
                urlfetch.set_default_fetch_deadline(60000)
                search = check_cache(title)
                if search[1] and search:
                    myfilm = MyFilm(parent=film_key(),
                                    title=title,
                                    user=user,
                                    rating=rating,
                                    blurb=blurb)
                    myfilm.put()
                    t = Film.by_name(title)
                    if t:
                        self.redirect('/')
                    else:
                        rating = search[0][1]
                        blurb = search[1]
                        u = Film(parent=film_key(),
                                 title=title,
                                 rating=rating,
                                 blurb=blurb)
                        u.put()
                        top_films(True)
                        self.redirect('/')
                else:
                    error = 'not found'
                    self.render("/admin/newmyfilm.html", title=title,
                                error=error)
            else:
                self.redirect('/')
        else:
            error = "darf"
            self.render("/admin/newmyfilm.html", title=title,
                        error=error)


class NewFilm(OhmanHandler):
    def get(self):
        if self.user:
            self.render("/admin/newmyfilm.html")
        else:
            self.redirect("/admin/login-form")

    def post(self):
        if not self.user:
            self.redirect("/")
        title = self.request.get('title')
        if title:
            set_fetch_timeout(60000)
            urlfetch.set_default_fetch_deadline(60000)
            search = check_cache(title)
            if search:
                rating = search[0][1]
                blurb = search[1]
                film = Film(parent=film_key(),
                            title=title,
                            rating=rating,
                            blurb=blurb)
                film.put()
                top_films(True)
                self.redirect('/')
            else:
                error = 'not found'
                self.render("newmyfilm.html", title=title,
                            error=error)
        else:
            error = "darf"
            self.render("newmyfilm.html", title=title,
                        error=error)

# models.py

from google.appengine.ext import db
from lib.vartools import *
import logging


def users_key(group = 'default'):
    return db.Key.from_path('users', group)
def myfilm_key(name = 'default'):
    return db.Key.from_path('myfilms', name)
def film_key(film = 'default'):
    return db.Key.from_path('films', film)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty(required = True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())
    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u
    @classmethod
    def register(cls, name, pw, email):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)
    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

class Film(db.Model):
    @classmethod
    def by_id(cls, uid):
        return Film.get_by_id(uid, parent = film_key())
    @classmethod
    def by_name(cls, title):
        u = Film.all().filter('title =', title).get()
        return u
    title = db.StringProperty(required = True)
    rating = db.StringProperty()
    blurb = db.TextProperty()
    keywords = db.TextProperty()

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render("film.html", film = self)

    def as_dict(self):
        time_fmt = '%c'
        d = {'title': self.title,
             'rating': self.rating,
             'blurb': self.blurb,
             'keywords': self.keywords}
        return d

class MyFilm(db.Model):
    @classmethod
    def by_id(cls, uid):
        return MyFilm.get_by_id(uid, parent = film_key())
    @classmethod
    def by_name(cls, title):
        u = MyFilm.all().filter('title =', title).get()
        return u
    title = db.StringProperty(required = True)
    user = db.StringProperty(required = True)
    rating = db.StringProperty()
    blurb = db.TextProperty()
    keywords = db.TextProperty()

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render("film.html", film = self)

    def as_dict(self):
        time_fmt = '%c'
        d = {'mytitle': self.title,
             'user': self.user,
             'myrating': self.rating,
             'myblurb': self.blurb,
             'mykeywords': self.keywords}
        return d

# class Project(db.Model):
#     url = db.StringProperty(required = True)
#     title = db.StringProperty(required = True)
#     blurb = db.StringProperty(multiline = True)
#     screenshot = ".jpg"
#
#     def render(self):
#         return render("project.html", app = self)
# class Post(db.Model):
#     subject = db.StringProperty(required = True)
#     content = db.TextProperty(required = True)
#     created = db.DateTimeProperty(auto_now_add = True)
#     last_modified = db.DateTimeProperty(auto_now = True)
#     createdby = db.StringProperty()
#
#     def render(self):
#         self._render_text = self.content.replace('\n', '<br>')
#         return render_str("post.html", p = self)
#

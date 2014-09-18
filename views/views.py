# views.py

import os
import webapp2
from google.appengine.ext import db
from google.appengine.api import urlfetch
import jinja2
from lib.vartools import *
from lib.filmofile import *
from models.models import *
from filmfile import jinja_env
from filmfile import render_str
from filmfile import *

class OhmanHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'

class FilmFront(OhmanHandler):
    def get(self):
        films = Film.all()
        self.render('topfilms.html', films = films)

class AllFilms(OhmanHandler):
    def get(self):
        films = Film.all()
        if self.format == 'html':
            self.render('films.html', films = films,
                                    username = self.user.name)
        else:
            return self.render_json([film.as_dict() for film in films])

class MyFilms(OhmanHandler):
    def get(self):
        if not self.user:
            self.redirect('/signup-login')
        myfilms = MyFilm.all()
        if self.format == 'html':
            self.render('myfilms.html', myfilms = myfilms,
                                        username = self.user.name)
        else:
            return self.render_json([myfilm.as_dict() for myfilm in myfilms])

    def post(self):
        def saveFilm(film_obj, user=False):
            if user:
                film_obj.put()
                logging.error('myfilm added to filmfile')
                user_title = film_obj.user +'|'+ film_obj.title
                CACHED[user_title] = film_obj.as_dict()
                logging.error('myfilm CACHED')
                logging.error(CACHED[user_title])
                return
            else:
                film_obj.put()
                logging.error('film added to filmfile')
                CACHED[title] = [film_obj]
                logging.error(CACHED[title])
                logging.error('film CACHED')
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
                    logging.error('film not in user filmfile')
                    myfilm = MyFilm(parent = film_key(),
                            title = title,
                            user = user,
                            rating = rating,
                            blurb = blurb)
                    saveFilm(myfilm, True)
                    if not title_check:
                        logging.error('new title request sent')
                        set_fetch_timeout(60000)
                        urlfetch.set_default_fetch_deadline(60000)
                        search = check_cache(title)
                        if search[1] and search[0]:
                            logging.error('film found-ratings found')
                            rating = search[0][1]
                            blurb = search[1]
                            film = Film(parent = film_key(),
                                        title = title,
                                        rating = rating,
                                        blurb = blurb)
                            saveFilm(film)
                            top_films(True)
                            logging.error('film saved to master filmfile')
                            return self.render_json(myfilm.as_dict())
                        else:
                            logging.error('no ratings or film found')
                            myfilm = Film(title='none',
                                            rating = 'none',
                                            blurb = 'none')
                            return self.render_json(myfilm.as_dict())
                    else:
                        logging.error('title found in db')
                        return self.render_json(myfilm.as_dict())
                else:
                    error = 'film already in library'
                    logging.error(error)
                    myfilm = mytitle_check
                    return self.render_json(myfilm.as_dict())
            else:
                logging.error('unlogged in user attempted POST')
                self.error(404)
                return



class FilmPage(OhmanHandler):
    def get(self, film_id):
        key = db.Key.from_path('Film', int(film_id), parent = film_key())
        film = db.get(key)
        if not film:
            self.error(404)
            return
        if self.format == 'html':
            self.render('permalink.html', post = film)
        else:
            return self.render_json(film.as_dict())

class MyFilmPage(OhmanHandler):
    def get(self, film_id):
        key = db.Key.from_path('MyFilm', int(film_id), parent = film_key())
        film = db.get(key)
        if not film:
            self.error(404)
            return
        if self.format == 'html':
            self.render('permalink.html', post = film)
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
                    myfilm = MyFilm(parent = film_key(),
                                title = title,
                                user = user,
                                rating = rating,
                                blurb = blurb)
                    myfilm.put()
                    t = Film.by_name(title)
                    if t:
                        self.redirect('/')
                    else:
                        rating = search[0][1]
                        blurb = search[1]
                        u = Film(parent = film_key(),
                                title = title,
                                rating = rating,
                                blurb = blurb)
                        u.put()
                        top_films(True)
                        self.redirect('/')
                else:
                    error = 'not found'
                    self.render("/admin/newmyfilm.html", title = title,
                                                    error = error)
            else:
                self.redirect('/')
        else:
            error = "darf"
            self.render("/admin/newmyfilm.html", title = title,
                                          error = error)

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
                film = Film(parent = film_key(),
                            title = title,
                            rating = rating,
                            blurb = blurb)
                film.put()
                top_films(True)
                self.redirect('/')
            else:
                error = 'not found'
                self.render("newmyfilm.html", title = title,
                                                error = error)
        else:
            error = "darf"
            self.render("newmyfilm.html", title = title,
                                          error = error)

# class ProjFront(OhmanHandler):
#     def get(self):
#         projects = Project.all()
#         self.render('projects.html', projects = projects)
#
# class BlogFront(OhmanHandler):
#     def get(self):
#         posts = Post.all().order('-created')
#         self.render('blog.html', posts = posts)
#
# class ProjPage(OhmanHandler):
#     def get(self, proj_id):
#         key = db.Key.from_path('Proj', int(proj_id), parent = proj_key())
#         proj = db.get(key)
#         if not proj:
#             self.error(404)
#             return
#         self.render("permalink.html", post = proj)
#
# class PostPage(OhmanHandler):
#     def get(self, post_id):
#         key = db.Key.from_path('Post', int(post_id), parent = blog_key())
#         post = db.get(key)
#         if not post:
#             self.error(404)
#             return
#         self.render("permalink.html", post = post)
#
# class NewProject(OhmanHandler):
#     def get(self):
#         if self.user:
#             self.render("/admin/newproject.html")
#         else:
#             self.redirect("/admin/login-form")
#
#     def post(self):
#         if not self.user:
#             self.redirect("/")
#         url = self.request.get('url')
#         title = self.request.get('title')
#         blurb = self.request.get('blurb')
#         if title and blurb and url:
#             screenshot = 'somethinghere'
#             pro = Project(parent = project_key(),
#                             url = url, 
#                             title = title,
#                             blurb = blurb, 
#                             screenshot = screenshot)
#             pro.put()
#             self.redirect('/')
#         else:
#             error = "shit negro"
#             self.render("newproject.html", url = url,
#                                             title = title,
#                                             blurb = blurb,
#                                             screenshot = screenshot,
#                                             error = error)
#
# class NewPost(OhmanHandler):
#     def get(self):
#         if self.user:
#             self.render("/admin/newpost.html")
#         else:
#             self.redirect("/admin/login-form")
#
#     def post(self):
#         if not self.user:
#             self.redirect("/")
#         subject = self.request.get('subject')
#         content = self.request.get('content')
#     	val = self.request.cookies.get('user_id').split('|')[0]
#         createdby = User.by_id(int(val)).name
#         if subject and content and createdby:
#             p = Post(parent = blog_key(), subject = subject, 
#             			content = content, 
#             			createdby = createdby)
#             p.put()
#             self.redirect('/blog/%s' % str(p.key().id()))
#         else:
#             error = 'shit negro'
#             self.render('/admin/newpost', subject=subject, 
#             			content=content, 
#             			error=error)
#
# application = webapp2.WSGIApplication([('/blog/?', BlogFront),
#
#                                ('/blog/([0-9]+)', PostPage),
#                                ('/admin/newpost', NewPost),
#                                ('/admin/newproject', NewProject),
#                                ('/admin/signup-form', Register),
#                                ('/admin/login-form', Login),
#                                ('/logout', Logout),
#
#                                ('/admin/register', RegisterInvite),
#                                ],
#                               debug=True)

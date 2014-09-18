# ohmanfoo.py

import os
import webapp2
import jinja2
import urllib2
from lib.vartools import *
from google.appengine.api import urlfetch
from google.appengine.api import mail
from google.appengine.ext import db
from models.models import *
from lib.filmofile import *

CACHED = {}

def top_films(update=False):
    key = 'top_ten'
    if not update and key in CACHED:
        films = CACHED[key]
        logging.error('retrieved from Film CACHED')
    else:
        logging.error('DBQUERY = Film')
        films = db.GqlQuery("SELECT * FROM Film WHERE ANCESTOR IS :1 ORDER BY rating DESC", film_key())
        films = list(films)
        CACHED[key] = films        
        logging.error('this is supposed to update the Film CACHED shit')
    return films

def my_top_films(user):
    films = []
    for i in CACHED:
        logging.error(i)
        if i.split('|')[0] == user:
            films.append(CACHED[i])
            logging.error('Found my top films in CACHED')
    logging.error(type(films))
    logging.error(films)
    logging.error(CACHED)
    return films

def topfilms(user):
    films = []
    for i in CACHED:
        if i.split('|')[0] == str(user):
            films[CACHED[i]] = CACHED[i]
    logging.error('Returned mytops from cache')

    return films




def top_myfilms(user, update=False):
    logging.error('DBQUERY = getting top_MyFilms')
    myfilms = db.GqlQuery("SELECT * FROM MyFilm WHERE user = :user ORDER BY rating DESC", user=user)
    myfilms = list(myfilms)
    return myfilms


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

from views.views import *

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

class Login(OhmanHandler):
    def get(self):
        if not self.user:
            self.render('/admin/login-form.html')
        else:
            myfilms = MyFilm.all()
            self.render('api/myfilms', myfilms = myfilms,
                                        username = self.user.name)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/api/myfilms')
        else:
            msg = 'Invalid login'
            self.render('/admin/login-form.html', error = msg)

class Logout(OhmanHandler):
    def get(self):
        self.logout()
        self.redirect('/')

class Signup(OhmanHandler):
    def get(self):
        if self.user:
            self.redirect('/backbone-test')
        else:
            self.render('/signup-form.html')

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        params = dict(username = self.username,
                      email = self.email)
        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True
        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True
        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True
        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'Name taken!'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/backbone-test')

class MainPage(OhmanHandler):
    def get(self):
        films = top_films()
        loggedin = self.user
        if loggedin:
            username = self.user.name            
            myfilms = my_top_films(username)
        else:
            username = '/signup-login'
            myfilms = []
        self.response.headers['Content-Type'] = 'text/html'
        self.render("topfilms.html", films = films,
                                    myfilms = myfilms,
                                    username = username)

class MainBackBonePage(OhmanHandler):
    def get(self):
        if not self.user:
            self.redirect('/')
        # myfilms = MyFilm.all()
        # films = Film.all()
        #filmjson = films.toJSON(films)
        else:
            self.render("/index.html", username = self.user.name)

    def post(self):
        if not self.user:
            self.redirect("/")
        title = self.request.get('title')
        val = self.request.cookies.get('user_id').split('|')[0]
        user = User.by_id(int(val)).name
        myrating = self.request.get('rating')
        myblurb = self.request.get('blurb')
        keywords = self.request.get('keywords')
        if title:
            title_check = Film.by_name(title)
            if not title_check:
                set_fetch_timeout(60000)
                urlfetch.set_default_fetch_deadline(60000)
                search = check_cache(title)
                if search[1] and search[0]:
                    rating = search[0][1]
                    blurb = search[1]
                    film = Film(parent = film_key(),
                                title = title,
                                rating = rating,
                                blurb = blurb,
                                keywords = keywords)
                    film.put()
                    top_films(True)
                    mytitle_check = MyFilm.by_name(title)
                    if mytitle_check:
                    # if in myfilm collection go to that film page
                        self.render('/index.html')
                    else:
                        myfilm = MyFilm(parent = film_key(),
                                title = title,
                                user = user,
                                rating = myrating,
                                blurb = myblurb,
                                keywords = keywords)
                        myfilm.put()
                        self.render('/index.html')
                else:
                    error = 'not found'
                    mytitle_check = MyFilm.by_name(title)
                    if mytitle_check:
                        self.render('/index.html')
                    self.render("/index.html", title = title,
                                               error = error)
            else:
                mytitle_check = MyFilm.by_name(title)
                if mytitle_check:
                    # if in myfilm collection go to that film page
                    self.render('/index.html')
                else:
                    myfilm = MyFilm(parent = film_key(),
                            title = title,
                            user = user,
                            rating = myrating,
                            blurb = myblurb,
                            keywords = keywords)
                    myfilm.put()
                    self.render('/index.html')
        else:
            error = "darf"
            self.render("/index.html", title = title,
                                    error = error)

application = webapp2.WSGIApplication([('/', MainPage),
                               # ('/blog/([0-9]+)', PostPage),
                               ('/api/films/?(?:.json)?', AllFilms),
                               ('/api/myfilms/?(?:.json)?', MyFilms),
                               ('/api/films/([0-9]+)(?:.json)?', FilmPage),
                               ('/api/myfilms/([0-9]+)(?:.json)?', MyFilmPage),
                               ('/backbone-test', MainBackBonePage),
                               ('/admin/newmyfilm', NewMyFilm),
                               ('/signup-login', Register),
                               ('/admin/login-form', Login),
                               ('/logout', Logout),
                               ],
                              debug=True)

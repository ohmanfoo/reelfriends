# filmfile.py
import re
from google.appengine.api import urlfetch
import webapp2
from views.views import (OhmanHandler,
                         AllFilms,
                         MyFilms,
                         FilmPage,
                         MyFilmPage,
                         NewMyFilm,
                         top_films,
                         my_top_films,
                         )
from models.models import (User,
                           Film,
                           MyFilm,
                           film_key)
from lib.filmofile import (check_cache, set_fetch_timeout)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,30}$")
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
PASS_RE = re.compile(r"^.{3,20}$")


class Login(OhmanHandler):
    def get(self):
        if not self.user:
            self.render('/admin/login-form.html')
        else:
            myfilms = MyFilm.all()
            self.render('api/myfilms', myfilms=myfilms,
                        username=self.user.name)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/api/myfilms')
        else:
            msg = 'Invalid login'
            self.render('/admin/login-form.html', error=msg)


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
        params = dict(username=self.username,
                      email=self.email)
        if not self.valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True
        if not self.valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True
        if not self.valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True
        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

        def valid_username(username):
            return username and USER_RE.match(username)

        def valid_password(password):
            return password and PASS_RE.match(password)

        def valid_email(email):
            return EMAIL_RE.match(email)

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(Signup):
    def done(self):
        # make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'Name taken!'
            self.render('signup-form.html', error_username=msg)
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
        self.render("topfilms.html", films=films,
                    myfilms=myfilms,
                    username=username)


class MainBackBonePage(OhmanHandler):
    def get(self):
        if not self.user:
            self.redirect('/')
        else:
            self.render("/index.html", username=self.user.name)

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
                    film = Film(parent=film_key(),
                                title=title,
                                rating=rating,
                                blurb=blurb,
                                keywords=keywords)
                    film.put()
                    top_films(True)
                    mytitle_check = MyFilm.by_name(title)
                    if mytitle_check:
                        # if in myfilm collection go to that film page
                        self.render('/index.html')
                    else:
                        myfilm = MyFilm(parent=film_key(),
                                        title=title,
                                        user=user,
                                        rating=myrating,
                                        blurb=myblurb,
                                        keywords=keywords)
                        myfilm.put()
                        self.render('/index.html')
                else:
                    error = 'not found'
                    mytitle_check = MyFilm.by_name(title)
                    if mytitle_check:
                        self.render('/index.html')
                    self.render("/index.html", title=title,
                                error=error)
            else:
                mytitle_check = MyFilm.by_name(title)
                if mytitle_check:
                    # if in myfilm collection go to that film page
                    self.render('/index.html')
                else:
                    myfilm = MyFilm(parent=film_key(),
                                    title=title,
                                    user=user,
                                    rating=myrating,
                                    blurb=myblurb,
                                    keywords=keywords)
                    myfilm.put()
                    self.render('/index.html')
        else:
            error = "Leave, we've fallen, said the other . . ."
            self.render("/index.html", title=title,
                        error=error)

application = webapp2.WSGIApplication(
            [('/', MainPage),
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

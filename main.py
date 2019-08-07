import webapp2
import jinja2
import os
from models import Meme, CssiUser
from google.appengine.api import users


the_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def checkLoggedInAndRegistered(request):
    # Check if user is logged in
    
    user = users.get_current_user()
        
    if not user: 
        request.redirect("/login")
        return
    
    # Check if user is registered
       
    email_address = user.nickname()
    registered_user = CssiUser.query().filter(CssiUser.email == email_address).get()
    
    if not registered_user:
         request.redirect("/register")
         return 
    

class HomeHandler(webapp2.RequestHandler):
    def get(self):  
        checkLoggedInAndRegistered(self)
        
        the_variable_dict = {
            "logout_url":  users.create_logout_url('/')
        }
        
        welcome_template = the_jinja_env.get_template('templates/home.html')
        self.response.write(welcome_template.render(the_variable_dict))

    def post(self):
        checkLoggedInAndRegistered(self)
        
        user = users.get_current_user()
        
        meme = Meme(
            line1=self.request.get('user-first-ln'), 
            line2=self.request.get('user-second-ln'),
            owner=user.nickname(),
            img_choice=self.request.get('meme-type')
        )
        meme_key = meme.put()
        self.response.write("Meme created: " + str(meme_key) + "<br>")
        self.response.write("<a href='/allmemes'>All memes</a> | ")
        self.response.write("<a href='/usermemes'>My memes</a>")
        


class AllMemesHandler(webapp2.RequestHandler):
    def get(self):
        checkLoggedInAndRegistered(self)
        
        
        
        all_memes = Meme.query().fetch()
        
        the_variable_dict = {
            "all_memes": all_memes
        }
        
        all_memes_template = the_jinja_env.get_template('templates/all_memes.html')
        self.response.write(all_memes_template.render(the_variable_dict))

class UserMemesHandler(webapp2.RequestHandler):
    def get(self):
        checkLoggedInAndRegistered(self)
        
        user = users.get_current_user()
        email_address = user.nickname()
        
        user_memes = Meme.query().filter(Meme.owner == email_address).fetch()
        
        the_variable_dict = {
            "user_memes": user_memes
        }
        
        user_memes_template = the_jinja_env.get_template('templates/user_memes.html')
        self.response.write(user_memes_template.render(the_variable_dict))
   
        

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        
        login_template = the_jinja_env.get_template('templates/login.html')
        the_variable_dict = {
            "login_url":  users.create_login_url('/')
        }
        
        self.response.write(login_template.render(the_variable_dict))
        

class RegistrationHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        registration_template = the_jinja_env.get_template('templates/registration.html')
        the_variable_dict = {
            "email_address":  user.nickname()
        }
        
        self.response.write(registration_template.render(the_variable_dict))
    
    def post(self):
        user = users.get_current_user()
        
        #Create a new CSSI User in our database
        
        cssi_user = CssiUser(
            first_name=self.request.get('first_name'), 
            last_name =self.request.get('last_name'), 
            email=user.nickname()
        )
        
        cssi_user.put()
        
        self.response.write('Thanks for signing up, %s! <br><a href="/">Home</a>' %
        cssi_user.first_name)
        
                  
    
app = webapp2.WSGIApplication([
    ('/', HomeHandler),
    ('/allmemes', AllMemesHandler), 
    ('/usermemes', UserMemesHandler), 
    ('/login', LoginHandler),
    ('/register', RegistrationHandler)
], debug=True)
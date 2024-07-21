from flask import Flask
from flask_login import LoginManager
from json_modules import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(int(user_id))

from routes import *

if __name__ == '__main__':
    app.run(debug=True)

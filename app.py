import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key_for_local_testing')

# Datenbankkonfiguration für Heroku Postgres ODER lokale SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://') or 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#url check? ggf falsch?

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'routes.login'

bootstrap = Bootstrap(app)

from routes import routes_blueprint
app.register_blueprint(routes_blueprint)

from models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from datetime import datetime
@app.template_filter('format_datetime')
def format_datetime_filter(value, format="%d.%m.%Y %H:%M"):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

if __name__ == '__main__':
    app.run(debug=True) # ACHTUNG: debug=True ist NICHT für Produktion empfohlen!
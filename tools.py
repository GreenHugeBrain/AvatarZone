from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from forms import RegistrationForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
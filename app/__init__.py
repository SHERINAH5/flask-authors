from flask import Flask
from app.extentions import db,migrate,jwt
from app.controllers.auth.auth_cotroller import auth
from app.controllers.users.user_controller import users
from app.controllers.companies.company_cotroller import companies
from app.controllers.books.book_controller import books


def create_app():

    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app,db)
    jwt.init_app(app)

    #importing models
    from app.models.users import User
    from app.models.companies import Company
    from app.models.books import Book
    
    #registering blue prints
    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(companies)
    app.register_blueprint(books)
    


    @app.route('/')
    def home():
        return 'Authors API'


    return app
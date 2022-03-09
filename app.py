from flask import Flask, make_response, request, g, abort
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime as dt, timedelta
import secrets
from flask_cors import CORS

class Config():
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
cors = CORS(app)

@basic_auth.verify_password
def verify_password(email, password):
    u = User.query.filter_by(email=email.lower()).first()
    if u is None:
        return False
    g.current_user = u
    return u.check_hashed_password(password)

@token_auth.verify_token
def verify_token(token):
    u = User.check_token(token) if token else None
    g.current_user = u
    return g.current_user or None


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, index=True, unique=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    password = db.Column(db.String)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    modified_on = db.Column(db.DateTime, onupdate=dt.utcnow)
    token = db.Column(db.String, index=True, unique=True)
    token_exp = db.Column(db.DateTime)

    def get_token(self, exp=86400):
        current_time = dt.utcnow()
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_urlsafe(32)
        self.token_exp = current_time + timedelta(seconds=exp)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_exp = dt.utcnow() - timedelta(seconds=61)

    @staticmethod
    def check_token(token):
        u = User.query.filter_by(token=token).first()
        if not u or u.token_exp < dt.utcnow():
            return None
        return u

    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<{self.user_id}|{self.email}>'

    def from_dict(self, data):
         for field in ["email","password", "first_name","last_name"]:
            if field in data:
                if field == "password":
                    setattr(self,field, self.hash_password(data[field]))
                else:
                    setattr(self,field, data[field])


    def register(self, data):
        self.email = data['email']
        self.password = self.hash_password(data['password'])
        self.first_name = data['first_name']
        self.last_name = data['last_name']

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "created_on":self.created_on,
            "modified_on":self.modified_on,
            "first_name":self.first_name,
            "last_name":self.last_name,
            "token":self.token
            }

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    author = db.Column(db.String)
    pages = db.Column(db.Integer)
    summary = db.Column(db.String)    
    img = db.Column(db.String)

    subject = db.Column(db.String)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
   

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<{self.id}|{self.title}>'

    def from_dict(self,data):
         for field in ["title","author", "pages","summary", "subject", "img"]:
            if field in data:
                setattr(self,field, data[field])
 

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author":self.author,
            "pages":self.pages,
            "summary":self.summary,
            'subject':self.subject,
            "created_on":self.created_on,
            "img":self.img
            }


    ##############
    # API ROUTES #
    ##############
'''
    Responses:
    200 : Everything went well
    401 : Invalid Token, or invalid Username/Password,
    403 : User not authorized for action
    404 : Resource not found
    500 : Server Side Error
'''

@app.get('/login')
@basic_auth.login_required()
def login():
    '''
        BasicAuth: base64encoded string=> user_name:password
        Authorization: Basic base64encoded_string
        returns user information including token
    '''
    g.current_user.get_token()
    return make_response(g.current_user.to_dict(), 200)


@app.post('/user')
def post_user():
    '''
        No Auth
        creates a new user.
        expected payload:
        {
            "email" : STRING,
            "first_name" : STRING,
            "last_name" : STRING
            "password" : STRING,
            
        }
    '''
    data = request.get_json()
    if User.query.filter_by(email=data.get('email')).first():
        abort(422)
    new_user = User()
    new_user.register(data)
    new_user.save()
    return make_response("success",200)

@app.put('/user')
@token_auth.login_required()
def put_user():
    '''
        Changes the information fro the user that has the token

        TokenAuth: Bearer TOKEN
        expected payload (does not need to include all key value pairsAny omitted values will remain unchanged):
        {
            "email" : STRING,
            "first_name" : STRING,
            "last_name" : STRING
            "password" : STRING,
        }
    '''
    data = request.get_json()
    g.current_user.from_dict(data)
    db.session.commit()
    return make_response("success",200)

@app.delete('/user')
@token_auth.login_required()
def delete_user():
    '''
        Can only be used by the user with <user_id>

        TokenAuth: Bearer TOKEN
        Will delete User accesing the endpoint
    '''
    g.current_user.delete()
    return make_response("success",200)


@app.get('/book')
def get_books():
    '''
        No Auth
        
        returns All Books information
    '''
    return make_response({"books":[book.to_dict() for book in Book.query.all()]}, 200)

@app.get('/book/<int:id>')
def get_book(id):
    '''
        No Auth
        
        returns info for the book with the id:id
    '''
    return make_response(Book.query.filter_by(id=id).first().to_dict(), 200)


@app.post('/book')
@token_auth.login_required()
def post_books():
    '''
        Creates a books in bulk

        TokenAuth: Bearer TOKEN
        creates a new book.

        expected payload:
        [{
            title : STRING,
            author : STRING,
            pages : INTEGER,
            summary : STRING,
            subject : STRING,
            img :  STRING URL
        },
        {
            title : STRING,
            author : STRING,
            pages : INTEGER,
            summary : STRING,
            subject : STRING,
            img :  STRING URL
        }
        ]
    '''
    if g.current_user.email.lower() !="kevinb@codingtemple.com":
        abort(403)
    data = request.get_json()
    books=[]
    for d in data:
        new_book = Book()
        new_book.from_dict(d)
        books.append(new_book)
    db.session.add_all(books)
    db.session.commit()
    return make_response("success",200)


if __name__=="__main__":
    app.run(debug=True) 
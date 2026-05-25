#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate

from models import db, Article, User, ArticleSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles')
def index_articles():
    articles = [ArticleSchema().dump(a) for a in Article.query.all()]
    return make_response(articles)

@app.route('/articles/<int:id>')
def show_article(id):
    # track & increment page views (cookie/session)
    # check page_views exists as key in user's session data
    if 'page_views' not in session: 
        # first time visitng: key won't exist
        session['page_views'] = 0 # initial 0 value 
    
    # page loads: add 1 to current count
    # new user: 0 -> 1 very first page load 
    session['page_views'] += 1 # increment by 1 

    # pageview limit (security & limit check)
    if session['page_views'] > 3:
        # viewed > 3 pages: JSON response (error message & status code 401(unauthorized))
        # page view hits 4 
        return make_response(
            jsonify({'message': 'Maximum pageview limit reached'}), 
            401
        )

    # query db for requested article 
    # pass limit check: look for article in db 
    # 'filter_by(id=id)': search article table where column id matches URL variable 
    # '.first()': grabs single matching row OR return None
    article = Article.query.filter_by(id=id).first()
    if not article: 
        # article none: return error & 404 (Not Found) status code
        return make_response(
            jsonify({'error': 'Article not found'}), 
            404
        )

    # serialize & return article data
    # 'ArticleSchema().dump(article)': convert raw db row into python dictionary 
    serialize_article = ArticleSchema().dump(article)
    # successful 200 (OK) status code
    return make_response(
        jsonify(serialize_article), 
        200
    )

if __name__ == '__main__':
    app.run(port=5555)

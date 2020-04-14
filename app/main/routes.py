from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app.models import User
from app.main import bp
from app import db
from datetime import datetime
from sqlalchemy import text

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    sql = text('SELECT title, author, year, isbn FROM book ORDER BY random() LIMIT 4')
    q = db.engine.execute(sql)
    return render_template('index.html', title='Home', rnd_book=q)


@bp.route('/search', methods=['GET'])
@login_required
def search():

    search_book = request.args.get('book')

    if not search_book:
        flash('You must provide a book.', 'warning')
        return render_template('index.html', title='Error')
    elif len(search_book) < 3:
        flash('You should enter more than 3 characters','warning') 
        return render_template('index.html', title='Error')
    else:
        query = '%' + search_book + '%'
        sql = text('SELECT title, author, year, isbn FROM book WHERE \
                    isbn LIKE :query OR \
                    title LIKE :query OR \
                    author LIKE :query LIMIT 4')
        book_result = db.engine.execute(sql, {"query" : query})

        if book_result.rowcount == 0:
            flash("we can't find books with that description.", "warning")
        return render_template('index.html', rnd_book=book_result)



@bp.route('/book/<isbn>', methods=['GET', 'POST'])
@login_required
def book(isbn):
    sql = text('SELECT title, author, year, isbn FROM book WHERE isbn LIKE :isbn')
    book_result = db.engine.execute(sql, {'isbn': isbn})
    return render_template('index.html', rnd_book=book_result)

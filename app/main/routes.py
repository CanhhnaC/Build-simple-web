from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import current_user, login_required
from app.models import User, Book
from app.main import bp
from app import db
from datetime import datetime
from sqlalchemy import text
import os
import requests
import json


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    # Postgresql
    # sql = text('SELECT title, author, year, isbn FROM book ORDER BY RAND() LIMIT 4')

    # SQL Server
    sql = text(
        'SELECT TOP 4 title, author, "year", isbn FROM book ORDER BY NEWID()')
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
        flash('You should enter more than 3 characters', 'warning')
        return render_template('index.html', title='Error')
    else:
        query = '%' + search_book + '%'
        sql = text('SELECT TOP 4 title, author, year, isbn FROM book WHERE \
                    isbn LIKE :query OR \
                    title LIKE :query OR \
                    author LIKE :query')
        book_result = db.engine.execute(sql, {"query": query})

        if book_result.rowcount == 0:
            flash("we can't find books with that description.", "warning")
        return render_template('index.html', rnd_book=book_result)


def get_rating(isbn, book_result):
    key = '8LMzrOv53AsM8C5D8hag'
    query = requests.get("https://www.goodreads.com/book/review_counts.json",
                         params={"key": key, "isbn": isbn})
    response = query.json()
    response = response['books'][0]
    book_result.append(response)
    return book_result


@bp.route('/book/<isbn>', methods=['GET', 'POST'])
@login_required
def book(isbn):
    sql = text('SELECT title, author, year, isbn FROM book WHERE isbn LIKE :isbn')
    book_result = db.engine.execute(sql, {'isbn': isbn})
    book_result = book_result.fetchall()

    if book_result is None:
        return render_template('/error/404.html')

    sql = text('SELECT id FROM book WHERE isbn = :isbn')
    row = db.engine.execute(sql, {'isbn': isbn})

    if request.method == 'POST':
        currentUser = current_user.get_id()
        rating = request.form.get('rating')
        comment = request.form.get('comment')

        bookId = row.fetchone()
        bookId = bookId[0]

        sql = text(
            'SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id ')
        row2 = db.engine.execute(sql, {'user_id': currentUser,
                                       'book_id': bookId})

        if row2.rowcount == 1:
            flash('You already submitted a review for this book', 'warning')
            return redirect("/book/" + isbn)

        rating = int(rating)

        sql = text('INSERT INTO reviews (user_id, book_id, comment, rating) VALUES \
                    (:user_id, :book_id, :comment, :rating)')

        db.engine.execute(sql, {'user_id': currentUser,
                                'book_id': bookId,
                                'comment': comment,
                                'rating': rating})
        db.session.commit()
        flash('review submitted', 'info')

        return redirect('/book/'+isbn)

    else:
        book = row.fetchone()
        book = book[0]

        sql = text('SELECT "user".username, reviews."comment", reviews.rating \
                            FROM "user" \
                            INNER JOIN reviews \
                            ON "user".id = reviews.user_id \
                            WHERE book_id = :book')

        results = db.engine.execute(sql, {'book': book})
        reviews = results.fetchall()

    return render_template('book.html', book_result=book_result, reviews=reviews)


@bp.route('/api/<isbn>', methods=['GET'])
@login_required
def api_call(isbn):

    sql = text("SELECT title, author, year, isbn, \
                COUNT(reviews.id) as review_count, \
                AVG(reviews.rating) as average_score \
                FROM book \
                INNER JOIN reviews \
                ON book.id = reviews.book_id \
                WHERE isbn = :isbn \
                GROUP BY title, author, year, isbn;")

    row = db.engine.execute(sql, {'isbn': isbn})

    if row.rowcount != 1:
        return jsonify({"Error": "Invalid book ISBN"}), 422

    tmp = row.fetchone()

    print(tmp)
    print('-------------------------------')

    result = dict(tmp.items())

    result['average_score'] = float('%.2f' % (result['average_score']))

    print(result)

    return jsonify(result)

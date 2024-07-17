import logging
from datetime import datetime

from flask import Blueprint, request, jsonify, abort
from flask_pydantic import validate
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from . import db, SERIAL_NUMBER_DIGITS
from .helpers import verify_number, verify_book_was_not_deleted
from .models import Book, Author, LibraryUser, Borrowing

books_bp = Blueprint('books', __name__)
users_bp = Blueprint('users', __name__)


@books_bp.route('/', methods=['GET'])
@validate()
def get_books():
    """
    Get all books
    ---
    responses:
      200:
        description: A successful response
    """
    books = Book.query.filter(Book.deleted == False).all()
    return jsonify([book.to_dict() for book in books])


@books_bp.route('/', methods=['POST'])
@validate()
def add_book():
    """
    Add a new book to the library. If author doesn't exist, it will be created
    ---
    parameters:
      - name: serial_number
        in: query
        type: string
        required: true
        description: 6 digit book serial number
      - name: title
        in: query
        type: string
        required: true
        description: book title
      - name: author_firstname
        in: query
        type: string
        required: true
        description: Book author first name
      - name: author_lastname
        in: query
        type: string
        required: true
        description: Book author last name
    responses:
      201:
        description: Book created
      409:
        description: Book with this serial number already exists
      415:
        description: Serial number malformed
    """
    serial_number: str = request.args["serial_number"]
    title: str = request.args["title"]
    author_firstname: str = request.args["author_firstname"]
    author_lastname: str = request.args["author_lastname"]
    verify_number(SERIAL_NUMBER_DIGITS, serial_number=serial_number)
    existing_author = Author.query.filter(and_(Author.first_name == author_firstname),
                                          (Author.last_name == author_lastname)).first()
    if existing_author:
        author = existing_author
    else:
        author = Author(first_name=author_firstname, last_name=author_lastname)

    new_book = Book(
        serial_number=int(serial_number),
        title=title,
        author=author
    )
    db.session.add(new_book)
    try:
        db.session.commit()
    except IntegrityError as ie:
        abort(409, description=f"Book with this serial number already exists: {ie}")
    return jsonify(new_book.to_dict()), 201


@books_bp.route('/<string:serial_number>', methods=['DELETE'])
@validate()
def delete_book(serial_number: str):
    """
    Remove a book from a library
    ---
    parameters:
      - name: serial_number
        in: path
        type: string
        required: true
        description: 6 digit book serial number
    responses:
      200:
        description: Book deleted
      404:
        description: Book not found
    """
    verify_number(SERIAL_NUMBER_DIGITS, serial_number=serial_number)
    book = Book.query.filter(and_(Book.serial_number == serial_number), (Book.deleted == False)).first_or_404()
    book.deleted = True
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})


@books_bp.route('/borrow/<string:serial_number>/', methods=['POST'])
@validate()
def borrow_book(serial_number: str):
    """
    Borrow the book
    ---
    parameters:
      - name: serial_number
        in: path
        type: string
        required: true
        description: 6 digit book serial number
      - name: library_card
        in: query
        type: string
        required: true
        description: 6 digit library card number
    responses:
      200:
        description: Book borrowed successfully
      404:
        description: Book not found
      409:
        description: Book is already borrowed!
    """
    library_card: str = request.args["library_card"]
    verify_number(SERIAL_NUMBER_DIGITS, serial_number=serial_number, library_card=library_card)
    book = Book.query.get_or_404(int(serial_number))
    verify_book_was_not_deleted(book)
    if not book.is_available():
        abort(409, description="The book is already borrowed")
    user = LibraryUser.query.get_or_404(int(library_card))

    borrowing = Borrowing(book=book, user=user, borrow_date=datetime.utcnow())
    db.session.add(borrowing)
    db.session.commit()
    return f"Book {book} borrowed by {user}!"


@books_bp.route('/return/<string:serial_number>/', methods=['POST'])
@validate()
def return_book(serial_number: str):
    """
    Return the book
    ---
    parameters:
      - name: serial_number
        in: path
        type: string
        required: true
        description: 6 digit book serial number
    responses:
      200:
        description: Book returned
      404:
        description: Book not found or not borrowed
    """
    verify_number(SERIAL_NUMBER_DIGITS, serial_number=serial_number)
    book = Book.query.get_or_404(serial_number)
    verify_book_was_not_deleted(book)
    borrowings = Borrowing.query.filter(and_(Borrowing.book == book), (Borrowing.return_date == None)).all()
    if not borrowings:
        return f"Book {serial_number} was not borrowed!", 404
    if len(borrowings) > 1:
        logging.error(f"More than 1 active borrowing found for book {book}: {borrowings}")
    for borrowing in borrowings:
        borrowing.return_date = datetime.utcnow()
        db.session.add(borrowing)

    db.session.commit()
    return f"Book {book} returned!"


class UserModel(BaseModel):
  library_card: str
  firstname: str = Field(..., max_length=10)
  lastname: str

@users_bp.route('/',
                methods=['POST'])
@validate()
def add_user():
    """
    Create library card for new user
    ---
    parameters:
      - name: library_card
        in: query
        type: string
        required: true
        description: 6 digit library card number
      - name: firstname
        in: query
        type: string
        required: true
        description: user's first name
      - name: lastname
        in: query
        type: string
        required: true
        description: user's last name
    responses:
      201:
        description: User created
      415:
        description: Serial number malformed
    """
    usr = UserModel(**request.args)
    verify_number(SERIAL_NUMBER_DIGITS, library_card=usr.library_card)

    new_user = LibraryUser(
        library_card=int(usr.library_card),
        first_name=usr.firstname,
        last_name=usr.lastname
    )
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError as ie:
        abort(409, description=f"Book with this serial number already exists: {ie}")
    return jsonify(new_user.to_dict()), 201


@books_bp.cli.command('seed')
def seed():
    """
        Seed sample data to database for testing purpose
    """
    # add authors
    sapkowski = Author(first_name="Andrzej", last_name="Sapkowski")
    dukaj = Author(first_name="Jacek", last_name="Dukaj")
    liu = Author(first_name="Cixin", last_name="Liu")
    db.session.add_all([sapkowski, dukaj, liu])

    # add books
    zmija = Book(serial_number=123456, title="Zmija", author=sapkowski)
    lod = Book(serial_number=234567, title="Lód", author=dukaj)
    problem_trzech_cial = Book(serial_number=345678, title="Problem trzech ciał", author=liu)
    db.session.add_all([zmija, lod, problem_trzech_cial])

    # add users
    michal = LibraryUser(library_card=987654, first_name="Michał", last_name="Kowalski")
    anna = LibraryUser(library_card=876543, first_name="Anna", last_name="Malinowska")
    jerzy = LibraryUser(library_card=765432, first_name="Jerzy", last_name="Lewandowski")
    db.session.add_all([michal, anna, jerzy])

    # add borrowings
    b1 = Borrowing(book=zmija, user=michal, borrow_date=datetime(2011, 10, 2), return_date=datetime(2011, 11, 12))
    b2 = Borrowing(book=zmija, user=anna, borrow_date=datetime(2024, 5, 2))
    b3 = Borrowing(book=lod, user=michal, borrow_date=datetime(2015, 10, 2), return_date=datetime(2015, 11, 12))
    db.session.add_all([b1, b2, b3])

    db.session.commit()

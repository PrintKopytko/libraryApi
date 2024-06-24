from flask import Blueprint, request, jsonify
from . import db
from .models import Book

books_bp = Blueprint('books', __name__)


@books_bp.route('/', methods=['GET'])
def get_books():
    """
    Get all books
    ---
    responses:
      200:
        description: A successful response
    """
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books])
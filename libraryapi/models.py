from . import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    book_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'
from typing import List, Any

from sqlalchemy import ForeignKey, Table, ColumnElement
from sqlalchemy.orm import Mapped, relationship, mapped_column, DeclarativeBase

from . import db


def to_dict(self):
    d = {}
    for column in self.__table__.columns:
        d[column.name] = str(getattr(self, column.name))
    return d


db.Model.to_dict = to_dict


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    works: Mapped[List["Book"]] = relationship(back_populates="author")

    def __repr__(self):
        return f'<Author {self.first_name} {self.last_name}>'


class Book(db.Model):
    __tablename__ = 'books'
    serial_number = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey(Author.id))
    author: Mapped["Author"] = relationship(back_populates="works")
    borrowings: Mapped[List["Borrowing"]] = relationship(back_populates="book")
    deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Book {self.title}>'

    def is_available(self):
        return all(borrowing.return_date for borrowing in self.borrowings)

    def active_borrowing(self):
        borrowing = next(iter(borrowing for borrowing in self.borrowings if not borrowing.return_date), None)
        if not borrowing:
            return None
        return borrowing

    def to_dict(self):
        book_dict = {"serial_numer": self.serial_number, "title": self.title, "author": f"{self.author.first_name} {self.author.last_name}"}
        active_borrowing = self.active_borrowing()
        if active_borrowing:
            book_dict["available"] = False
            book_dict["borrowed_by"] = f"{active_borrowing.user}"
            book_dict["borrowed_on"] = f"{active_borrowing.borrow_date}"
        else:
            book_dict["available"] = True
        return book_dict


class LibraryUser(db.Model):
    __tablename__ = 'library_users'
    library_card = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    borrowed_books: Mapped[List["Borrowing"]] = relationship(back_populates="user")

    def __repr__(self):
        return f'<User {self.first_name} {self.last_name} {self.library_card}>'

    def to_dict(self):
        return {"library_card": self.library_card, "first_name": self.first_name, "last_name": self.last_name}


class Borrowing(db.Model):
    __tablename__ = 'books_users_association'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, ForeignKey("books.serial_number"))
    book: Mapped[Book] = relationship(back_populates="borrowings")
    user_id = db.Column(db.Integer, ForeignKey("library_users.library_card"))
    user: Mapped[LibraryUser] = relationship(back_populates="borrowed_books")
    borrow_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Borrowing book: {self.book_id} user: {self.user_id} borrow date: {self.borrow_date} return date: {self.return_date}>'

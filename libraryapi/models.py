from typing import List

from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import Mapped, relationship, mapped_column, DeclarativeBase

from . import db


def to_dict(self):
    """ Create a dictionary out of a model
    :param self:
    :return:
    """
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
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey(Author.id))
    author: Mapped["Author"] = relationship(back_populates="works")
    borrowings: Mapped[List["Borrowing"]] = relationship(back_populates="book")

    def __repr__(self):
        return f'<Book {self.title}>'

    def is_available(self):
        return all(borrowing.return_date for borrowing in self.borrowings)

    def to_dict(self):
        return {"serial_numer": self.serial_number, "title": self.title,
                "author": f"{self.author.first_name} {self.author.last_name}", "available": self.is_available()}


class LibraryUser(db.Model):
    __tablename__ = 'library_users'
    id = db.Column(db.Integer, primary_key=True)
    library_card = db.Column(db.Integer, unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    borrowed_books: Mapped[List["Borrowing"]] = relationship(back_populates="user")

    def __repr__(self):
        return f'<User {self.first_name} {self.last_name} {self.library_card}>'


class Borrowing(db.Model):
    __tablename__ = 'books_users_association'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, ForeignKey("books.id"))
    book: Mapped[Book] = relationship(back_populates="borrowings")
    user_id = db.Column(db.Integer, ForeignKey("library_users.id"))
    user: Mapped[LibraryUser] = relationship(back_populates="borrowed_books")
    borrow_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime, nullable=True)

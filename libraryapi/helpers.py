from flask import abort

from libraryapi.models import Book


def verify_number(expected_digits, **kwargs):
    """ Validate that string is a digit of {expected_digits} length
    :param expected_digits:
    :param kwargs: parameter name and its value
    """
    for key, value in kwargs.items():
        if len(value) != expected_digits or not value.isdigit():
            abort(415, description=f"{key} must be {expected_digits} digit long")


def verify_book_was_not_deleted(book: Book):
    if book.deleted:
        abort(404, description=f"Book {book} was removed!")


def strip_string_param(param_name, param):
    param = param.strip()
    if not param:
        abort(415, description=f"Param {param_name} must not be empty string or whitespace only!")
    return param

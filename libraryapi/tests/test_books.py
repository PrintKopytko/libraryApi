import random
import sys
import unittest
from urllib.parse import urlencode

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from flask_testing import TestCase
sys.path.append("../..")
from libraryapi import create_app, db


TEST_DB_NAME = 'test_library_db'


def check_if_database_exists(dbname, conn):
    cursor = conn.cursor()
    cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [dbname])
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists


def create_test_db_if_not_exists(dbname, conn):
    if not check_if_database_exists(dbname, conn):
        cursor = conn.cursor()
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(dbname)))


class MyTestCase(TestCase):

    TESTING = True

    def test_add_book(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, 200)
        # save a number of books before the test
        before_adding = len(response.json)

        book_nr = random.randint(100000, 999999)
        test_title = "testtitle"
        author_firstname = "John"
        author_lastname = "Doe"
        query_params = {"serial_number": book_nr, "title": test_title, "author_firstname": author_firstname, "author_lastname": author_lastname}
        url = '/api/books/?' + urlencode(query_params)
        created_book = self.client.post(url)
        self.assertEqual(created_book.status_code, 201)

        response = self.client.get("/api/books/")
        new_book = next(iter(book for book in response.json if book["serial_number"] == book_nr), None)
        self.assertEquals(new_book, {"author": f"{author_firstname} {author_lastname}", "available": True, "serial_number": book_nr, "title": test_title})
        self.assertEqual(len(response.json), before_adding + 1)

        # try to add the same book second time, should not succeed
        created_book = self.client.post(url)
        self.assertEqual(created_book.status_code, 409)

    def test_add_books_invalid_serial_number(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, 200)
        # save a number of books before the test
        before_adding = len(response.json)

        book_nr = "123"  # too short
        test_title = "testtitle"
        author_firstname = "John"
        author_lastname = "Doe"
        query_params = {"serial_number": book_nr, "title": test_title, "author_firstname": author_firstname,
                        "author_lastname": author_lastname}
        url = '/api/books/?' + urlencode(query_params)
        created_book = self.client.post(url)
        self.assertEqual(created_book.status_code, 415)

        # Too long
        query_params["serial_number"] = "1234567899999"
        url = '/api/books/?' + urlencode(query_params)
        created_book = self.client.post(url)
        self.assertEqual(created_book.status_code, 415)

        response = self.client.get("/api/books/")
        self.assertEqual(len(response.json), before_adding)  # number of books should be unchanged

    def create_app(self):
        db_connection = None
        try:
            db_connection = psycopg2.connect(dbname='postgres', user='bookworm', host='db', password='my-password')
            db_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            create_test_db_if_not_exists(TEST_DB_NAME, db_connection)
        finally:
            if db_connection:
                db_connection.close()
        # pass in test configuration
        return create_app(test=True)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        # self.remove_db(False)
        db.session.remove()


if __name__ == '__main__':
    unittest.main()

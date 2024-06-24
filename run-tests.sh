#!/bin/bash

pip install -r libraryapi/tests/requirements.txt
PYTHONPATH=. python libraryapi/tests/test_books.py

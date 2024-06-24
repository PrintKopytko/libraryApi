import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://bookworm:my-password@db:5432/library_db?client_encoding=utf8')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
                                        'postgresql://bookworm:my-password@db:5432/test_library_db?client_encoding=utf8')
# 📚 Library API 📚
API for a library written in Python
## Requirements
You have to install `docker` and `docker-compose` packages in your mac/linux OS.
## How to run API server
From the main directory of the repo run:
```Bash
docker-compose up
```

To seed sample data, open another console window and run:
```Bash
docker-compose exec api flask --app libraryapi books seed
```
it adds a few users, authors, books and borrowings to the database

### Debugging database
You can enter psql console by running
```commandline
docker-compose exec db psql --username=bookworm --dbname=library_db
```

## How to run the tests
You must run the API server first, then run in another console:
```Bash
docker-compose exec api ./run-tests.sh
```

## Endpoints Documentation
Base url for endpoints http://localhost:8000/api/

You can find API specification generated as swagger at http://localhost:8000/apidocs

## Local usage
Run the server from main directory
```commandline
DATABASE_URL=[database url] python -m libraryapi.app
```
where `[database url]` is a string containing connection parameters to your database like
`postgresql://username:my-password@localhost:5432/library_db`
You can also send requests to API using this swagger.

## Author & Chief Librarian
Patryk Kowalczyk

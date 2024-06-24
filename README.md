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
it will add a few users, authors, books and borrowings to the database

## How to run the tests
You must run the API server first, then run in another console:
```Bash
docker-compose exec api ./run-tests.sh
```

## Endpoints
Base url for endpoints is http://localhost:8000/api/

You can find API specification generated as swagger at http://localhost:8000/apidocs

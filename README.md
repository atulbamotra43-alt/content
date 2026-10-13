# Library Management API

This project includes a FastAPI REST API for the library management system.

## Run the API

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the development server:

```bash
uvicorn main:app --reload
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### Main endpoints

- `GET /books` — list books; use `?search=term` to filter
- `POST /books` — add a book
- `GET /books/{book_id}` — view one book
- `POST /books/{book_id}/issue` — issue a book
- `POST /books/{book_id}/return` — return a book
- `DELETE /books/{book_id}` — delete an available book
- `GET /statistics` — view library statistics

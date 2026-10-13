
import json
import os
from datetime import date

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

FILE_NAME = "library_data.json"

app = FastAPI(
    title="Library Management API",
    description="A REST API for managing library books.",
    version="1.0.0",
)


class BookCreate(BaseModel):
    """Request body for adding a book."""

    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)


class IssueRequest(BaseModel):
    """Request body for issuing a book."""

    student_name: str = Field(..., min_length=1)


def load_books():
    """Load books from the JSON file."""
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        print("Warning: Invalid library data.")
        return []

    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read the library file.")
        return []


def save_books(books):
    """Save books to the JSON file."""
    try:
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            json.dump(books, file, indent=4)
        return True

    except OSError:
        print("Error: Could not save library data.")
        return False


def find_book(books, book_id):
    """Find a book by ID."""
    return next((book for book in books if book.get("id") == book_id), None)


@app.get("/", tags=["General"])
def root():
    """Return basic API information."""
    return {"message": "Library Management API", "docs": "/docs"}


@app.get("/books", tags=["Books"])
def get_books(search: str | None = Query(default=None, description="Search by title or author")):
    """Return all books, optionally filtered by title or author."""
    books = load_books()

    if search:
        query = search.strip().lower()
        books = [
            book for book in books
            if query in book["title"].lower()
            or query in book["author"].lower()
        ]

    return books


@app.get("/books/{book_id}", tags=["Books"])
def get_book(book_id: int):
    book = find_book(load_books(), book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books", status_code=201, tags=["Books"])
def create_book(book_data: BookCreate):
    books = load_books()
    book_id = max((book.get("id", 0) for book in books), default=0) + 1
    book = {
        "id": book_id,
        "title": book_data.title.strip(),
        "author": book_data.author.strip(),
        "issued": False,
        "issued_to": "",
        "issue_date": "",
    }

    if not book["title"] or not book["author"]:
        raise HTTPException(status_code=422, detail="Title and author cannot be empty")

    books.append(book)
    if not save_books(books):
        raise HTTPException(status_code=500, detail="Could not save library data")
    return book


@app.post("/books/{book_id}/issue", tags=["Books"])
def issue_book_api(book_id: int, issue_data: IssueRequest):
    books = load_books()
    book = find_book(books, book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if book["issued"]:
        raise HTTPException(status_code=409, detail="This book is already issued")

    student_name = issue_data.student_name.strip()
    if not student_name:
        raise HTTPException(status_code=422, detail="Student name cannot be empty")

    book["issued"] = True
    book["issued_to"] = student_name
    book["issue_date"] = date.today().isoformat()

    if not save_books(books):
        raise HTTPException(status_code=500, detail="Could not save library data")
    return book


@app.post("/books/{book_id}/return", tags=["Books"])
def return_book_api(book_id: int):
    books = load_books()
    book = find_book(books, book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book["issued"]:
        raise HTTPException(status_code=409, detail="This book is not currently issued")

    book["issued"] = False
    book["issued_to"] = ""
    book["issue_date"] = ""

    if not save_books(books):
        raise HTTPException(status_code=500, detail="Could not save library data")
    return book


@app.delete("/books/{book_id}", tags=["Books"])
def delete_book_api(book_id: int):
    books = load_books()
    book = find_book(books, book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if book["issued"]:
        raise HTTPException(status_code=409, detail="Return this book before deleting it")

    books.remove(book)
    if not save_books(books):
        raise HTTPException(status_code=500, detail="Could not save library data")
    return {"message": "Book deleted successfully", "book_id": book_id}


@app.get("/statistics", tags=["General"])
def statistics():
    books = load_books()
    issued = sum(1 for book in books if book["issued"])
    return {
        "total_books": len(books),
        "available_books": len(books) - issued,
        "issued_books": issued,
    }


def add_book(books):
    """Add a new book to the library."""
    title = input("Enter book title: ").strip()
    author = input("Enter author name: ").strip()

    if not title or not author:
        print("Title and author cannot be empty.")
        return

    book_id = max(
        (book.get("id", 0) for book in books),
        default=0
    ) + 1

    book = {
        "id": book_id,
        "title": title,
        "author": author,
        "issued": False,
        "issued_to": "",
        "issue_date": ""
    }

    books.append(book)

    if save_books(books):
        print(f"Book added successfully! Book ID: {book_id}")
    else:
        books.remove(book)


def view_books(books):
    """Display all books."""
    if not books:
        print("\nNo books available.")
        return

    print("\n========== BOOK LIST ==========")

    for book in books:
        status = "Issued" if book["issued"] else "Available"

        print(f"\nID: {book['id']}")
        print(f"Title: {book['title']}")
        print(f"Author: {book['author']}")
        print(f"Status: {status}")

        if book["issued"]:
            print(f"Issued to: {book['issued_to']}")
            print(f"Issue date: {book['issue_date']}")


def search_book(books):
    """Search books by title or author."""
    query = input("Enter title or author to search: ").strip().lower()

    if not query:
        print("Please enter a search term.")
        return

    results = [
        book for book in books
        if query in book["title"].lower()
        or query in book["author"].lower()
    ]

    if not results:
        print("No matching books found.")
        return

    print("\nSearch results:")

    for book in results:
        print(
            f"ID: {book['id']} | "
            f"Title: {book['title']} | "
            f"Author: {book['author']}"
        )


def issue_book(books):
    """Issue an available book to a person."""
    try:
        book_id = int(input("Enter book ID to issue: "))
    except ValueError:
        print("Please enter a valid numeric ID.")
        return

    book = next(
        (item for item in books if item["id"] == book_id),
        None
    )

    if book is None:
        print("Book not found.")
        return

    if book["issued"]:
        print("This book is already issued.")
        return

    person = input("Enter student name: ").strip()

    if not person:
        print("Student name cannot be empty.")
        return

    book["issued"] = True
    book["issued_to"] = person
    book["issue_date"] = date.today().isoformat()

    if save_books(books):
        print(f"'{book['title']}' issued to {person}.")
    else:
        book["issued"] = False
        book["issued_to"] = ""
        book["issue_date"] = ""


def return_book(books):
    """Return an issued book."""
    try:
        book_id = int(input("Enter book ID to return: "))
    except ValueError:
        print("Please enter a valid numeric ID.")
        return

    book = next(
        (item for item in books if item["id"] == book_id),
        None
    )

    if book is None:
        print("Book not found.")
        return

    if not book["issued"]:
        print("This book is not currently issued.")
        return

    previous_person = book["issued_to"]

    book["issued"] = False
    book["issued_to"] = ""
    book["issue_date"] = ""

    if save_books(books):
        print(
            f"'{book['title']}' returned successfully "
            f"by {previous_person}."
        )
    else:
        book["issued"] = True
        book["issued_to"] = previous_person


def delete_book(books):
    """Delete a book that is not currently issued."""
    try:
        book_id = int(input("Enter book ID to delete: "))
    except ValueError:
        print("Please enter a valid numeric ID.")
        return

    book = next(
        (item for item in books if item["id"] == book_id),
        None
    )

    if book is None:
        print("Book not found.")
        return

    if book["issued"]:
        print("Return this book before deleting it.")
        return

    books.remove(book)

    if save_books(books):
        print("Book deleted successfully.")
    else:
        books.append(book)


def show_statistics(books):
    """Display library statistics."""
    total = len(books)
    issued = sum(1 for book in books if book["issued"])
    available = total - issued

    print("\n======= LIBRARY STATISTICS =======")
    print(f"Total books: {total}")
    print(f"Available books: {available}")
    print(f"Issued books: {issued}")


def main():
    """Run the library management application."""
    books = load_books()

    while True:
        print("\n======= LIBRARY MANAGEMENT =======")
        
        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            add_book(books)
        elif choice == "2":
            view_books(books)
        elif choice == "3":
            search_book(books)
        elif choice == "4":
            issue_book(books)
        elif choice == "5":
            return_book(books)
        elif choice == "6":
            delete_book(books)
        elif choice == "7":
            show_statistics(books)
        

if __name__ == "__main__":
    main()


import json
import os
from datetime import date

FILE_NAME = "library_data.json"


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

# content reviewer notes

## Architecture
This is a small, single-file, interactive command-line library management application (`main.py`). Book records are kept as dictionaries in a JSON array stored in `library_data.json`; `main()` loads that array, dispatches menu choices, and passes the in-memory list to operation functions. Persistence is handled centrally through `load_books()` and `save_books()`.

## Conventions
- Keep user-facing operations as separate functions accepting the shared `books` list: `add_book`, `view_books`, `search_book`, `issue_book`, `return_book`, `delete_book`, and `show_statistics` in `main.py`.
- Use the established book schema: `id`, `title`, `author`, `issued`, `issued_to`, and `issue_date` (`main.py`, `add_book()`).
- IDs are positive integers generated as one greater than the current maximum, using `max(..., default=0) + 1`; do not derive IDs from list indexes (`main.py`, `add_book()`).
- Normalize interactive text with `.strip()`, reject empty required values, and report validation failures with `print()` before returning (`add_book()`, `issue_book()`, `search_book()`).
- Persist changes through `save_books(books)`. Mutating operations optimistically update the in-memory list/object and explicitly roll back the mutation if saving fails (`add_book()`, `issue_book()`, `return_book()`, `delete_book()`).
- Dates are stored as ISO-formatted calendar dates from `date.today().isoformat()` (`issue_book()`), not timestamps.
- File I/O uses UTF-8 and JSON indentation of four spaces (`load_books()` and `save_books()`).
- The program is intentionally procedural: menu dispatch uses an `if`/`elif` chain in `main()` rather than a command registry or class-based model.

## Intentional non-standard choices
- Missing, malformed, unreadable, or non-list JSON data is treated as an empty library, with a warning printed rather than an exception propagated (`load_books()`).
- There is no separate database, service layer, or validation/model class; the JSON dictionaries are the persistence and domain representation.
- The application is fully terminal-driven: `input()` and `print()` are used directly inside business-operation functions.

## Watch out for
- Changes to the book schema must be reflected in every reader, especially direct indexing such as `book["issued"]`, `book["title"]`, and `book["author"]`; malformed individual records can currently raise `KeyError`.
- Any new mutation must preserve the existing rollback behavior when `save_books()` returns `False`; otherwise the in-memory state can diverge from `library_data.json`.
- Do not allow deletion of issued books; this invariant is enforced in `delete_book()`.
- Preserve issue-state consistency: issuing sets all three fields (`issued`, `issued_to`, `issue_date`), while returning clears them. Returning currently restores `issued` and `issued_to` on save failure, so changes must also restore `issue_date`.
- Be cautious with ID generation when importing or editing records: the current strategy assumes numeric IDs and uses the maximum existing value.
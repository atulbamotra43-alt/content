# content reviewer notes

## Architecture

This repository is intended to be a FastAPI library-management REST API, with endpoints documented in `README.md` and behavior tested through `TestClient` in `test_main.py`. The sampled `main.py`, however, currently implements only an interactive CLI backed by `library_data.json`; it does not define `app` or any REST routes, so it is inconsistent with the README and tests. Persistence is file-based JSON rather than database-backed.

## Conventions

- Book records use the fields `id`, `title`, `author`, `issued`, `issued_to`, and `issue_date`; see `main.py:add_book`.
- IDs are generated as one greater than the current maximum, defaulting to `1` for an empty library (`main.py:add_book`). Preserve this API behavior unless requirements explicitly change.
- Issue dates are stored as ISO-formatted calendar dates using `date.today().isoformat()` (`main.py:issue_book`).
- Searches are case-insensitive and match either title or author (`main.py:search_book`); the API tests expect `GET /books?search=tolkien` to find authors case-insensitively (`test_main.py:test_create_and_search_book`).
- Mutations persist immediately through `save_books(books)`. Failed writes must restore the in-memory mutation: issue/return revert fields, while delete re-adds the removed record (`main.py:issue_book`, `return_book`, `delete_book`).
- The documented API contract uses HTTP semantics: create returns `201`, missing books return `404`, and deleting an issued book returns `409` with detail `"Return this book before deleting it"` (`README.md`, `test_main.py`).
- Tests isolate persistence by monkeypatching `main.FILE_NAME` to a `tmp_path` file (`test_main.py:client`); avoid hard-coding a data path that bypasses this seam.

## Intentional non-standard choices

- JSON-file persistence and graceful fallback to an empty library on missing, malformed, or unreadable data are intentional in `main.py:load_books`; do not require a database without a stated architectural change.
- Deleting issued books is deliberately forbidden, and returning a book clears `issued_to` and `issue_date` (`main.py:delete_book`, `return_book`).

## Watch out for

- The current sampled implementation is not runnable as the documented API: `test_main.py` requires `main.app`, while `main.py` defines only CLI functions and `main()`. Treat restoration or implementation of the FastAPI app and all README routes as a high-priority issue.
- Do not remove the `if __name__ == "__main__": main()` guard or accidentally trigger interactive `input()` calls during API imports/tests.
- Validate malformed JSON structures and missing record fields before indexing them; current display/search/statistics code assumes valid book dictionaries.
- Preserve state rollback when `save_books` fails; otherwise failed requests can leave memory inconsistent with `library_data.json`.

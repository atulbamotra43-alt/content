# content reviewer notes

## Architecture

This repository is intended to be a FastAPI library-management REST API, with endpoints documented in `README.md` and exercised through `TestClient` in `test_main.py`. The supplied `main.py`, however, currently implements only an interactive CLI backed by `library_data.json`; it defines no `app` object or REST routes. Data is represented as mutable book dictionaries and persisted to a local JSON file.

## Conventions

- Book records use the fields `id`, `title`, `author`, `issued`, `issued_to`, and `issue_date`; this shape is established in `main.py:add_book`.
- IDs are generated as one greater than the maximum existing ID, defaulting to `1` for an empty collection (`main.py:add_book`).
- Dates are stored as ISO strings from `date.today().isoformat()` (`main.py:issue_book`).
- Persistence is file-based through the module-level `FILE_NAME = "library_data.json"` and the `load_books`/`save_books` helpers (`main.py`).
- File and JSON read failures are handled by returning an empty list and printing warnings (`main.py:load_books`); save failures return `False`.
- Mutating operations roll back their in-memory changes when saving fails, including issue, return, and delete (`main.py:issue_book`, `return_book`, and `delete_book`).
- API behavior expected by the tests includes `201` for book creation, `404` for missing books, `409` when deleting an issued book, and exact statistics keys (`test_main.py`).
- Tests isolate storage by monkeypatching `main.FILE_NAME` to a `tmp_path` file (`test_main.py:client`).

## Intentional non-standard choices

- The implementation uses a JSON file rather than a database or ORM (`main.py:FILE_NAME`, `load_books`, `save_books`); preserve this unless the task explicitly changes the persistence layer.
- Book state is represented with an `issued` boolean plus empty-string fields for unavailable metadata, rather than nullable fields (`main.py:add_book`, `return_book`).
- The code deliberately prints user-facing warnings/errors and uses empty-list fallback behavior for malformed or missing data (`main.py:load_books`).

## Watch out for

- Do not treat the current `main.py` as satisfying the documented API: `test_main.py` requires `main.app`, while the shown file has only CLI functions and `main()`. Changes should reconcile this mismatch rather than merely adding unrelated CLI behavior.
- Preserve endpoint contracts from `README.md` and `test_main.py`, especially request field `student_name`, response status codes, and exact `/statistics` response keys.
- Avoid deleting issued books; the expected API response is `409` with detail `"Return this book before deleting it"` (`test_main.py:test_cannot_delete_issued_book`).
- Ensure failed writes do not leave partially updated book state; existing CLI logic explicitly restores prior state after `save_books` failure.
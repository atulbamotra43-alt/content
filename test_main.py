"""Tests for the Library Management FastAPI application."""

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Use a temporary data file for every test."""
    monkeypatch.setattr(main, "FILE_NAME", str(tmp_path / "library_data.json"))
    return TestClient(main.app)


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Library Management API"


def test_create_and_search_book(client):
    create_response = client.post(
        "/books",
        json={"title": "The Hobbit", "author": "J. R. R. Tolkien"},
    )

    assert create_response.status_code == 201
    assert create_response.json()["id"] == 1

    search_response = client.get("/books?search=tolkien")

    assert search_response.status_code == 200
    assert len(search_response.json()) == 1
    assert search_response.json()[0]["title"] == "The Hobbit"


def test_issue_and_return_book(client):
    client.post("/books", json={"title": "1984", "author": "George Orwell"})

    issue_response = client.post(
        "/books/1/issue",
        json={"student_name": "Alex"},
    )
    assert issue_response.status_code == 200
    assert issue_response.json()["issued"] is True
    assert issue_response.json()["issued_to"] == "Alex"

    return_response = client.post("/books/1/return")
    assert return_response.status_code == 200
    assert return_response.json()["issued"] is False


def test_delete_and_statistics(client):
    client.post("/books", json={"title": "Dune", "author": "Frank Herbert"})

    statistics_response = client.get("/statistics")
    assert statistics_response.json() == {
        "total_books": 1,
        "available_books": 1,
        "issued_books": 0,
    }

    delete_response = client.delete("/books/1")
    assert delete_response.status_code == 200
    assert client.get("/books/1").status_code == 404


def test_cannot_delete_issued_book(client):
    client.post("/books", json={"title": "Dune", "author": "Frank Herbert"})
    client.post("/books/1/issue", json={"student_name": "Sam"})

    response = client.delete("/books/1")

    assert response.status_code == 409
    assert response.json()["detail"] == "Return this book before deleting it"

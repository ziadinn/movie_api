from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_line_by_id():
    response = client.get("/lines/9999")
    assert response.status_code == 200

    with open("test/lines/9999.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_bad_line():
    response = client.get("/lines/99990")
    assert response.status_code == 404

    with open("test/lines/error.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_lines():
    response = client.get("/lines/")
    assert response.status_code == 200

    with open("test/lines/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_lines_by_name():
    response = client.get("/lines/?name=bianca")
    assert response.status_code == 200

    with open("test/lines/bianca.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_conversations():
    response = client.get("/conversations/")
    assert response.status_code == 200

    with open("test/lines/conversations.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)
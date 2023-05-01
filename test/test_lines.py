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

# def test_basic_post():
#     data = {
#         "character_1_id": 0,
#         "character_2_id": 1,
#         "lines": [{"character_id": 0, "line_text": "testing this string"}],
#     }

#     postResponse = client.post("/movies/0/conversations/", json=data)
#     assert postResponse.status_code == 200
#     assert "conversation_id" in postResponse.json()
#     assert postResponse.json()["conversation_id"] > 83073
    
# def test_error_post():
#     data = {
#         "character_1_id": 0,
#         "character_2_id": 0,
#         "lines": [{"character_id": 1, "line_text": "testing this string"}],
#     }
    
#     postResponse = client.post("/movies/0/conversations/", json=data)
#     assert postResponse.status_code == 400


# def test_more_post():
#     data = {
#         "character_1_id": 9021,
#         "character_2_id": 9024,
#         "lines": [
#             {"character_id": 9021, "line_text": "Hi, I am talking to you"},
#             {"character_id": 9024, "line_text": "Yes, you are talking right now"},
#             {"character_id": 9021, "line_text": "This should be my second custom line"},
#             {"character_id": 9024, "line_text": "And this is my last"},
#         ],
#     }

#     preMaitreLines = client.get("/lines/?character=MAITRE D'")
#     preOldVioLines = client.get("/lines/?character=OLD VIOLINIST")
#     with open("test/lines/maitre_pre.json", encoding="utf-8") as f:
#         assert preMaitreLines.json() == json.load(f)
#     with open("test/lines/oldViolinist_pre.json", encoding="utf-8") as f:
#         assert preOldVioLines.json() == json.load(f)

#     basicPostResponse = client.post("/movies/615/conversations/", json=data)
#     with open("test/lines/morePostResponse.json", encoding="utf-8") as f:
#         assert basicPostResponse.json() == json.load(f)

#     postMaitreLines = client.get("/lines/?character=MAITRE D'")
#     postOldVioLines = client.get("/lines/?character=OLD VIOLINIST")
#     with open("test/lines/maitre_post.json", encoding="utf-8") as f:
#         assert postMaitreLines.json() == json.load(f)
#     with open("test/lines/oldViolinist_post.json", encoding="utf-8") as f:
#         assert postOldVioLines.json() == json.load(f)

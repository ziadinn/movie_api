from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
from src.datatypes import Conversation, Line
import sqlalchemy
import dotenv
import os

router = APIRouter()

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("DB_USER")
    DB_PASSWD = os.environ.get("DB_PASSWD")
    DB_SERVER: str = os.environ.get("DB_SERVER")
    DB_PORT: str = os.environ.get("DB_PORT")
    DB_NAME: str = os.environ.get("DB_NAME")
    print('>>>: ' + f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

engine = sqlalchemy.create_engine(database_connection_url())
conn = engine.connect()

# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()

def verifyConversation(movieId, conversation):
    errors = []
    if conversation.character_1_id == conversation.character_2_id:
        errors.append("Characters cannot be the same")
    character_1 = db.characters.get(conversation.character_1_id)
    character_2 = db.characters.get(conversation.character_2_id)
    if character_1.movie_id != character_2.movie_id:
        errors.append("Characters must be in the same movie")
    if character_1.movie_id != movieId:
        errors.append("Characters 1 must be in the movie")
    if character_2.movie_id != movieId:
        errors.append("Characters 2 must be in the movie")
    if errors:
        raise HTTPException(status_code=400, detail=errors)

@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """
    verifyConversation(movie_id, conversation)
    character_ids = [conversation.character_1_id, conversation.character_2_id]
    lines = conversation.lines
    current_conversation_id = conn.execute(
        sqlalchemy.text("SELECT conversation_id FROM conversation ORDER BY conversation_id DESC LIMIT 1")
    ).fetchone()[0] + 1
    current_line_id = conn.execute(
        sqlalchemy.text("SELECT line_id FROM lines ORDER BY line_id DESC LIMIT 1")
    ).fetchone()[0] + 1
    validLines = []
    for i, line in enumerate(lines):
        if line.character_id not in character_ids:
            raise HTTPException(status_code=400, detail=["Character id does not match"])
        validLines.append(Line(
            int(current_line_id),
            int(line.character_id),
            int(movie_id),
            int(current_conversation_id),
            int(i),
            line.line_text,
        ))
        current_line_id += 1
    for validLine in validLines:
        conn.execute(
            sqlalchemy.text("INSERT INTO lines VALUES (:id, :c_id, :movie_id, :conv_id, :line_sort, :line_text)"),
            [{"id": validLine.id, "c_id": validLine.c_id, "movie_id": validLine.movie_id, "conv_id": validLine.conv_id, "line_sort": validLine.line_sort, "line_text": validLine.line_text}]
        )
    conn.execute(
        sqlalchemy.text("INSERT INTO conversation VALUES (:id, :c1_id, :c2_id, :movie_id)"),
        [{"id": current_conversation_id, "c1_id": conversation.character_1_id, "c2_id": conversation.character_2_id, "movie_id": movie_id}]
    )
    conn.commit()
    return {"conversation_id": current_conversation_id}

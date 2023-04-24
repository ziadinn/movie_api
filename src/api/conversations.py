from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
from src.datatypes import Conversation, Line


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

    # TODO: Remove the following two lines. This is just a placeholder to show
    # how you could implement persistent storage.

    verifyConversation(movie_id, conversation)
    character_ids = [conversation.character_1_id, conversation.character_2_id]
    lines = conversation.lines
    current_conversation_id = max(db.conversations.keys()) + 1
    current_line_id = max(db.lines.keys()) + 1

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
        db.lines[validLine.id] = validLine
    db.conversations[current_conversation_id] = Conversation(
        int(current_conversation_id),
        int(conversation.character_1_id),
        int(conversation.character_2_id),
        int(movie_id),
        len(validLines),
    )
    db.logs.append({"post_call_time": datetime.now(), "movie_id_added_to": movie_id})
    db.upload_new_log()
    return {"conversation_id": current_conversation_id}

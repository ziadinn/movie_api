from fastapi import APIRouter, HTTPException
from src import database as db

router = APIRouter()


def getConversationData(conversation_id, character_id):
    if conversation_id not in db.conversations:
        raise HTTPException(status_code=404, detail="conversation not found.")
    conversation = db.conversations.get(conversation_id)
    character1 = db.characters.get(conversation.c1_id)
    character2 = db.characters.get(conversation.c2_id)
    otherChar = character1 if character2.id == character_id else character2
    return {
        "speaker": db.characters.get(character_id).name,
        "listener": otherChar.name,
    }

@router.get("/lines/{id}", tags=["lines"])
def get_line(id: str):
    """
    This endpoint returns a single line by its identifier. For each line it returns:
    * `line_id`: the internal id of the line. Can be used to query the
        `/lines/{line_id}` endpoint.
    * `character_id`: the internal id of the character. Can be used to query the
        `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie_id`: the internal id of the movie. Can be used to query the
        `/movies/{movie_id}` endpoint.
    * `movie`: The title of the movie.
    * `line_text`: The text of the line.
    * `conversation`: A dictionary describing the conversation the line is part of.
    
    The conversation is represented by a dictionary with the following keys:
    * `speaker`: The name of the character that speaks the line.
    * `listener`: The name of the character that listens to the line.
    """
    id = int(id)
    if id not in db.lines:
        raise HTTPException(status_code=404, detail="line not found.")
    line = db.lines.get(id)
    conversation_id = line.conv_id
    char_id = line.c_id
    return {
        "line_id": int(id),
        "character_id": int(line.c_id),
        "character": db.characters.get(line.c_id).name,
        "movie_id": int(line.movie_id),
        "movie": db.movies.get(line.movie_id).title,
        "line_text": line.line_text,
        "conversation": getConversationData(conversation_id, char_id),
    }

@router.get("/lines/", tags=["lines"])
def list_lines(
    character: str = "",
    limit: int = 50,
    offset: int = 0,
):
    """
    This endpoint returns a list of lines. For each line it returns:
    * `line_id`: the internal id of the line. Can be used to query the
        `/lines/{line_id}` endpoint.
    * `character_id`: the internal id of the character. Can be used to query the
        `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie_id`: the internal id of the movie. Can be used to query the
        `/movies/{movie_id}` endpoint.
    * `movie`: The title of the movie.
    * `line_text`: The text of the line.
    * `conversation`: A dictionary describing the conversation the line is part of.

    The conversation is represented by a dictionary with the following keys:
    * `speaker`: The name of the character that speaks the line.
    * `listener`: The name of the character that listens to the line.
    """
    json = []
    for lineId in db.lines:
        line = db.lines.get(lineId)
        if (not character or
            db.characters.get(line.c_id).name.lower() == character.lower()):
            conversation_id = line.conv_id
            char_id = line.c_id
            json.append({
                "line_id": int(lineId),
                "character_id": int(char_id),
                "character": db.characters.get(char_id).name,
                "movie_id": int(line.movie_id),
                "movie": db.movies.get(line.movie_id).title,
                "line_text": line.line_text,
                "conversation": getConversationData(conversation_id, char_id),
            })
    return json[offset:offset+limit]

@router.get("/conversations/{id}", tags=["lines"])
def get_convo(id: str):
    id = int(id)
    if id not in db.conversations:
        raise HTTPException(status_code=404, detail="conversation not found.")
    conversation = db.conversations.get(id)
    return {
        "conversation_id": int(id),
        "character1_id": int(conversation.c1_id),
        "character1": db.characters.get(conversation.c1_id).name,
        "character2_id": int(conversation.c2_id),
        "character2": db.characters.get(conversation.c2_id).name,
        "movie_id": int(conversation.movie_id),
        "movie": db.movies.get(conversation.movie_id).title,
    }

@router.get("/conversations/", tags=["lines"])
def list_conversations(
    limit: int = 50,
    offset: int = 0,
):
    """
    This endpoint returns a list of conversations. For each conversation it returns:
    * `conversation_id`: the internal id of the conversation. Can be used to query the
        `/conversations/{conversation_id}` endpoint.
    * `speaker`: The name of the character that speaks the line.
    * `listener`: The name of the character that listens to the line.
    * `movie`: The title of the movie.
    """
    json = []
    for conversationId in db.conversations:
        conversation = db.conversations.get(conversationId)
        character = db.characters.get(conversation.c1_id)
        otherChar = db.characters.get(conversation.c2_id)
        json.append({
            "conversation_id": int(conversationId),
            "speaker": character.name,
            "listener": otherChar.name,
            "movie": db.movies.get(conversation.movie_id).title,
        })
    return json[offset:offset+limit]

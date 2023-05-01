from fastapi import APIRouter, HTTPException
from src import database as db
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

router = APIRouter()


def getConversationData(conversation_id, character_id):
    conv_res = conn.execute(
        sqlalchemy.text('''
            SELECT *
            FROM conversation
            WHERE conversation_id = :conv_id
        '''),
        [{"conv_id": conversation_id}]
    )
    if conv_res.rowcount == 0:
        raise HTTPException(status_code=404, detail="conversation not found.")
    conversation = conv_res.fetchone()
    character1 = conversation[1]
    char1_data = conn.execute(
        sqlalchemy.text('''
            SELECT *
            FROM characters
            WHERE character_id = :character_id
        '''),
        [{"character_id": character1}]
    )
    character2 = conversation[2]
    char2_data = conn.execute(
        sqlalchemy.text('''
            SELECT *
            FROM characters
            WHERE character_id = :character_id
        '''),
        [{"character_id": character2}]
    )
    speaker_data = char1_data.fetchone() if character_id == character1 else char2_data.fetchone()
    listender_data = char2_data.fetchone() if character_id == character1 else char1_data.fetchone()
    return {
        "speaker": speaker_data[1],
        "listener": listender_data[1],
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
    # id = int(id)
    # if id not in db.lines:
    #     raise HTTPException(status_code=404, detail="line not found.")
    # line = db.lines.get(id)
    # conversation_id = line.conv_id
    # char_id = line.c_id
    # return {
    #     "line_id": int(id),
    #     "character_id": int(line.c_id),
    #     "character": db.characters.get(line.c_id).name,
    #     "movie_id": int(line.movie_id),
    #     "movie": db.movies.get(line.movie_id).title,
    #     "line_text": line.line_text,
    #     "conversation": getConversationData(conversation_id, char_id),
    # }
    result = conn.execute(
        sqlalchemy.text('''
            SELECT *
            FROM lines
            WHERE line_id = :line_id
        '''),
        [{"line_id": id}]
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="line not found.")
    line = result.fetchone()
    # line headers: line_id,character_id,movie_id,conversation_id,line_sort,line_text

    conversation_id = line[3]

    movie_id = line[2]
    movie_result = conn.execute(
        sqlalchemy.text('''
            SELECT *
            FROM movies
            WHERE movie_id = :movie_id
        '''),
        [{"movie_id": movie_id}]
    )
    movie = movie_result.fetchone()

    char_id = line[1]
    char_result = conn.execute(
        sqlalchemy.text('''
            SELECT *
            FROM characters
            WHERE character_id = :character_id
        '''),
        [{"character_id": char_id}]
    )
    char = char_result.fetchone()

    return {
        "line_id": int(id),
        "character_id": int(char_id),
        "character": char[1],
        "movie_id": int(movie_id),
        "movie": movie[1],
        "line_text": line[5],
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
    # json = []
    # for lineId in db.lines:
    #     line = db.lines.get(lineId)
    #     if (not character or
    #         db.characters.get(line.c_id).name.lower() == character.lower()):
    #         conversation_id = line.conv_id
    #         char_id = line.c_id
    #         json.append({
    #             "line_id": int(lineId),
    #             "character_id": int(char_id),
    #             "character": db.characters.get(char_id).name,
    #             "movie_id": int(line.movie_id),
    #             "movie": db.movies.get(line.movie_id).title,
    #             "line_text": line.line_text,
    #             "conversation": getConversationData(conversation_id, char_id),
    #         })
    # return json[offset:offset+limit]
    result = conn.execute(
        sqlalchemy.text('''
            SELECT *
            FROM lines
            WHERE line_text LIKE :character
            LIMIT :limit
            OFFSET :offset
        '''),
        [{"character": "%" + character + "%", "limit": limit, "offset": offset}]
    )
    json = []
    for line in result:
        conversation_id = line[3]

        movie_id = line[2]
        movie_result = conn.execute(
            sqlalchemy.text('''
                SELECT *
                FROM movies
                WHERE movie_id = :movie_id
            '''),
            [{"movie_id": movie_id}]
        )
        movie = movie_result.fetchone()

        char_id = line[1]
        char_result = conn.execute(
            sqlalchemy.text('''
                SELECT *
                FROM characters
                WHERE character_id = :character_id
            '''),
            [{"character_id": char_id}]
        )
        char = char_result.fetchone()

        json.append({
            "line_id": int(line[0]),
            "character_id": int(char_id),
            "character": char[1],
            "movie_id": int(movie_id),
            "movie": movie[1],
            "line_text": line[5],
            "conversation": getConversationData(conversation_id, char_id),
        })
    return json

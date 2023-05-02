from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db
import os
import dotenv
import sqlalchemy

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

def get_top_conv_characters(c_id, movie_id):
    conversations_results = conn.execute(
        sqlalchemy.text("SELECT * FROM conversation WHERE (character1_id = :c_id OR character2_id = :c_id) AND movie_id = :movie_id"),
        [{"c_id": c_id, "movie_id": str(movie_id)}]
    )
    # Headers = conversation_id,character1_id,character2_id,movie_id
    convos_with_char = {}
    for conv in conversations_results:
        convos_with_char[conv[0]] = conv[1] if conv[1] != c_id else conv[2]
    lines_results = conn.execute(
        sqlalchemy.text("SELECT * FROM lines WHERE movie_id = :movie_id"),
        [{"movie_id": movie_id}]
    )
    counter = Counter()
    # headers: line_id,character_id,movie_id,conversation_id,line_sort,line_text
    for line in lines_results:
        if line[3] in convos_with_char:
            otherChar = line[1] if line[1] != c_id else convos_with_char[line[3]]
            counter[otherChar] += 1
    return counter.most_common()


@router.get("/characters/{id}", tags=["characters"])
def get_character(id: int):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """
    result = conn.execute(
        sqlalchemy.text("SELECT * FROM characters WHERE character_id = :id"),
        [{"id": id}]
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="character not found.")
    character = result.first()
    movie_id = character[2]
    movie_result = conn.execute(
        sqlalchemy.text("SELECT * FROM movies WHERE movie_id = :movie_id"),
        [{"movie_id": movie_id}]
    )
    movie = movie_result.first()
    top_convos = []
    for other_id, lines in get_top_conv_characters(character[0], movie_id):
        res_char = conn.execute(
            sqlalchemy.text("SELECT * FROM characters WHERE character_id = :other_id"),
            [{"other_id": other_id}]
        )
        other_char = res_char.first()
        top_convos.append({
            "character_id": other_id,
            "character": other_char[1],
            "gender": other_char[3],
            "number_of_lines_together": lines,
        })
    return {
        "character_id": character[0],
        "character": character[1],
        "movie": movie[1],
        "gender": character[3],
        "top_conversations": top_convos,
    }


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    col_name_sort = ""
    if sort == character_sort_options.character:
        col_name_sort = "name"
    elif sort == character_sort_options.movie:
        col_name_sort = "title"
    elif sort == character_sort_options.number_of_lines:
        col_name_sort = "number_of_lines"

    result = conn.execute(
        sqlalchemy.text(f'''
            SELECT characters.*, movies.title, lines.number_of_lines FROM characters
            INNER JOIN movies ON characters.movie_id = movies.movie_id
            INNER JOIN (
                SELECT character_id, COUNT(*) AS number_of_lines FROM lines
                GROUP BY character_id
            ) AS lines ON characters.character_id = lines.character_id
            WHERE LOWER(name) LIKE LOWER(:name)
            ORDER BY {col_name_sort} {"DESC" if col_name_sort == "number_of_lines" else "ASC"}, character_id ASC
            LIMIT :limit
            OFFSET :offset
        '''),
        [{"name": f"%{name}%", "limit": limit, "offset": offset}]
    )
    characters = []
    for row in result:
        character_id, name, _, _, _, movie_title, number_of_lines = row
        characters.append({
            "character_id": character_id,
            "character": name,
            "movie": movie_title,
            "number_of_lines": number_of_lines
        })
    return characters

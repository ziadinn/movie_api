from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query
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

@router.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: int):
    """
    This endpoint returns a single movie by its identifier. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `top_characters`: A list of characters that are in the movie. The characters
    are ordered by the number of lines they have in the movie. The top five
      characters are listed.

    Each character is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `num_lines`: The number of lines the character has in the movie.

    """
    result = conn.execute(
        sqlalchemy.text("SELECT * FROM movies WHERE movie_id = :movie_id"),
        [{"movie_id": movie_id}]
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="movie not found.")
    
    movie = result.fetchone()
    conversations = conn.execute(
        sqlalchemy.text('''
            SELECT character_id, COUNT(*) AS line_count 
            FROM lines
            WHERE movie_id = :movie_id
            GROUP BY character_id
            ORDER BY line_count DESC
            LIMIT 5
        '''),
        [{"movie_id": movie_id}]
    )
    top_characters = []
    for row in conversations:
        res_char = conn.execute(
            sqlalchemy.text('''
                SELECT * FROM characters
                WHERE character_id = :character_id
            '''),
            [{"character_id": row[0]}]
        )
        character = res_char.fetchone()
        top_characters.append({
            "character_id": character[0],
            "character": character[1],
            "num_lines": row[1]
        })
    
    return {
        "movie_id": movie[0],
        "title": movie[1],
        "top_characters": [
            {
                "character_id": c["character_id"],
                "character": c["character"],
                "num_lines": c["num_lines"]
            } for c in top_characters
        ]
    }


class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/movies/", tags=["movies"])
def list_movies(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: movie_sort_options = movie_sort_options.movie_title,
):
    """
    This endpoint returns a list of movies. For each movie it returns:
    * `movie_id`: the internal id of the movie. Can be used to query the
      `/movies/{movie_id}` endpoint.
    * `movie_title`: The title of the movie.
    * `year`: The year the movie was released.
    * `imdb_rating`: The IMDB rating of the movie.
    * `imdb_votes`: The number of IMDB votes for the movie.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `year` - Sort by year of release, earliest to latest.
    * `rating` - Sort by rating, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    col_name_sort = ""
    if sort == movie_sort_options.movie_title:
        col_name_sort = "title"
    elif sort == movie_sort_options.year:
        col_name_sort = "year"
    elif sort == movie_sort_options.rating:
        col_name_sort = "imdb_rating"

    result = conn.execute(
        sqlalchemy.text(f'''
            SELECT * FROM movies
            WHERE title LIKE :name
            ORDER BY {col_name_sort} {"DESC" if col_name_sort == "imdb_rating" else "ASC"}, movie_id ASC
            LIMIT :limit
            OFFSET :offset
        '''),
        [{"name": f"%{name}%", "limit": limit, "offset": offset}]
    )
    movies = []
    for row in result:
        movies.append({
            "movie_id": row[0],
            "movie_title": row[1],
            "year": str(row[2]),
            "imdb_rating": row[3],
            "imdb_votes": row[4]
        })
    return movies

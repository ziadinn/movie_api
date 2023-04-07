from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from src.datatypes import Character, Movie, Conversation, Line

router = APIRouter()


def get_num_lines(char_id, movie_id):
    raise DeprecationWarning
    c = db.characters.get(char_id)
    if not c:
        return None
    return sum(1 for line in db.lines.values() if line.movie_id == movie_id and line.c_id == char_id)
    
    lines = filter(
        lambda line: line.movie_id == movie_id and line.c_id == char_id,
        (db.lines.get(line_id) for line_id in c.lines if line_id)
    )
    
    # lines = filter(
    #     lambda line: line.movie_id == movie_id,
    #     (db.lines.get(line_id) for line_id in c.lines if line_id)
    # )
    return len(lines)

# include top 3 actors by number of lines
@router.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: str):
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
    if movie_id.isnumeric():
        movie_id = int(movie_id)
        movie = db.movies.get(movie_id)
        if movie:
            top_chars = [
                {
                    "character_id" : c.id,
                    "character" : c.name,
                    "num_lines" : c.num_lines #sum(1 for line in db.lines.values() if line.movie_id == movie_id and line.c_id == c.id)
                }
                for c in db.characters.values() if c.movie_id == movie_id
                #for c in map(lambda c_id: db.characters.get(c_id), movie.characters) if c
            ]
            top_chars.sort(key=lambda c: c["num_lines"], reverse=True)

            result = {
                "movie_id" : movie_id,
                "title" : movie.title,
                "top_characters" : top_chars[0:5]
            }
            return result

    # json = None

    # for movie in db.movies:
    #     if movie["movie_id"] == id:
    #         print("movie found")
    #         json = movie

    raise HTTPException(status_code=404, detail="movie not found.")


class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/movies/", tags=["movies"])
def list_movies(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
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

    items = list(filter(lambda m: name in m.title, db.movies.values()))
    if sort == movie_sort_options.movie_title:
        #sort_fn = lambda m: m.title
        items.sort(key=lambda m: m.title)
    elif sort == movie_sort_options.year:
        #sort_fn = lambda m: m.year
        items.sort(key=lambda m: m.year)
    elif sort == movie_sort_options.rating:
        items.sort(key=lambda m: m.imdb_rating, reverse=True)


    #items.sort(key=sort_fn)
    #sort_fn(items)
    json = (
        {
            "movie_id" : m.id,
            "movie_title" : m.title,
            "year" : m.year,
            "imdb_rating" : m.imdb_rating,
            "imdb_votes" : m.imdb_votes
        }
        for m in items[offset:offset+limit]
    )

    return json

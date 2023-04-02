from fastapi import APIRouter, HTTPException
from enum import Enum

router = APIRouter()


# include top 3 actors by number of lines
@router.get("/movies/{movie_id}")
def get_movie(movie_id: str):
    json = None

    if json is None:
        raise HTTPException(status_code=404, detail="movie not found.")

    return json


class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/movies/")
def list_movies(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: movie_sort_options = movie_sort_options.movie_title,
):
    json = None

    return json

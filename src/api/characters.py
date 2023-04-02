from fastapi import APIRouter, HTTPException
from enum import Enum

router = APIRouter()


@router.get("/characters/{id}")
def get_character(id: str):
    json = None

    if json is None:
        raise HTTPException(status_code=404, detail="movie not found.")

    return json


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/")
def list_characters(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: character_sort_options = character_sort_options.character,
):
    json = None
    return json

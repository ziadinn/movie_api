from fastapi import APIRouter, HTTPException
import sqlalchemy
from src import database as db
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
    subquery = (
        sqlalchemy.select(
            db.lines.c.character_id, sqlalchemy.func.count("*").label("num_lines")
        )
        .group_by(db.lines.c.character_id)
        .subquery()
    )

    if sort is character_sort_options.character:
        order_by = db.characters.c.name
    elif sort is character_sort_options.movie:
        order_by = db.movies.c.title
    elif sort is character_sort_options.number_of_lines:
        order_by = sqlalchemy.desc(subquery.c.num_lines)
    else:
        assert False

    stmt = (
        sqlalchemy.select(
            db.characters.c.name,
            db.characters.c.character_id,
            db.movies.c.title,
            subquery.c.num_lines,
        )
        .join(db.movies)
        .join(subquery)
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.characters.c.character_id)
    )

    # filter only if name parameter is passed
    if name != "":
        stmt = stmt.where(db.characters.c.name.ilike(f"%{name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "character_id": row.character_id,
                    "character": row.name,
                    "movie": row.title,
                    "number_of_lines": row.num_lines,
                }
            )

    return json

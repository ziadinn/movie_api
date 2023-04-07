from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
import json

router = APIRouter()

def get_top_conversations(character):
  return None
  # def conversation(c_id, m_id):
  #   for convo in db.conversations:
  #     if convo["movie_id"] == m_id and (convo["character1_id"] == c_id or convo["character2_id"] == c_id):
  #       yield convo
  
  
    

@router.get("/characters/{id}", tags=["characters"])
def get_character(id: str):
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
    
    character = db.idsearch(db.characters, id)

    if character:
      # print("character found")
      movie = db.idsearch(db.movies, character.movie_id)
      result = {
          "character_id" : character.id,
          "character" : character.name,
          "movie" : movie.title,
          "gender" : character.gender,
          "top_conversations" : get_top_conversations(character)
        }
      return result

    # for character in db.characters:
    #     if character["character_id"] == id:
    #         print("character found")
    #         json_str = character # json.dumps(character)

    #         movie = next((m for m in db.movies if character["movie_id"] == m["movie_id"]))
    
    #         result = {
    #           "character_id" : int(character["character_id"]),
    #           "character" : character["name"],
    #           "movie" : movie["title"],
    #           "gender" : character["gender"],
    #           "top_conversations" : get_top_conversations(character, movie)
    #         }
    #         return result

    raise HTTPException(status_code=404, detail="movie not found.")


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
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

    chars = filter(lambda c: name in c.name, db.characters)

    json_str = db.characters # json.dumps(db.characters)
    return json_str

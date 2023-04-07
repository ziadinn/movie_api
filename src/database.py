import csv
from src.datatypes import Character, Movie, Conversation, Line

# TODO: You will want to replace all of the code below. It is just to show you
# an example of reading the CSV files where you will get the data to complete
# the assignment.

print("reading movies")

def try_parse(type, val):
    try:
        return type(val)
    except ValueError:
        return None

def idsearch(list, id):
    return list.get(id)
    # Assumes list is sorted by id
    lo = 0
    hi = len(list)
    if (id < hi and list[id].id == id):
        return list[id] # fast result if list is indexed by id
    # otherwise do binary search
    while lo < hi:
        mid = (lo + hi) // 2
        if list[mid].id == id:
            return list[mid]
        if list[mid].id < id:
            lo = mid + 1
        else:
            hi = mid
    return None

with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    movies = {
        try_parse(int, row["movie_id"]) :
        Movie(
            try_parse(int, row["movie_id"]),
            row["title"] or None,
            row["year"] or None,
            try_parse(float, row["imdb_rating"]),
            try_parse(int, row["imdb_votes"]),
            row["raw_script_url"] or None,
            [],
            [],
            [] # filled in later
        )
        for row in csv.DictReader(csv_file, skipinitialspace=True)
    }

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    characters = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        char = Character(
            try_parse(int, row["character_id"]),
            row["name"] or None,
            try_parse(int, row["movie_id"]),
            row["gender"] or None,
            try_parse(int, row["age"]),
            [],
            []
        )
        characters[char.id] = char
        if char.movie_id:
            m = movies.get(char.movie_id)
            if m:
                m.characters.append(char.id)

with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    conversations = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        conv = Conversation(
            try_parse(int, row["conversation_id"]),
            try_parse(int, row["character1_id"]),
            try_parse(int, row["character2_id"]),
            try_parse(int, row["movie_id"]),
            0,
            []
        )
        conversations[conv.id] = conv
        for c_id in [conv.c1_id, conv.c2_id]:
            c = idsearch(characters, c_id)
            if c:
                c.conversations.append(conv.id)
        m = idsearch(movies, conv.movie_id)
        if m:
            m.conversations.append(conv.id)

with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    lines = {}
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        line = Line(
            try_parse(int, row["line_id"]),
            try_parse(int, row["character_id"]),
            try_parse(int, row["movie_id"]),
            try_parse(int, row["conversation_id"]),
            try_parse(int, row["line_sort"]),
            row["line_text"]
        )
        lines[line.id] = line
        c = idsearch(characters, line.c_id)
        if c:
            c.lines.append(line.id)

        m = idsearch(movies, line.movie_id)
        if m:
            m.lines.append(line.id)
        
        conv = idsearch(conversations, line.conv_id)
        if conv:
            conv.lines.append(line.id)
            conv.num_lines += 1


# with open("movies.csv", mode="r", encoding="utf8") as csv_file:
#     movies = [
#         {k: v for k, v in row.items()}
#         for row in csv.DictReader(csv_file, skipinitialspace=True)
#     ]

# with open("characters.csv", mode="r", encoding="utf8") as csv_file:
#     characters = [
#         {k: v for k, v in row.items()}
#         for row in csv.DictReader(csv_file, skipinitialspace=True)
#     ]

# with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
#     conversations = [
#         {k: v for k, v in row.items()}
#         for row in csv.DictReader(csv_file, skipinitialspace=True)
#     ]

# with open("lines.csv", mode="r", encoding="utf8") as csv_file:
#     lines = [
#         {k: v for k, v in row.items()}
#         for row in csv.DictReader(csv_file, skipinitialspace=True)
#     ]

from fastapi import FastAPI
from src.api import characters, movies, pkg_util

description = """
Movie API returns dialog statistics on top hollywood movies from decades past.

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

app = FastAPI(
    title="Movie Lines API",
    description=description,
    version="0.0.1",
    contact={
        "name": "Lucas Pierce",
        "email": "lupierce@calpoly.edu",
    },
)
app.include_router(characters.router)
app.include_router(movies.router)
app.include_router(pkg_util.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the movie API"}

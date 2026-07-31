from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from ..database import SessionDep
from .model import Movie

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/new")
def new_movie() -> Movie:
    return Movie(title="New Movie")


@router.get("/")
async def get_movies(session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
                     ) -> list[Movie]:
    movies = session.exec(select(Movie).offset(offset).limit(limit)).all()
    return movies


@router.post("/")
def create_movie(movie: Movie, session: SessionDep) -> Movie:
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie


@router.get("/{movie_id}")
async def get_movie(movie_id: int, session: SessionDep) -> Movie:
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.patch("/{movie_id}")
async def update_movie(movie_id: int, movie: Movie, session: SessionDep) -> Movie:
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie


@router.put("/{movie_id}")
async def update_movie(movie_id: int, movie: Movie, session: SessionDep) -> Movie:
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie


@router.delete("/{movie_id}")
async def delete_movie(movie_id: int, session: SessionDep):
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    session.delete(movie)
    return { "ok": True }

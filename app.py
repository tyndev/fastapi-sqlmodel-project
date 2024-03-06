from typing import List, Optional

from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select


# Define models with relationships for a simple ORM setup using SQLModel
#   This is an SQLModel class that represents both the database model and the schema for API requests/responses.   
#   It serves both as Pydantic models (for type validation and serialization) and SQLAlchemy models (for database ORM), 
#   it simplifies the codebase by eliminating the need to define separate models for the database and API schemas.
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)


# Setup database connection
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False} # Prevent sharing same session with more than one request
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

# Function to create database and tables based on SQLModel definitions
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Instance of the FastAPI class
app = FastAPI()


# Initialize database and tables on app startup
@app.on_event("startup") # TODO https://chat.openai.com/c/aef8ba7d-47c7-4554-8c97-884c1d4445cb
def on_startup():
    create_db_and_tables()

# Define endpoint to create a new hero via POST request
@app.post("/heroes/", response_model=Hero)
def create_hero(hero: Hero):
    with Session(engine) as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


@app.get("/heroes/", response_model=List[Hero])
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes
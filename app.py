import asyncio
from typing import List, Optional

from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager

# DATA MODELS ----------------------------------
# Model that represents a table in the database, (both a Pydantic model, and a SQLAlchemy model)
# Pydantic models (for type validation and serialization) and SQLAlchemy models (for database ORM)
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)

# API MODELS ----------------------------------
# Model that defines what client needs to send to our API, (only a Pydantic model)
class HeroCreate(SQLModel): 
    name: str
    secret_name: str
    age: Optional[int] = None
# Model that defines what client can expect to receive from our API, (only a Pydantic model)
class HeroRead(SQLModel):
    id: int
    name: str
    secret_name: str
    age: Optional[int] = None


# Setup database connection
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False} # Prevent sharing same session with more than one request
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

# Function to create database and tables based on SQLModel definitions
def create_db_and_tables_sync():
    SQLModel.metadata.create_all(engine)

# Async version of the above function
async def create_db_and_tables():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, create_db_and_tables_sync)

# Async context manager to handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run startup logic
    await create_db_and_tables()
    yield
    # Run shutdown logic (if any)

# Instance of the FastAPI class
app = FastAPI(lifespan=lifespan)


# Define endpoint to create a new hero via POST request
@app.post("/heroes/", response_model=HeroRead)
def create_hero(hero: HeroCreate):
    with Session(engine) as session:
        db_hero = Hero.model_validate(hero) # validates client request against data model
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero


@app.get("/heroes/", response_model=List[Hero])
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes
import asyncio
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager


# BASE MODEL --------------------------------------------------
# Model that is used for inheritance of common or shared fields
class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)
    
# DATA MODELS ----------------------------------
# Model that represents a table in the database, (both a Pydantic model, and a SQLAlchemy model)
# Pydantic models (for type validation and serialization) and SQLAlchemy models (for database ORM)
class Hero(HeroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field()
# API MODELS ----------------------------------
# Model that defines what client needs to send to our API, (only a Pydantic model)
# Could just use the base model, but docs would say HeroBase, & HeroCreate is more client friendly
class HeroCreate(HeroBase): 
    password: str

# Model that defines what client can expect to receive from our API, (only a Pydantic model)
# ID will be created when pulling from database, so this is required
class HeroRead(HeroBase):
    id: int 

# Model for optional updates accounting for potential partial hero data modifications
# Because all fields are options, this model can not inheret from HeroBase
class HeroUpdate(SQLModel):
    name: Optional[str] = None
    secret_name: Optional[str] = None
    age: Optional[int] = None
    password: Optional[str] = None

# Setup database connection
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False} # Prevent sharing same session with more than one request
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

# Function to create database and tables based on SQLModel definitions
def create_db_and_tables_sync():
    SQLModel.metadata.create_all(engine)

# Function to create a fake hashed password for testing
def hash_password(password: str) -> str:
    # use something like passlib here
    return f"not actually hashed {password}"

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
    hashed_password = hash_password(hero.password)
    with Session(engine) as session:
        extra_data = {"hashed_password": hashed_password}
        db_hero = Hero.model_validate(hero, update=extra_data) # validates client request against data model and adds extra data like hashed password
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero

# Define endpoint to read heroes via GET request
@app.get("/heroes/", response_model=List[HeroRead])
def read_heroes(offset: int = 0, limit: int = Query(default=100, le=100)):
    with Session(engine) as session:
        heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()     
        return heroes
    
    
# Define endpoint to read one hero via GET request
@app.get("/heroes/{hero_id}", response_model=HeroRead)
def read_hero(hero_id: int):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        return hero

# Define endpoint to update a hero by ID, handling partial updates
@app.patch("/heroes/{hero_id}", response_model=HeroRead)
def update_hero(hero_id: int, hero: HeroUpdate):
    with Session(engine) as session:
        db_hero = session.get(Hero, hero_id)
        if not db_hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        hero_data = hero.model_dump(exclude_unset=True) # exclude defaul `None`s if any
        extra_data = {}
        if "password" in hero_data:
            password = hero_data["password"]
            hashed_password = hash_password(password)
            extra_data["hashed_password"] = hashed_password
        db_hero.sqlmodel_update(hero_data, update=extra_data)
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero
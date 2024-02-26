from typing import Optional

from sqlmodel import Field, Session, SQLModel, col, create_engine, select

# This class Hero represents the table for our heroes. And each instance we create later will represent a row in the table.
# the config table=True tells SQLModel that this is a table model, aka it represents a table.
# we tell SQLModel that this id field/column is the primary key of the table. But inside the SQL database, it is always required and can't be NULL. Why should we declare it with Optional? The id will be required in the database, but it will be generated by the database, not by our code. So, whenever we create an instance of this class (in the next chapters), we will not set the id. And the value of id will be None until we save it in the database, and then it will finally have a value. So, because in our code (not in the database) the value of id could be None, we use Optional. This way the editor will be able to help us, for example, if we try to access the id of an object that we haven't saved in the database yet and would still be None. If we didn't set the default value, whenever we use this model later to do data validation (powered by Pydantic) it would accept a value of None apart from an int, but it would still require passing that None value. And it would be confusing for whoever is using this model later (probably us), so better set the default value here.
# tell SQLModel that age is not required when validating data and that it has a default value of None. And we also tell it that, in the SQL database, the default value of age is NULL (the SQL equivalent to Python's None).
class Hero(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True) 
    name: str
    secret_name: str
    age: Optional[int] = None 


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}" 
# Alternative in-Memory SQLite Database: SQLite supports a special database that lives all in memory. Hence, it's very fast, but be careful, the database gets deleted after the program terminates. You can specify this in-memory database by using just two slash characters (//) and no file name: `sqlite://`

engine = create_engine(sqlite_url, echo=True) 
# You should normally have a single engine object for your whole application and re-use it everywhere. 
# echo=True will make the engine print all the SQL statements it executes, which can help you understand what's happening. It is particularly useful for learning and debugging but in production, you would probably want to remove it.


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # If this was not in a function and we tried to import something from this module (from this file) in another, it would try to create the database and table every time we executed that other file that imported this module.

def create_heroes():
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
    hero_4 = Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32)
    hero_5 = Hero(name="Black Lion", secret_name="Trevor Challa", age=35)
    hero_6 = Hero(name="Dr. Weird", secret_name="Steve Weird", age=36)
    hero_7 = Hero(name="Captain North America", secret_name="Esteban Rogelios", age=93)
    
    print("Before interacting with the database")
    print("Hero 1:", hero_1)
    print("Hero 2:", hero_2)
    print("Hero 3:", hero_3)
    
    # The session will create a new transaction and execute all the SQL code in that transaction. This ensures that the data is saved in a single batch, and that it will all succeed or all fail, but it won't leave the database in a broken state. It's good to know how the Session works and how to create and close it manually. It might be useful if, for example, you want to explore the code in an interactive session (for example with Jupyter). But there's a better way to handle the session, using a `with` block.
    # session = Session(engine)
    with Session(engine) as session:
        # This works similarly to Git where `add` stages the changes and `commit` saves them to the database.
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        session.add(hero_4)
        session.add(hero_5)
        session.add(hero_6)
        session.add(hero_7)
                
        print("After adding to the session")
        print("Hero 1:", hero_1) # 
        print("Hero 2:", hero_2)
        print("Hero 3:", hero_3)
        
        session.commit()
        
        # After committing, the objects are expired and have no values
        print("After committing the session")
        print("Hero 1:", hero_1) # returns nothing
        print("Hero 2:", hero_2) # returns nothing
        print("Hero 3:", hero_3) # returns nothing

        # But when accessing the attribute after committing, SQLAlchemy will automatically fetch the data from the database and update the object.
        print("After committing the session, show IDs")
        print("Hero 1 ID:", hero_1.id)
        print("Hero 2 ID:", hero_2.id)
        print("Hero 3 ID:", hero_3.id)
        print("After committing the session, show names")
        print("Hero 1 name:", hero_1.name)
        print("Hero 2 name:", hero_2.name)
        print("Hero 3 name:", hero_3.name)
        
        # Remember here_1 (ect.) returned empty after the commit above. Below the session will make the engine communicate with the database to get the recent data for this object hero_1 (etc.), and then the session puts the data in the hero_1 object and marks it as "fresh" or "not expired".
        session.refresh(hero_1)
        session.refresh(hero_2)
        session.refresh(hero_3)
        print("After refreshing the heroes")
        print("Hero 1:", hero_1)
        print("Hero 2:", hero_2)
        print("Hero 3:", hero_3)
        # This `refresh` could be useful, for example, if you are building a web API to create heroes. And once a hero is created with some data, you return it to the client. You wouldn't want to return an object that looks empty because the automatic magic to refresh the data was not triggered. In this case, after committing the object to the database with the session, you could refresh it, and then return it to the client. This would ensure that the object has its fresh data.
    
    # By finishing the with block, the Session is closed, including a rollback of any pending transaction that could have been there and was not committed.    
    # You always need to close the session as it uses resources `session.close()`. HOWEVER here, using a with block, the session will be automatically created when starting the with block and assigned to the variable session, and it will be automatically closed (meaning `session.close()` not needed) after the with block is finished. And it will work even if there's an exception in the code. 
    print("After the session closes")
    print("Hero 1:", hero_1)
    print("Hero 2:", hero_2)
    print("Hero 3:", hero_3)    

def select_heros():
    # We pass the class model Hero to the select() function. And that tells it that we want to select all the columns necessary for the Hero class. And notice that in the select() function we don't explicitly specify the FROM like in SQL. It is already obvious to SQLModel (actually to SQLAlchemy) that we want to select FROM the table hero, because that's the one associated with the Hero class model.
    with Session(engine) as session:
        # Your editor will give you autocompletion for both SQLModel's session.exec() and SQLAlchemy's session.execute(). Remember to always use session.exec() to get the best editor support and developer experience.
        heroes = session.exec(select(Hero).where(col(Hero.age) >= 35, col(Hero.age) < 40)).all()
        print(heroes)
        # hero = Hero(name="Deadpond", secret_name="Dive Wilson")
        # Above, the model class is Hero (capital H) and the instance is hero (lowercase h).
        # So now you have Hero.name and hero.name that look very similar, but are two different things:
        # >>> Hero.name == "Deadpond"
        # <sqlalchemy.sql.elements.BinaryExpression object at 0x7f4aec0d6c90>
        # >>> hero.name == "Deadpond"
        # True or False
        # Without col() above, you get a type error b/c Hero.age is potentially None, and you cannot compare None with an operqator like `>=`. This is because as we are using pure and plain Python annotations for the fields, age is indeed annotated as Optional[int], which means int or None. To fix this we can tell the editor that this class attribute is actually a special SQLModel column (instead of an instance attribute with a normal value).
        
def main():
    create_db_and_tables()
    create_heroes()
    select_heros()

if __name__ == "__main__":
    main()
# fastapi-sqlmodel-project
 
A learning project for database management and ORM best practices using SQLModel. Much was learned by diligently working through the [SQLModel Tutorial](https://sqlmodel.tiangolo.com/tutorial/) and [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/).

🚧 Eventually, this project should also demonstrate HTTP endpoints (GET, POST, PUT, DELETE), request handling, and response management.

**Completed:**
- defining models
- interacting with an SQLite database
- performing CRUD operations in a structured and efficient manner

## Learnings

### Object-Relational Mapping (ORM)
- **Model Definition**: learned to used SQLModel for defining data models that map Python classes to SQL database tables.
- **Primary Key Handling**: used `Optional[int]` for primary keys to accommodate auto-generated IDs by the SQL database. This taught the distinction between code-level and database-level requirements.
- **Automatic Data Refresh**: Learned about object expiration and the use of session refresh to synchronize ORM objects with their latest database state. Important to make sure empty data sets are not used by mistake.
- **Class vs. Instance Attributes**: Learned when to use class attributes for query expressions (e.g., `Hero.name`) and instance attributes for specific values (e.g., `hero.name`). This is important for constructing good SQL queries vs accessing object data.

### Database Operations
- **Engine Configuration**: Learned to use a single SQLite database engine object and re-use it everywhere to provide with good performance and safe database interactions.
- **Session Management**: Implemented the use of context managers (originally learned in an advanced Python course) for handling database sessions so that transactions are correctly committed or rolled back.

### CRUD Operations
- **Data Insertion**: Learned how to add multiple entries to a database in a single transaction for efficient batch processing using an ORM.
- **Data Querying**: Implemented queries with filters, with SQLModel / SQLAlchemy expressions to get specific data sets based on conditions.


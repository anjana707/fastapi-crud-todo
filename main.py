from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
from contextlib import asynccontextmanager

# Setup Engine
sqlite_url = "sqlite:///tasks.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def seed_tasks_if_empty():
    """Ensures 3 default tasks exist if database is fresh."""
    with Session(engine) as session:
        statement = select(Task)
        existing_tasks = session.exec(statement).first()
        
        # Only seed if no tasks exist
        if not existing_tasks:
            default_tasks = [
                Task(title="Buy Milk", done=False),
                Task(title="Complete Assignment", done=False),
                Task(title="Review Stage 5 Code", done=True),
            ]
            session.add_all(default_tasks)
            session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create tables automatically on startup
    SQLModel.metadata.create_all(engine)
    # 2. Seed default data if database is empty
    seed_tasks_if_empty()
    yield

app = FastAPI(lifespan=lifespan)

#1. Define 3 example tasks 
tasks = [
    {"id": 1, "title": "Task 1", "done": False},
    {"id": 2, "title": "Task 2", "done": True},
    {"id": 3, "title": "Task 3", "done": False},
]

class Task(SQLModel, table = True): # creates class "Tasks" consisting of three columns: id, title, done 
    id: int | None = Field(default=None, primary_key = True)
    title: str
    done: bool = False

sqlite_file_name = "tasks.db"
sqlite_url = f"sqlite:///{sqlite_file_name}" #url for database 
engine = create_engine(sqlite_url) # create engine


# Define temp root endpoint
@app.get("/")   # what happens when a client sends a GET request to the root endpoint
def real_root():
    return {
        "name": "Task API", # Name of the API
        "version": "1.0",
        "endpoints": ["/tasks"] # functionality of the API
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok" # Health status of the API
    }

@app.get("/tasks")  # what happens when a client sends a GET request to the /tasks endpoint
def get_tasks(done: Optional[bool] = None):
    with Session(engine) as session: #opens temporary channel btw application and database
        statement = select(Task)
        #Apply filter only if "done" parameter provided by client 
        if done is not None:
            statement = statement.where(Task.done == done)
        tasks = session.exec(select(Task)).all() # builds a query equivalent to SELECT * FROM tasks
        return tasks  # Return the list of tasks

@app.get("/tasks/{task_id}")  # what happens when a client sends a GET request to the /tasks/{task_id} endpoint
def get_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id) # SELECT * FROM tasks WHERE id = ? 
        if not task:
             return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})  # Return an error message if no matching task is found
        
        return task # Return the matching task
   
@app.post("/tasks", status_code=201)  # what happens when a client sends a POST request to the /tasks endpoint, sets the status code to 201 (Created)
def create_task(task: Task):
    #1. Validate the input data
    if not task.title or task.title.strip() == "":
        return JSONResponse(status_code=400, content={"error": "Task must have a title"})  # Return an error message if the input data is invalid
    
    #2. Save to database
    with Session(engine) as session:
        new_task = Task(title=task.title.strip(), done=False)
        session.add(new_task) # adds new task to database session
        session.commit() #writes task direcrly to tasks.db
        session.refresh(new_task)  # Gets the database-assigned ID
        return new_task

@app.put("/tasks/{task_id}")  # what happens when a client sends a PUT request to the /tasks/{task_id} endpoint
def update_task(task_id: int, updated_task: Task):
    if updated_task.title is not None and updated_task.title.strip() == "":
        return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})
    with Session(engine) as session:
        db_task = session.get(Task, task_id)
        if not db_task:
            return JSONResponse(status_code=404, content= {"error": "Task not found"})
        
        #update attributes
        db_task.title = updated_task.title.strip()
        db_task.done = updated_task.done
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

@app.delete("/tasks/{task_id}")  # what happens when a client sends a DELETE request to the /tasks/{task_id} endpoint
def delete_task(task_id: int):
    with Session(engine) as session:
        db_task = session.get(Task, task_id)
        if not db_task:
            return JSONResponse(status_code=404, content={"error": "Task not found"})
        # if valid input for delete
        session.delete(db_task)
        session.commit()
        return JSONResponse(status_code=204, content={"message": f"Task deleted"})  # Return a success message if the task is deleted
    
#Create Database on Startup 
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables() # on startup, create database and tables 



from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Field, Session, SQLModel, create_engine

#Initialize the FastAPI app
app = FastAPI()

#1. Define 3 example tasks 
tasks = [
    {"id": 1, "title": "Task 1", "done": False},
    {"id": 2, "title": "Task 2", "done": True},
    {"id": 3, "title": "Task 3", "done": False},
]
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
def get_tasks():
    with Session(engine) as session: #opens temporary channel btw application and database
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
def create_task(task: dict):
    #1. Validate the input data
    if "title" not in task:
        return JSONResponse(status_code=400, content={"error": "Task must have a title"})  # Return an error message if the input data is invalid
    
    #2. Process the input data and create a new task
    task_id = len(tasks) + 1  # Generate a new task ID
    task["id"] = task_id  # Assign the new ID to the task
    task["done"] = False  # Set the done status to False by default
    tasks.append(task)  # Add the new task to the list of tasks
    return task  # Return the newly created task

@app.put("/tasks/{task_id}")  # what happens when a client sends a PUT request to the /tasks/{task_id} endpoint
def update_task(task_id: int, updated_task: dict):
    for task in tasks:  # Iterate through the list of tasks
        if task["id"] == task_id:  # Check if the task ID matches the requested ID
            task.update(updated_task)  # Update the task with the new data
            return task  # Return the updated task
    if not any(task["id"] == task_id for task in tasks):  # Check if the task ID does not exist in the list of tasks
        return JSONResponse(status_code=404, content={"error": f"Unkown ID"})  # Return an error message if no matching task is found
    
    return JSONResponse(status_code=400, content={"error": f"Task {task_id} not found"})  # Return an error message if no matching task is found

@app.delete("/tasks/{task_id}")  # what happens when a client sends a DELETE request to the /tasks/{task_id} endpoint
def delete_task(task_id: int):
    for task in tasks: 
        if task["id"] == task_id:
            tasks.remove(task)
            return JSONResponse(status_code=204, content={"message": f"Task {task_id} deleted"})  # Return a success message if the task is deleted
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})  # Return an error message if the task is not found

class Task(SQLModel, table = True): # three columnds: id, title, done 
    id: int | None = Field(default=None, primary_key = True)
    title: str
    done: bool = False

sqlite_file_name = "tasks.db"
sqlite_url = f"sqlite:///{sqlite_file_name}" #url for database 
engine = create_engine(sqlite_url) # create engine

#Create Database on Startup 
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables() # on startup, create database and tables 



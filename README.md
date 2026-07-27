# FastAPI Task Manager Database API

A lightweight RESTful API for managing tasks powered by FastAPI, SQLModel, and SQLite.

## How to Run the Project

Run the following command to start the server:

```bash
uvicorn main:app --reload
```

> **Note:** On first run, `tasks.db` will be created automatically and populated with 3 initial seed tasks.

---

## Database Architecture & Decisions

### Why SQLite was Chosen
* **Single File:** The entire database lives inside a single `tasks.db` file on disk.
* **Zero Setup:** Requires no external database servers, background services, or credentials.
* **Persistence:** Data survives server reloads and restarts, unlike in-memory databases.

### Database Location & Version Control
* The database file is located at `./tasks.db`.
* It is created automatically upon launching the application.
* `tasks.db` is included in `.gitignore` so that every fresh clone builds its own local database upon startup without git conflicts.

---

## Stage 4 Example SQL Query

Below is an example of the SQL query executed under the hood during **Stage 4** to retrieve filtered tasks:

```sql
SELECT task.id, task.title, task.done 
FROM task 
WHERE task.done = 0;
```

---

## Database Inspection

![DB Browser Screenshot](./screenshot.png)
*(Includes table schema and seeded task records viewed in DB Browser for SQLite)*
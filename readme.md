# Enhanced Task Manager with MySQL

A task management application with persistent storage in MySQL and full CRUD operations.

## Setup Instructions

1. Install required packages:
   ```
   pip install mysql-connector-python pytest
   ```

2. Configure database connection:
   
   Create `db_config.py` with your MySQL credentials:
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "port": 3306,
       "user": "your_username",
       "password": "your_password", 
       "database": "task_manager"
   }
   ```

   For testing, create `tests/test_db_config.py`:
   ```python
   DB_CONFIG_TEST = {
       "host": "localhost",
       "port": 3306,
       "user": "your_username",
       "password": "your_password", 
       "database": "task_manager_test"
   }
   ```

3. Run the application:
   ```
   python task_manager.py
   ```

## Running Tests

Run the test suite using pytest:
```
python -m pytest tests/task_manager_tests.py -v
```

The tests will:
- Create a separate test database
- Perform CRUD operations for validation
- Clean up by dropping the test database when finished

## Usage

The application provides a simple command-line interface with the following options:

1. **Add Task**: Create a new task with name, description, and status
2. **Show Tasks**: View existing tasks with optional filtering
3. **Update Task**: Change the status of a task
4. **Delete Task**: Remove a task from the database
5. **Exit**: Close the application

At any prompt, you can type 'exit' to cancel the current operation and return to the main menu.
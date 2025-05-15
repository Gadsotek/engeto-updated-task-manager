# Task status constants
TASK_STATE_NOT_STARTED = "Not started"
TASK_STATE_IN_PROGRESS = "In progress"
TASK_STATE_COMPLETED = "Completed"

# UI text constants
UI_DIVIDER = 5*"_"
UI_HEADER_TASK_MANAGER = UI_DIVIDER + "Task Manager" + UI_DIVIDER
UI_HEADER_ADD_TASK = UI_DIVIDER + "Add Task" + UI_DIVIDER
UI_HEADER_TASK_LIST = UI_DIVIDER + "Task List" + UI_DIVIDER
UI_HEADER_UPDATE_TASK = UI_DIVIDER + "Update Task" + UI_DIVIDER
UI_HEADER_DELETE_TASK = UI_DIVIDER + "Delete Task" + UI_DIVIDER

UI_EXIT_MESSAGE = "Type 'exit' at any prompt to return to main menu"
UI_CANCEL_MESSAGE = "{} cancelled."

# Error messages
ERROR_TASK_NAME_REQUIRED = "Task name is required. Please enter a valid name."
ERROR_TASK_DESC_REQUIRED = "Task description is required. Please enter a valid description."
ERROR_TASK_NOT_FOUND = "Task not found. Please enter a valid ID."
ERROR_INVALID_NUMBER = "Please enter a valid number."
ERROR_INVALID_CHOICE = "Please select a valid option ({})"
ERROR_NO_TASKS = "No tasks found. Please add some tasks first."
ERROR_NO_TASKS_TO_UPDATE = "No tasks available for update."
ERROR_NO_TASKS_TO_DELETE = "No tasks available to delete."

# Success messages
SUCCESS_TASK_ADDED = "Task '{}' added successfully with status '{}'."
SUCCESS_TASK_UPDATED = "Task '{}' updated to '{}'."
SUCCESS_TASK_DELETED = "Task '{}' deleted successfully."
SUCCESS_SETUP_COMPLETE = "Task Manager is ready!"

# Failure messages
FAILURE_ADD_TASK = "Failed to add task. Please try again."
FAILURE_UPDATE_TASK = "Failed to update task. Please try again."
FAILURE_DELETE_TASK = "Failed to delete task. Please try again."

# Database messages
DB_CREATED_OR_EXISTS = "Database '{}' created or already exists"
DB_TABLE_CREATED_OR_EXISTS = "Tasks table created or already exists"

# Field constraints
MAX_NAME_LENGTH = 255
ERROR_NAME_TOO_LONG = f"Task name too long. Maximum length is {MAX_NAME_LENGTH} characters."
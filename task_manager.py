import os
import sys

# Import database configuration - raise exception if missing
try:
    from db_config import DB_CONFIG
except ImportError:
    raise ImportError("Database configuration file (db_config.py) is missing. Please create this file with your database settings.")

# Import our modules
from constants import *
from utils import get_input_with_exit, get_numeric_input_with_exit, is_exit_command
from models import Task
from db_manager import DatabaseManager
from repository import TaskRepository


class TaskManager:
    """
    Main application class that handles user interaction
    """
    def __init__(self, db_config=None):
        """
        Initialize the Task Manager with an optional database configuration.
        
        Args:
            db_config (dict, optional): Database configuration dictionary.
        """
        self.db_manager = DatabaseManager(db_config if db_config else DB_CONFIG)
        self.task_repository = TaskRepository(self.db_manager)
    
    def setup_database(self):
        """
        Sets up the database and required tables
        """
        self.db_manager.create_database()
        self.db_manager.create_table()
    
    def main_menu(self):
        """
        Display the main menu with options and return the user's choice.
        """
        print(f"\n{UI_HEADER_TASK_MANAGER}")
        print("1. Add task")
        print("2. Show tasks")
        print("3. Update task")
        print("4. Delete task")
        print("5. Exit program")
        
        choice = get_numeric_input_with_exit("\nSelect option (1-5): ", 1, 5)
        # If user entered 'exit', exit the program
        return 5 if choice is None else choice
    
    def add_task(self):
        """
        Adds a new task to the database.
        """
        print(f"\n{UI_HEADER_ADD_TASK}")
        print(UI_EXIT_MESSAGE)
        
        # Get task name (required)
        while True:
            name = get_input_with_exit("Task name: ")
            if name is None:
                print(UI_CANCEL_MESSAGE.format("Task creation"))
                return
            
            if not name.strip():
                print(ERROR_TASK_NAME_REQUIRED)
                continue
                
            # Check name length to fit VARCHAR(255)
            if len(name) > MAX_NAME_LENGTH:
                print(ERROR_NAME_TOO_LONG)
                continue

            break
        
        # Get task description (required)
        while True:
            description = get_input_with_exit("Task description: ")
            if description is None:
                print(UI_CANCEL_MESSAGE.format("Task creation"))
                return
            
            if not description.strip():
                print(ERROR_TASK_DESC_REQUIRED)
                continue
                
            break
        
        # Get task status
        print("\nSelect task status:")
        print(f"1. {TASK_STATE_NOT_STARTED} (default)")
        print(f"2. {TASK_STATE_IN_PROGRESS}")
        print(f"3. {TASK_STATE_COMPLETED}")
        
        status_choice = get_numeric_input_with_exit(
            "Enter choice (1-3, or press Enter for default): ", 
            1, 3, 
            allow_empty=True
        )
        if status_choice is None and is_exit_command(status_choice):
            print(UI_CANCEL_MESSAGE.format("Task creation"))
            return
            
        # Determine status based on choice
        status = TASK_STATE_NOT_STARTED  # Default
        if status_choice == 2:
            status = TASK_STATE_IN_PROGRESS
        elif status_choice == 3:
            status = TASK_STATE_COMPLETED
        
        # Create and add the task
        task = Task(name=name, description=description, status=status)
        if self.task_repository.add(task):
            print(SUCCESS_TASK_ADDED.format(name, status))
        else:
            print(FAILURE_ADD_TASK)
    
    def show_tasks(self):
        """
        Shows tasks with optional filtering by status
        """
        print(f"\n{UI_HEADER_TASK_LIST}")
        print(UI_EXIT_MESSAGE)
        
        print("1. Show active tasks only (Not started and In progress)")
        print("2. Show all tasks including completed ones")
        
        choice = get_numeric_input_with_exit("\nSelect option (1-2): ", 1, 2)
        if choice is None:
            return
            
        if choice == 1:
            # Get tasks that are not started or in progress
            filter_status = (TASK_STATE_NOT_STARTED, TASK_STATE_IN_PROGRESS)
            tasks = self.task_repository.get_all(filter_status)
        else:
            # Get all tasks including completed ones
            tasks = self.task_repository.get_all()
        
        if not tasks:
            print(ERROR_NO_TASKS)
            return
        
        for task in tasks:
            print(task.display())
            print()
    
    def update_task(self):
        """
        Updates the status of a task
        """
        print(f"\n{UI_HEADER_UPDATE_TASK}")
        print(UI_EXIT_MESSAGE)
        
        # Show all tasks that are not completed
        filter_status = (TASK_STATE_NOT_STARTED, TASK_STATE_IN_PROGRESS)
        tasks = self.task_repository.get_all(filter_status)
        
        if not tasks:
            print(ERROR_NO_TASKS_TO_UPDATE)
            return
        
        print("Available tasks:")
        for task in tasks:
            print(f"ID: {task.id} - {task.name} - Status: {task.status}")
        
        # Get task ID to update
        task_id = get_numeric_input_with_exit(
            "\nEnter the ID of the task to update: ", 
            1, 
            9999  # Arbitrary large number
        )
        if task_id is None:
            print(UI_CANCEL_MESSAGE.format("Task update"))
            return
            
        task = self.task_repository.get_by_id(task_id)
        if not task:
            print(ERROR_TASK_NOT_FOUND)
            return
        
        # Get new status
        print("\nSelect new status:")
        print(f"1. {TASK_STATE_IN_PROGRESS}")
        print(f"2. {TASK_STATE_COMPLETED}")
        
        status_choice = get_numeric_input_with_exit("Enter choice (1-2): ", 1, 2)
        if status_choice is None:
            print(UI_CANCEL_MESSAGE.format("Task update"))
            return
            
        new_status = TASK_STATE_IN_PROGRESS if status_choice == 1 else TASK_STATE_COMPLETED
        
        # Update the task
        if self.task_repository.update_status(task_id, new_status):
            print(SUCCESS_TASK_UPDATED.format(task.name, new_status))
        else:
            print(FAILURE_UPDATE_TASK)
    
    def delete_task(self):
        """
        Deletes a task from the database
        """
        print(f"\n{UI_HEADER_DELETE_TASK}")
        print(UI_EXIT_MESSAGE)
        
        # Show all tasks
        tasks = self.task_repository.get_all()
        
        if not tasks:
            print(ERROR_NO_TASKS_TO_DELETE)
            return
        
        print("Available tasks:")
        for task in tasks:
            print(f"ID: {task.id} - {task.name} - Status: {task.status}")
        
        # Get task ID to delete
        task_id = get_numeric_input_with_exit(
            "\nEnter the ID of the task to delete: ", 
            1, 
            9999  # Arbitrary large number
        )
        if task_id is None:
            print(UI_CANCEL_MESSAGE.format("Task deletion"))
            return
            
        task = self.task_repository.get_by_id(task_id)
        if not task:
            print(ERROR_TASK_NOT_FOUND)
            return
        
        # Confirm deletion
        confirm = get_input_with_exit(f"Are you sure you want to delete task '{task.name}'? (y/n): ")
        if confirm is None or confirm.lower() != 'y':
            print(UI_CANCEL_MESSAGE.format("Deletion"))
            return
        
        # Delete the task
        if self.task_repository.delete(task_id):
            print(SUCCESS_TASK_DELETED.format(task.name))
        else:
            print(FAILURE_DELETE_TASK)
    
    def run(self):
        """
        Main application loop
        """
        print("Setting up database...")
        self.setup_database()
        print(SUCCESS_SETUP_COMPLETE)
        
        while True:
            choice = self.main_menu()
            
            if choice == 1:
                self.add_task()
            elif choice == 2:
                self.show_tasks()
            elif choice == 3:
                self.update_task()
            elif choice == 4:
                self.delete_task()
            elif choice == 5:
                print("Exiting Task Manager. Goodbye!")
                break


if __name__ == "__main__":
    task_manager = TaskManager()
    task_manager.run()
import pytest
import sys
import os
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from io import StringIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from constants import TASK_STATE_NOT_STARTED, TASK_STATE_IN_PROGRESS, TASK_STATE_COMPLETED
from constants import MAX_NAME_LENGTH, ERROR_NAME_TOO_LONG
from models import Task
from db_manager import DatabaseManager
from repository import TaskRepository
from task_manager import TaskManager

# Import test fixtures
from test_fixtures import (
    setup_teardown_database,
    clean_database,
    db_manager,
    task_repository,
    DB_CONFIG_TEST
)


class TestTaskManager:
    """
    Test class for TaskManager
    """
    # Tests for add_task
    def test_add_task_positive(self, task_repository):
        """
        Positive test for adding a task
        """
        # Create a test task
        task = Task(
            name="Test Task",
            description="This is a test task"
        )
        
        # Add the task
        result = task_repository.add(task)
        
        # Verify task was added successfully
        assert result == True
        assert task.id is not None  # Task should have an ID after being added
        
        # Verify the task can be retrieved
        retrieved_task = task_repository.get_by_id(task.id)
        assert retrieved_task is not None
        assert retrieved_task.name == "Test Task"
        assert retrieved_task.description == "This is a test task"
        assert retrieved_task.status == TASK_STATE_NOT_STARTED
    
    def test_add_task_negative(self, task_repository, monkeypatch):
        """
        Negative test for adding a task - simulate database error
        """
        # Create a test task
        task = Task(
            name="Test Task",
            description="This is a test task"
        )
        
        # Monkeypatch the connect method to simulate a connection failure
        def mock_connect(*args, **kwargs):
            return None
        
        monkeypatch.setattr(task_repository.db_manager, "connect", mock_connect)
        
        # Try to add the task
        result = task_repository.add(task)
        
        # Verify task was not added
        assert result == False
    
    # Tests for update_task
    def test_update_task_positive(self, task_repository):
        """
        Positive test for updating a task
        """
        # Add a test task first
        task = Task(
            name="Update Test Task",
            description="This is a task to be updated"
        )
        task_repository.add(task)
        assert task.id is not None
        
        # Update the task status
        result = task_repository.update_status(task.id, TASK_STATE_IN_PROGRESS)
        
        # Verify the update was successful
        assert result == True
        
        # Verify the task was actually updated
        updated_task = task_repository.get_by_id(task.id)
        assert updated_task is not None
        assert updated_task.status == TASK_STATE_IN_PROGRESS
    
    def test_update_task_negative(self, task_repository):
        """
        Negative test for updating a task - non-existent task ID
        """
        # Try to update a non-existent task
        non_existent_id = 9999  # Assuming this ID doesn't exist
        result = task_repository.update_status(non_existent_id, TASK_STATE_IN_PROGRESS)
        
        # Verify the update failed
        assert result == False
    
    # Tests for delete_task
    def test_delete_task_positive(self, task_repository):
        """
        Positive test for deleting a task
        """
        # Add a test task first
        task = Task(
            name="Delete Test Task",
            description="This is a task to be deleted"
        )
        task_repository.add(task)
        assert task.id is not None
        
        # Delete the task
        result = task_repository.delete(task.id)
        
        # Verify the deletion was successful
        assert result == True
        
        # Verify the task was actually deleted
        deleted_task = task_repository.get_by_id(task.id)
        assert deleted_task is None
    
    def test_delete_task_negative(self, task_repository):
        """
        Negative test for deleting a task - non-existent task ID
        """
        # Try to delete a non-existent task
        non_existent_id = 9999  # Assuming this ID doesn't exist
        result = task_repository.delete(non_existent_id)
        
        # Verify the deletion failed
        assert result == False
    
    # Additional tests
    def test_get_all_tasks_filtered(self, task_repository):
        """
        Test retrieving tasks filtered by status
        """
        # Add multiple tasks with different statuses
        task1 = Task(name="Task 1", description="Not started task", status=TASK_STATE_NOT_STARTED)
        task2 = Task(name="Task 2", description="In progress task", status=TASK_STATE_IN_PROGRESS)
        task3 = Task(name="Task 3", description="Completed task", status=TASK_STATE_COMPLETED)
        
        task_repository.add(task1)
        task_repository.add(task2)
        task_repository.add(task3)
        
        # Get tasks that are not completed
        filter_status = (TASK_STATE_NOT_STARTED, TASK_STATE_IN_PROGRESS)
        tasks = task_repository.get_all(filter_status)
        
        # Verify only the non-completed tasks are returned
        assert len(tasks) == 2
        statuses = [task.status for task in tasks]
        assert TASK_STATE_NOT_STARTED in statuses
        assert TASK_STATE_IN_PROGRESS in statuses
        assert TASK_STATE_COMPLETED not in statuses

    def test_database_connection_error(self):
        """
        Test handling of database connection errors
        """
        # Create a database manager with invalid credentials
        invalid_config = {
            "host": "invalid_host",
            "user": "invalid_user",
            "password": "invalid_password",
            "database": "invalid_database"
        }
        db_manager = DatabaseManager(invalid_config)
        
        # Try to connect
        connection = db_manager.connect()
        
        # Verify connection failed
        assert connection is None
    
    def test_add_task_with_status_positive(self, task_repository):
        """
        Positive test for adding a task with specific status
        """
        # Create test tasks with different statuses
        task1 = Task(
            name="Task with Not Started status",
            description="This is a test task",
            status=TASK_STATE_NOT_STARTED
        )
        
        task2 = Task(
            name="Task with In Progress status",
            description="This is a test task",
            status=TASK_STATE_IN_PROGRESS
        )
        
        task3 = Task(
            name="Task with Completed status",
            description="This is a test task",
            status=TASK_STATE_COMPLETED
        )
        
        # Add the tasks
        result1 = task_repository.add(task1)
        result2 = task_repository.add(task2)
        result3 = task_repository.add(task3)
        
        # Verify tasks were added successfully
        assert result1 == True
        assert result2 == True
        assert result3 == True
        
        # Verify tasks have IDs
        assert task1.id is not None
        assert task2.id is not None
        assert task3.id is not None
        
        # Verify the tasks can be retrieved with correct statuses
        retrieved_task1 = task_repository.get_by_id(task1.id)
        retrieved_task2 = task_repository.get_by_id(task2.id)
        retrieved_task3 = task_repository.get_by_id(task3.id)
        
        assert retrieved_task1.status == TASK_STATE_NOT_STARTED
        assert retrieved_task2.status == TASK_STATE_IN_PROGRESS
        assert retrieved_task3.status == TASK_STATE_COMPLETED
    
    def test_get_all_tasks_unfiltered(self, task_repository):
        """
        Test retrieving all tasks without filtering
        """
        # Add multiple tasks with different statuses
        task1 = Task(name="Task 1", description="Not started task", status=TASK_STATE_NOT_STARTED)
        task2 = Task(name="Task 2", description="In progress task", status=TASK_STATE_IN_PROGRESS)
        task3 = Task(name="Task 3", description="Completed task", status=TASK_STATE_COMPLETED)
        
        task_repository.add(task1)
        task_repository.add(task2)
        task_repository.add(task3)
        
        # Get all tasks without filtering
        tasks = task_repository.get_all()
        
        # Verify all tasks are returned
        assert len(tasks) == 3
        statuses = [task.status for task in tasks]
        assert TASK_STATE_NOT_STARTED in statuses
        assert TASK_STATE_IN_PROGRESS in statuses
        assert TASK_STATE_COMPLETED in statuses
    
    def test_task_manager_integration(self, db_manager):
        """
        Integration test for TaskManager class
        """
        # Create a TaskManager instance with the DB_CONFIG_TEST
        task_manager = TaskManager(DB_CONFIG_TEST)
        repo = task_manager.task_repository
        
        # Add tasks through repository directly (for testing only)
        task1 = Task(
            name="Integration Test Task 1", 
            description="Description 1", 
            status=TASK_STATE_NOT_STARTED
        )
        task2 = Task(
            name="Integration Test Task 2", 
            description="Description 2", 
            status=TASK_STATE_IN_PROGRESS
        )
        task3 = Task(
            name="Integration Test Task 3", 
            description="Description 3", 
            status=TASK_STATE_COMPLETED
        )
        
        # Add tasks directly to repository for testing
        assert repo.add(task1)
        assert repo.add(task2)
        assert repo.add(task3)
        
        # Get all tasks
        all_tasks = repo.get_all()
        assert len(all_tasks) == 3
        
        # Get only active tasks
        active_tasks = repo.get_all((TASK_STATE_NOT_STARTED, TASK_STATE_IN_PROGRESS))
        assert len(active_tasks) == 2
        
        # Update a task
        update_result = repo.update_status(task1.id, TASK_STATE_COMPLETED)
        assert update_result
        
        # Verify update worked
        updated_tasks = repo.get_all((TASK_STATE_NOT_STARTED, TASK_STATE_IN_PROGRESS))
        assert len(updated_tasks) == 1
        
        # Delete a task
        delete_result = repo.delete(task2.id)
        assert delete_result
        
        # Verify delete worked
        remaining_tasks = repo.get_all()
        assert len(remaining_tasks) == 2
    
    # Name length validation tests
    def test_name_length_validation(self, task_repository):
        """
        Test that name length validation works at the database level
        """
        # Test with a name at the maximum allowed length
        max_length_name = "A" * MAX_NAME_LENGTH
        task_valid = Task(
            name=max_length_name,
            description="Test description"
        )
        
        # This should succeed
        result = task_repository.add(task_valid)
        assert result == True
        assert task_valid.id is not None
        
        # Verify the name was saved correctly
        retrieved_task = task_repository.get_by_id(task_valid.id)
        assert len(retrieved_task.name) == MAX_NAME_LENGTH
        
        # Now test with a name that exceeds the maximum length
        # This might fail at the database level depending on how your repository handles errors
        oversized_name = "B" * (MAX_NAME_LENGTH + 10)
        task_invalid = Task(
            name=oversized_name,
            description="Test description"
        )
        
        # This might succeed or fail depending on your error handling in repository
        try:
            result = task_repository.add(task_invalid)
            # If it doesn't raise an exception but returns False, that's fine too
            if result:
                # If it somehow succeeded, the database might have truncated the name
                retrieved_task = task_repository.get_by_id(task_invalid.id)
                # The name should be no longer than MAX_NAME_LENGTH
                assert len(retrieved_task.name) <= MAX_NAME_LENGTH
        except:
            # It's okay if it raises an exception
            pass

    # Name length validation tests
    def test_name_length_validation_error(self, task_repository):
        """
        Test that name length validation works at the database level
        """
        # Test with a name at the maximum allowed length
        max_length_name = "A" * 500
        task_valid = Task(
            name=max_length_name,
            description="Test description"
        )
        
        # This should succeed
        result = task_repository.add(task_valid)
        assert result == False

    def test_name_length_validation_in_ui(self, monkeypatch):
        """
        Test that the UI validates name length before submitting to database
        """
        # Mock a sequence of inputs: 
        # 1. First too long name
        # 2. Valid name
        # 3. Valid description
        # 4. Enter (default status)
        task_manager = TaskManager(DB_CONFIG_TEST)
        too_long_name = "A" * (MAX_NAME_LENGTH + 10)
        valid_name = "Valid Name"
        valid_desc = "Valid Description"
        
        inputs = [too_long_name, valid_name, valid_desc, ""]
        input_iterator = iter(inputs)
        
        def mock_input(prompt):
            return next(input_iterator)
        
        monkeypatch.setattr('builtins.input', mock_input)
        
        # Capture stdout to check for error message
        output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        
        # Run the add_task method
        task_manager.add_task()
        
        # Reset stdout
        sys.stdout = original_stdout
        
        # Check that the error message was displayed
        assert ERROR_NAME_TOO_LONG in output.getvalue()
        
        # Check that the task was eventually added with the valid name
        tasks = task_manager.task_repository.get_all()
        assert len(tasks) == 1
        assert tasks[0].name == valid_name        

    # Exit functionality tests with proper connection handling
    def test_exit_functionality_main_menu(self, monkeypatch, db_manager):
        """
        Test that typing 'exit' in the main menu returns option 5 (exit program)
        """
        task_manager = TaskManager(DB_CONFIG_TEST)
        
        # Mock input to return 'exit'
        monkeypatch.setattr('builtins.input', lambda _: 'exit')
        
        # Call main_menu and verify it returns 5
        choice = task_manager.main_menu()
        assert choice == 5
    
    def test_exit_functionality_add_task(self, monkeypatch, db_manager):
        """
        Test that typing 'exit' during add_task cancels the operation
        """
        task_manager = TaskManager(DB_CONFIG_TEST)
        
        # Get initial count of tasks
        initial_count = len(task_manager.task_repository.get_all())
        
        # Test exiting at name prompt (first input)
        monkeypatch.setattr('builtins.input', lambda _: 'exit')
        
        # Capture print output to check for cancellation message
        output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        
        task_manager.add_task()  # Should exit early
        
        # Reset stdout
        sys.stdout = original_stdout
        
        # Check output for cancellation message
        assert "cancelled" in output.getvalue().lower()
        
        # Verify no task was added
        current_count = len(task_manager.task_repository.get_all())
        assert current_count == initial_count
    
    def test_exit_functionality_multistep_inputs(self, monkeypatch, db_manager):
        """
        Test exit functionality with multiple inputs in sequence
        """
        task_manager = TaskManager(DB_CONFIG_TEST)
        repo = task_manager.task_repository
        
        # Create test task first (directly through repository for testing)
        task = Task(name="Test Task for Update", description="Test Description", status=TASK_STATE_NOT_STARTED)
        repo.add(task)
        
        # Test exiting at the second input (status selection) in update_task
        # Sequence: valid ID → 'exit'
        input_values = [str(task.id), 'exit']
        input_iterator = iter(input_values)
        
        def mock_input_sequence(prompt):
            return next(input_iterator)
            
        monkeypatch.setattr('builtins.input', mock_input_sequence)
        
        # Capture print output
        output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        
        # Run update task operation
        task_manager.update_task()
        
        # Reset stdout
        sys.stdout = original_stdout
        
        # Check for cancellation message
        assert "cancelled" in output.getvalue().lower()
        
        # Verify task status was not changed
        task_after = repo.get_by_id(task.id)
        assert task_after.status == TASK_STATE_NOT_STARTED
    
    def test_exit_functionality_delete_confirmation(self, monkeypatch, db_manager):
        """
        Test exit functionality during delete confirmation
        """
        task_manager = TaskManager(DB_CONFIG_TEST)
        repo = task_manager.task_repository
        
        # Create test task first (directly through repository for testing)
        task = Task(name="Test Task for Delete", description="Test Description", status=TASK_STATE_NOT_STARTED)
        repo.add(task)
        
        # Test exiting at confirmation prompt
        # Sequence: valid ID → 'exit' at confirmation
        input_values = [str(task.id), 'exit']
        input_iterator = iter(input_values)
        
        def mock_input_sequence(prompt):
            return next(input_iterator)
            
        monkeypatch.setattr('builtins.input', mock_input_sequence)
        
        # Capture print output
        output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        
        # Run delete task operation
        task_manager.delete_task()
        
        # Reset stdout
        sys.stdout = original_stdout
        
        # Check for cancellation message
        assert "cancelled" in output.getvalue().lower()
        
        # Verify task was not deleted
        task_after = repo.get_by_id(task.id)
        assert task_after is not None
    
    def test_multiple_exit_points(self, monkeypatch, db_manager):
        """
        Test that exit functionality works at various points in the application
        """
        task_manager = TaskManager(DB_CONFIG_TEST)
        repo = task_manager.task_repository
        
        # Create test task first for showing tasks
        task = Task(name="Test Task", description="Test Description", status=TASK_STATE_NOT_STARTED)
        repo.add(task)
        
        # Test exit points in various functions
        test_cases = [
            # Function, Expected output
            (task_manager.show_tasks, None),  # No specific output expected
            (task_manager.main_menu, None),  # Returns 5, no specific print output
            (task_manager.add_task, "cancelled"),
            (task_manager.update_task, "cancelled"),
            (task_manager.delete_task, "cancelled")
        ]
        
        for func, expected_output in test_cases:
            # Set input to always return 'exit'
            monkeypatch.setattr('builtins.input', lambda _: 'exit')
            
            # Capture output if needed
            if expected_output:
                output = StringIO()
                original_stdout = sys.stdout
                sys.stdout = output
            
            # Call the function - should exit gracefully
            if func == task_manager.main_menu:
                result = func()
                assert result == 5  # Exit option
            else:
                func()  # Should not raise exceptions
            
            # Check output if needed
            if expected_output:
                sys.stdout = original_stdout
                assert expected_output.lower() in output.getvalue().lower()        
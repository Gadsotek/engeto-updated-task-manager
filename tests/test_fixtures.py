import pytest
import sys
import os
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from constants import TASK_STATE_NOT_STARTED, TASK_STATE_IN_PROGRESS, TASK_STATE_COMPLETED
from models import Task
from db_manager import DatabaseManager
from repository import TaskRepository
from task_manager import TaskManager

# Import test database configuration - raise exception if missing
try:
    from test_db_config import DB_CONFIG_TEST
except ImportError:
    raise ImportError("Test database configuration file (test_db_config.py) is missing. Please create this file with your test database settings.")


def close_all_connections():
    """Helper function to force close any lingering connections"""
    try:
        # Connect to server without database
        conn_params = {
            "host": DB_CONFIG_TEST["host"],
            "port": DB_CONFIG_TEST.get("port", 3306),
            "user": DB_CONFIG_TEST["user"],
            "password": DB_CONFIG_TEST["password"]
        }
        conn = mysql.connector.connect(**conn_params)
        cursor = conn.cursor()
        
        # Close open connections to test database (MySQL 8.0+)
        cursor.execute(f"SELECT id FROM information_schema.processlist WHERE db = '{DB_CONFIG_TEST['database']}'")
        process_ids = [row[0] for row in cursor.fetchall()]
        
        for pid in process_ids:
            try:
                cursor.execute(f"KILL {pid}")
            except:
                pass
        
        cursor.close()
        conn.close()
    except:
        # Silently fail if this doesn't work
        pass


def recreate_test_database():
    """Function to recreate the test database from scratch"""
    try:
        # Connect to MySQL server without specifying the database
        conn_params = {
            "host": DB_CONFIG_TEST["host"],
            "port": DB_CONFIG_TEST.get("port", 3306),
            "user": DB_CONFIG_TEST["user"],
            "password": DB_CONFIG_TEST["password"]
        }
        conn = mysql.connector.connect(**conn_params)
        cursor = conn.cursor()
        
        # Drop and recreate database
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG_TEST['database']}")
        cursor.execute(f"CREATE DATABASE {DB_CONFIG_TEST['database']}")
        
        # Use the database and create the tasks table
        cursor.execute(f"USE {DB_CONFIG_TEST['database']}")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Not started',
            created_at DATETIME NOT NULL
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error recreating test database: {e}")


@pytest.fixture(scope="session", autouse=True)
def setup_teardown_database():
    """Fixture to create and clean up the test database"""
    # Set up - create the test database
    recreate_test_database()
    
    yield
    
    # Tear down - force close connections and drop the database
    close_all_connections()
    try:
        conn_params = {
            "host": DB_CONFIG_TEST["host"],
            "port": DB_CONFIG_TEST.get("port", 3306),
            "user": DB_CONFIG_TEST["user"],
            "password": DB_CONFIG_TEST["password"]
        }
        conn = mysql.connector.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG_TEST['database']}")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error dropping test database: {e}")


@pytest.fixture(scope="function", autouse=True)
def clean_database():
    """Fixture to clean the database before each test"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG_TEST)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error cleaning database: {e}")
    
    yield


@pytest.fixture(scope="function")
def db_manager():
    """
    Fixture to provide a database manager for testing
    """
    # Create a database manager with test configuration
    db_manager = DatabaseManager(DB_CONFIG_TEST)
    
    yield db_manager
    
    # Close the connection after the test
    db_manager.close()


@pytest.fixture(scope="function")
def task_repository(db_manager):
    """
    Fixture to provide a task repository for testing
    """
    repo = TaskRepository(db_manager)
    yield repo


@pytest.fixture(scope="function")
def task_manager(db_manager):
    """
    Fixture to provide a TaskManager instance for testing
    """
    task_manager = TaskManager(DB_CONFIG_TEST)
    yield task_manager
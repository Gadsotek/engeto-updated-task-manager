import mysql.connector
from mysql.connector import Error
from constants import DB_CREATED_OR_EXISTS, DB_TABLE_CREATED_OR_EXISTS

class DatabaseManager:
    """
    Class to manage database connection and operations
    """
    def __init__(self, config=None):
        """
        Initialize the database manager with configuration.
        
        Args:
            config (dict, optional): Database configuration with host, user, password, and database keys.
        """
        self.config = config
        self.connection = None
        
    def connect(self):
        """
        Establishes connection to the MySQL database.
        Returns connection object if successful, None otherwise.
        """
        # Close any existing connection first
        self.close()
        
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
        return None
    
    def close(self):
        """
        Closes the database connection if it's open
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
            
    def __del__(self):
        """
        Ensure connection is closed when object is destroyed
        """
        self.close()
            
    def create_database(self):
        """
        Creates the database if it doesn't exist
        """
        try:
            # Connect to MySQL server without specifying the database
            connection_params = {
                "host": self.config["host"],
                "port": self.config.get("port", 3306),
                "user": self.config["user"],
                "password": self.config["password"]
            }
            
            temp_connection = mysql.connector.connect(**connection_params)
            if temp_connection.is_connected():
                cursor = temp_connection.cursor()
                # Create the database if it doesn't exist
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
                print(DB_CREATED_OR_EXISTS.format(self.config['database']))
                cursor.close()
                temp_connection.close()
                return True
        except Error as e:
            print(f"Error creating database: {e}")
            return False
    
    def create_table(self):
        """
        Creates the tasks table if it doesn't exist
        """
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                
                # SQL query to create the tasks table
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
                connection.commit()
                print(DB_TABLE_CREATED_OR_EXISTS)
                cursor.close()
                self.close()
                return True
            except Error as e:
                print(f"Error creating table: {e}")
                self.close()
                return False
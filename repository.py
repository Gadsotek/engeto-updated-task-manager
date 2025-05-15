from mysql.connector import Error
from models import Task

class TaskRepository:
    """
    Repository class for Task CRUD operations
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def add(self, task):
        """
        Adds a task to the database
        """
        connection = self.db_manager.connect()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO tasks (name, description, status, created_at)
            VALUES (%s, %s, %s, %s)
            """
            values = (task.name, task.description, task.status, task.created_at)
            cursor.execute(query, values)
            connection.commit()
            
            # Get the ID of the newly inserted task
            task.id = cursor.lastrowid
            
            cursor.close()
            return True
        except Error as e:
            print(f"Error adding task: {e}")
            return False
        finally:
            self.db_manager.close()
    
    def get_all(self, filter_status=None):
        """
        Retrieves all tasks, optionally filtered by status
        """
        connection = self.db_manager.connect()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            if filter_status:
                query = "SELECT * FROM tasks WHERE status IN (%s, %s)"
                cursor.execute(query, filter_status)
            else:
                query = "SELECT * FROM tasks"
                cursor.execute(query)
                
            result = cursor.fetchall()
            tasks = []
            
            for row in result:
                task = Task(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    status=row['status'],
                    created_at=row['created_at']
                )
                tasks.append(task)
                
            cursor.close()
            return tasks
        except Error as e:
            print(f"Error retrieving tasks: {e}")
            return []
        finally:
            self.db_manager.close()
    
    def get_by_id(self, task_id):
        """
        Retrieves a task by its ID
        """
        connection = self.db_manager.connect()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM tasks WHERE id = %s"
            cursor.execute(query, (task_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            task = Task(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                status=row['status'],
                created_at=row['created_at']
            )
                
            cursor.close()
            return task
        except Error as e:
            print(f"Error retrieving task: {e}")
            return None
        finally:
            self.db_manager.close()
    
    def update_status(self, task_id, new_status):
        """
        Updates the status of a task
        """
        connection = self.db_manager.connect()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            query = "UPDATE tasks SET status = %s WHERE id = %s"
            cursor.execute(query, (new_status, task_id))
            connection.commit()
            
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows > 0
        except Error as e:
            print(f"Error updating task: {e}")
            return False
        finally:
            self.db_manager.close()
    
    def delete(self, task_id):
        """
        Deletes a task by its ID
        """
        connection = self.db_manager.connect()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            query = "DELETE FROM tasks WHERE id = %s"
            cursor.execute(query, (task_id,))
            connection.commit()
            
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows > 0
        except Error as e:
            print(f"Error deleting task: {e}")
            return False
        finally:
            self.db_manager.close()
from datetime import datetime
from constants import TASK_STATE_NOT_STARTED

class Task:
    """
    Class representing a Task entity
    """
    def __init__(self, id=None, name="", description="", 
                 status=TASK_STATE_NOT_STARTED, created_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.created_at = created_at if created_at else datetime.now()
    
    def __str__(self):
        return f"Task {self.id}: {self.name} - Status: {self.status}"
        
    def display(self, include_description=True):
        """
        Format task for display
        """
        output = [f"ID: {self.id} - {self.name}"]
        if include_description:
            output.append(f"   Description: {self.description}")
        output.append(f"   Status: {self.status}")
        output.append(f"   Created at: {self.created_at}")
        return "\n".join(output)
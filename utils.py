from constants import *

def is_exit_command(command):
    """
    Check if input is an exit command
    """
    return isinstance(command, str) and command.lower() == 'exit'


def get_input_with_exit(prompt, validation_func=None, error_message=None):
    """
    Get input from user with exit command handling and optional validation
    
    Args:
        prompt (str): Input prompt to display
        validation_func (callable, optional): Function to validate input
        error_message (str, optional): Error message for invalid input
        
    Returns:
        str: User input or None if user entered exit command
    """
    while True:
        user_input = input(prompt).strip()
        
        if is_exit_command(user_input):
            return None
            
        if validation_func:
            if validation_func(user_input):
                return user_input
            else:
                print(error_message)
        else:
            return user_input


def get_numeric_input_with_exit(prompt, min_val, max_val, allow_empty=False):
    """
    Get numeric input from user with validation and exit command handling
    
    Args:
        prompt (str): Input prompt to display
        min_val (int): Minimum acceptable value
        max_val (int): Maximum acceptable value
        allow_empty (bool): Whether to allow empty input (return None)
        
    Returns:
        int: Numeric value or None if user entered exit command or (if allowed) empty input
    """
    while True:
        user_input = input(prompt).strip()
        
        if is_exit_command(user_input):
            return None
            
        if allow_empty and not user_input:
            return None
            
        try:
            value = int(user_input)
            if min_val <= value <= max_val:
                return value
            else:
                print(ERROR_INVALID_CHOICE.format(f"{min_val}-{max_val}"))
        except ValueError:
            print(ERROR_INVALID_NUMBER)
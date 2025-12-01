import os

def get_project_root():
    """
    Returns the absolute path to the project root directory.
    """
    # src/ is one level below project root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_data_file_path(filename):
    """
    Get the absolute path to a file in the test_data directory.
    
    Args:
        filename: Name of the file in the test_data directory
        
    Returns:
        Absolute path to the file
    """
    project_root = get_project_root()
    return os.path.join(project_root, "test_data", filename)

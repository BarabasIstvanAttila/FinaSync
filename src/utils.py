import os

def get_data_file_path(filename):
    """
    Get the absolute path to a file in the test_data directory.
    
    Args:
        filename: Name of the file in the test_data directory
        
    Returns:
        Absolute path to the file
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, "test_data", filename)

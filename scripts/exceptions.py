class InvalidFileStructureException(Exception):
    """
    Raised when in reading file something not correct
    """
    def __init__(self, message):
        self.message = message


class InvalidFileFormatException(Exception):
    """
    Raised when file format is not supported
    """
    def __init__(self, message):
        self.message = message

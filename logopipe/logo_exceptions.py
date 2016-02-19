"""
Expecptions for logopipe
"""

class InvalidExecutableError(Exception):
    """Error thrown when executable doesn't exist"""
    def __init__(self, message):
        super(InvalidExecutableError, self).__init__(message)

class InvalidBatchTypeError(Exception):
    """Error thrown when batch type isn't supported"""
    def __init__(self, message):
        super(InvalidBatchTypeError, self).__init__(message)

class InvalidYAMLFormatError(Exception):
    """Error thrown when yaml format is incorrect"""
    def __init__(self, message):
        super(InvalidYAMLFormatError, self).__init__(message)

class NoUniqueFileFoundError(Exception):
    """Error when no unique file can be found"""
    def __init__(self, message):
        super(NoUniqueFileFoundError, self).__init__(message)



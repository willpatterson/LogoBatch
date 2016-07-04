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

class BatchTemplateFileNotFoundError(Exception):
    """Error when no batchfile is found"""
    def __init__(self, message):
        super(BatchTemplateFileNotFoundError, self).__init__(message)

class NoBatchesError(Exception):
    """Error when no batches are found in a bbatch file"""
    def __init__(self, message):
        super(NoBatchesError, self).__init__(message)

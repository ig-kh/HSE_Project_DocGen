class DocGenError(Exception):
    """
    Base exception for all DocGen backend errors.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ExtractionError(DocGenError):
    """
    Raised when LLM extraction fails.
    """
    pass


class ValidationError(DocGenError):
    """
    Raised when extracted JSON fails validation.
    """
    pass


class DocxProcessingError(DocGenError):
    """
    Raised when DOCX parsing or processing fails.
    """
    pass


class EntityReplacementError(DocGenError):
    """
    Raised when entity replacement fails.
    """
    pass


class RenderingError(DocGenError):
    """
    Raised when template rendering fails.
    """
    pass


class PipelineError(DocGenError):
    """
    Raised for general pipeline failures.
    """
    pass
from shared.models.enums import ErrorCode


class AgentException(Exception):
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.AGENT_RUNTIME_ERROR):
        super().__init__(message)
        self.error_code = error_code

class AgentPromptException(AgentException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.AGENT_PROMPT_ERROR)

class AgentLLMException(AgentException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.AGENT_LLM_ERROR)

class AgentTimeoutException(AgentException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.AGENT_TIMEOUT)

class AgentOutputParseException(AgentException):
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.AGENT_OUTPUT_PARSE_ERROR)
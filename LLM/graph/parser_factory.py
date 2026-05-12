from .base_parser import BaseCodeParser
from .parsers.go_parser import GoParser
from .parsers.java_parser import JavaParser
from .parsers.javascript_parser import JavaScriptParser
from .parsers.python_parser import PythonParser
from .parsers.typescript_parser import TypeScriptParser

_REGISTRY: dict[str, type[BaseCodeParser]] = {
    "python": PythonParser,
    "typescript": TypeScriptParser,
    "javascript": JavaScriptParser,
    "java": JavaParser,
    "go": GoParser,
}


def get_parser(language: str) -> BaseCodeParser | None:
    """Return a parser for *language*, or None if unsupported."""
    cls = _REGISTRY.get(language.lower())
    return cls() if cls else None

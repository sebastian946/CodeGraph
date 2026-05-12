from dataclasses import dataclass, field


@dataclass
class FunctionInfo:
    name: str
    start_line: int
    end_line: int
    parameters: list[str] = field(default_factory=list)
    docstring: str | None = None
    calls: list[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    start_line: int
    end_line: int
    methods: list[FunctionInfo] = field(default_factory=list)
    docstring: str | None = None


@dataclass
class FileAST:
    filepath: str
    language: str
    imports: list[str] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)

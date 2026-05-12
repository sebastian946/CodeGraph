from abc import ABC, abstractmethod
from tree_sitter import Language, Parser, Node
from .models import FileAST, FunctionInfo, ClassInfo


class BaseCodeParser(ABC):
    """Abstract base for language-specific AST parsers (Visitor pattern).

    Subclasses implement one method per extraction concern; parse() orchestrates them.
    """

    def __init__(self, language: Language) -> None:
        self._parser = Parser(language)
        self._language = language

    def parse(self, source: str | bytes, filepath: str = "") -> FileAST:
        if isinstance(source, str):
            source_bytes = source.encode("utf-8")
        else:
            source_bytes = source

        tree = self._parser.parse(source_bytes)
        root = tree.root_node
        known_names = self._collect_top_level_names(root, source_bytes)

        return FileAST(
            filepath=filepath,
            language=self._language_name(),
            imports=self._extract_imports(root, source_bytes),
            functions=self._extract_functions(root, source_bytes, known_names),
            classes=self._extract_classes(root, source_bytes, known_names),
        )

    def _node_text(self, node: Node, source: bytes) -> str:
        return source[node.start_byte : node.end_byte].decode("utf-8")

    @abstractmethod
    def _language_name(self) -> str: ...

    @abstractmethod
    def _collect_top_level_names(self, root: Node, source: bytes) -> set[str]: ...

    @abstractmethod
    def _extract_imports(self, root: Node, source: bytes) -> list[str]: ...

    @abstractmethod
    def _extract_functions(
        self, root: Node, source: bytes, known_names: set[str]
    ) -> list[FunctionInfo]: ...

    @abstractmethod
    def _extract_classes(
        self, root: Node, source: bytes, known_names: set[str]
    ) -> list[ClassInfo]: ...

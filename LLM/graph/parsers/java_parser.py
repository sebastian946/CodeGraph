import tree_sitter_java as tsjava
from tree_sitter import Language, Node

from ..base_parser import BaseCodeParser
from ..models import ClassInfo, FunctionInfo

JAVA_LANGUAGE = Language(tsjava.language())


class JavaParser(BaseCodeParser):
    def __init__(self) -> None:
        super().__init__(JAVA_LANGUAGE)

    def _language_name(self) -> str:
        return "java"

    # ------------------------------------------------------------------ #
    # Name collection                                                      #
    # ------------------------------------------------------------------ #

    def _collect_top_level_names(self, root: Node, source: bytes) -> set[str]:
        names: set[str] = set()
        self._walk_method_names(root, source, names)
        return names

    def _walk_method_names(self, node: Node, source: bytes, names: set[str]) -> None:
        if node.type == "method_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                names.add(self._node_text(name_node, source))
        for child in node.children:
            self._walk_method_names(child, source, names)

    # ------------------------------------------------------------------ #
    # Imports                                                              #
    # ------------------------------------------------------------------ #

    def _extract_imports(self, root: Node, source: bytes) -> list[str]:
        return [
            self._node_text(node, source).strip()
            for node in root.children
            if node.type == "import_declaration"
        ]

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _extract_javadoc(self, node: Node, source: bytes) -> str | None:
        prev = node.prev_named_sibling
        if prev and prev.type == "block_comment":
            text = self._node_text(prev, source)
            if text.startswith("/**"):
                return text
        return None

    def _extract_parameters(self, params_node: Node, source: bytes) -> list[str]:
        return [
            self._node_text(name_node, source)
            for child in params_node.children
            if child.type == "formal_parameter"
            for name_node in [child.child_by_field_name("name")]
            if name_node
        ]

    def _collect_calls(
        self, node: Node, source: bytes, known_names: set[str], acc: list[str]
    ) -> None:
        if node.type == "method_invocation":
            # Only unqualified calls: `foo()` not `obj.foo()`
            if not node.child_by_field_name("object"):
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = self._node_text(name_node, source)
                    if name in known_names:
                        acc.append(name)
        for child in node.children:
            self._collect_calls(child, source, known_names, acc)

    def _extract_calls(
        self, body_node: Node, source: bytes, known_names: set[str]
    ) -> list[str]:
        acc: list[str] = []
        self._collect_calls(body_node, source, known_names, acc)
        return list(dict.fromkeys(acc))

    def _build_method(
        self, node: Node, source: bytes, known_names: set[str]
    ) -> FunctionInfo:
        name_node = node.child_by_field_name("name")
        params_node = node.child_by_field_name("parameters")
        body_node = node.child_by_field_name("body")

        return FunctionInfo(
            name=self._node_text(name_node, source) if name_node else "<anonymous>",
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            parameters=self._extract_parameters(params_node, source) if params_node else [],
            docstring=self._extract_javadoc(node, source),
            calls=self._extract_calls(body_node, source, known_names) if body_node else [],
        )

    # ------------------------------------------------------------------ #
    # Java has no top-level functions — only class methods                #
    # ------------------------------------------------------------------ #

    def _extract_functions(
        self, root: Node, source: bytes, known_names: set[str]
    ) -> list[FunctionInfo]:
        return []

    def _extract_classes(
        self, root: Node, source: bytes, known_names: set[str]
    ) -> list[ClassInfo]:
        classes: list[ClassInfo] = []
        self._walk_classes(root, source, known_names, classes)
        return classes

    def _walk_classes(
        self,
        node: Node,
        source: bytes,
        known_names: set[str],
        acc: list[ClassInfo],
    ) -> None:
        if node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            body_node = node.child_by_field_name("body")
            methods = (
                [
                    self._build_method(child, source, known_names)
                    for child in body_node.children
                    if child.type == "method_declaration"
                ]
                if body_node
                else []
            )
            acc.append(
                ClassInfo(
                    name=self._node_text(name_node, source) if name_node else "<anonymous>",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    methods=methods,
                    docstring=self._extract_javadoc(node, source),
                )
            )
            # Also recurse into nested classes inside the body
            if body_node:
                for child in body_node.children:
                    if child.type == "class_declaration":
                        self._walk_classes(child, source, known_names, acc)
        else:
            for child in node.children:
                self._walk_classes(child, source, known_names, acc)

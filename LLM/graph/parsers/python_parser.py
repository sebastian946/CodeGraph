import tree_sitter_python as tspython
from tree_sitter import Language, Node

from ..base_parser import BaseCodeParser
from ..models import ClassInfo, FunctionInfo

PY_LANGUAGE = Language(tspython.language())


class PythonParser(BaseCodeParser):
    def __init__(self) -> None:
        super().__init__(PY_LANGUAGE)

    def _language_name(self) -> str:
        return "python"

    # ------------------------------------------------------------------ #
    # Name collection for call-graph resolution                           #
    # ------------------------------------------------------------------ #

    def _collect_top_level_names(self, root: Node, source: bytes) -> set[str]:
        names: set[str] = set()
        for node in root.children:
            if node.type == "function_definition":
                name_node = node.child_by_field_name("name")
                if name_node:
                    names.add(self._node_text(name_node, source))
            elif node.type == "class_definition":
                body = node.child_by_field_name("body")
                if body:
                    for child in body.children:
                        if child.type == "function_definition":
                            name_node = child.child_by_field_name("name")
                            if name_node:
                                names.add(self._node_text(name_node, source))
        return names

    # ------------------------------------------------------------------ #
    # Imports                                                              #
    # ------------------------------------------------------------------ #

    def _extract_imports(self, root: Node, source: bytes) -> list[str]:
        return [
            self._node_text(node, source)
            for node in root.children
            if node.type in ("import_statement", "import_from_statement")
        ]

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _extract_docstring(self, body_node: Node, source: bytes) -> str | None:
        for child in body_node.children:
            if child.type == "expression_statement":
                for expr in child.children:
                    if expr.type == "string":
                        raw = self._node_text(expr, source)
                        # Strip triple or single quotes
                        for q in ('"""', "'''", '"', "'"):
                            if raw.startswith(q) and raw.endswith(q):
                                return raw[len(q) : -len(q)].strip()
                        return raw.strip()
            elif child.type not in ("comment", "newline", "indent"):
                break
        return None

    def _extract_parameters(self, params_node: Node, source: bytes) -> list[str]:
        params: list[str] = []
        skip = {"self", "cls"}
        for child in params_node.named_children:
            name: str | None = None
            if child.type == "identifier":
                name = self._node_text(child, source)
            elif child.type in (
                "typed_parameter",
                "default_parameter",
                "typed_default_parameter",
                "list_splat_pattern",
                "dictionary_splat_pattern",
            ):
                # First identifier child is the parameter name in all cases
                for sub in child.children:
                    if sub.type == "identifier":
                        name = self._node_text(sub, source)
                        break
            if name and name not in skip:
                params.append(name)
        return params

    def _collect_calls(
        self, node: Node, source: bytes, known_names: set[str], acc: list[str]
    ) -> None:
        if node.type == "call":
            func_node = node.child_by_field_name("function")
            if func_node and func_node.type == "identifier":
                name = self._node_text(func_node, source)
                if name in known_names:
                    acc.append(name)
        for child in node.children:
            self._collect_calls(child, source, known_names, acc)

    def _extract_calls(
        self, body_node: Node, source: bytes, known_names: set[str]
    ) -> list[str]:
        acc: list[str] = []
        self._collect_calls(body_node, source, known_names, acc)
        return list(dict.fromkeys(acc))  # deduplicate, preserve order

    # ------------------------------------------------------------------ #
    # Function / class extraction                                          #
    # ------------------------------------------------------------------ #

    def _build_function(
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
            docstring=self._extract_docstring(body_node, source) if body_node else None,
            calls=self._extract_calls(body_node, source, known_names) if body_node else [],
        )

    def _extract_functions(
        self, root: Node, source: bytes, known_names: set[str]
    ) -> list[FunctionInfo]:
        return [
            self._build_function(node, source, known_names)
            for node in root.children
            if node.type == "function_definition"
        ]

    def _extract_classes(
        self, root: Node, source: bytes, known_names: set[str]
    ) -> list[ClassInfo]:
        classes: list[ClassInfo] = []
        for node in root.children:
            if node.type != "class_definition":
                continue
            name_node = node.child_by_field_name("name")
            body_node = node.child_by_field_name("body")
            methods = (
                [
                    self._build_function(child, source, known_names)
                    for child in body_node.children
                    if child.type == "function_definition"
                ]
                if body_node
                else []
            )
            classes.append(
                ClassInfo(
                    name=self._node_text(name_node, source) if name_node else "<anonymous>",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    methods=methods,
                    docstring=self._extract_docstring(body_node, source) if body_node else None,
                )
            )
        return classes

import tree_sitter_typescript as tsts
from tree_sitter import Language, Node

from ..base_parser import BaseCodeParser
from ..models import ClassInfo, FunctionInfo

TS_LANGUAGE = Language(tsts.language_typescript())


class JsTsParser(BaseCodeParser):
    """Shared parsing logic for JavaScript and TypeScript.

    Both grammars use the same node-type names for the constructs we care
    about, so a single implementation covers both. Subclasses only need to
    supply the concrete Language object and the language name string.
    """

    # ------------------------------------------------------------------ #
    # Name collection                                                      #
    # ------------------------------------------------------------------ #

    def _collect_top_level_names(self, root: Node, source: bytes) -> set[str]:
        names: set[str] = set()
        for node in root.children:
            if node.type in ("function_declaration", "generator_function_declaration"):
                name_node = node.child_by_field_name("name")
                if name_node:
                    names.add(self._node_text(name_node, source))
            elif node.type in ("lexical_declaration", "variable_declaration"):
                for child in node.children:
                    if child.type == "variable_declarator":
                        name_node = child.child_by_field_name("name")
                        value_node = child.child_by_field_name("value")
                        if (
                            name_node
                            and value_node
                            and value_node.type in ("arrow_function", "function")
                        ):
                            names.add(self._node_text(name_node, source))
        return names

    # ------------------------------------------------------------------ #
    # Imports                                                              #
    # ------------------------------------------------------------------ #

    def _extract_imports(self, root: Node, source: bytes) -> list[str]:
        return [
            self._node_text(node, source)
            for node in root.children
            if node.type == "import_statement"
        ]

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _extract_jsdoc(self, node: Node, source: bytes) -> str | None:
        # prev_named_sibling skips anonymous whitespace/punctuation tokens
        prev = node.prev_named_sibling
        if prev and prev.type == "comment":
            text = self._node_text(prev, source)
            if text.startswith("/**"):
                return text
        return None

    def _extract_parameters(self, params_node: Node, source: bytes) -> list[str]:
        params: list[str] = []
        for child in params_node.children:
            if child.type == "identifier":
                params.append(self._node_text(child, source))
            elif child.type in (
                "required_parameter",
                "optional_parameter",
                "rest_pattern",
                "assignment_pattern",
            ):
                # pattern field holds the identifier
                pattern = child.child_by_field_name("pattern")
                if pattern and pattern.type == "identifier":
                    params.append(self._node_text(pattern, source))
                else:
                    # fallback: first identifier child
                    for sub in child.children:
                        if sub.type == "identifier":
                            params.append(self._node_text(sub, source))
                            break
        return params

    def _collect_calls(
        self, node: Node, source: bytes, known_names: set[str], acc: list[str]
    ) -> None:
        if node.type == "call_expression":
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
        return list(dict.fromkeys(acc))

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
            docstring=self._extract_jsdoc(node, source),
            calls=self._extract_calls(body_node, source, known_names) if body_node else [],
        )

    def _extract_functions(
        self, root: Node, source: bytes, known_names: set[str]
    ) -> list[FunctionInfo]:
        functions: list[FunctionInfo] = []
        for node in root.children:
            if node.type in ("function_declaration", "generator_function_declaration"):
                functions.append(self._build_function(node, source, known_names))
            elif node.type in ("lexical_declaration", "variable_declaration"):
                for child in node.children:
                    if child.type != "variable_declarator":
                        continue
                    name_node = child.child_by_field_name("name")
                    value_node = child.child_by_field_name("value")
                    if not (name_node and value_node and value_node.type in ("arrow_function", "function")):
                        continue
                    params_node = value_node.child_by_field_name(
                        "parameters"
                    ) or value_node.child_by_field_name("parameter")
                    body_node = value_node.child_by_field_name("body")
                    functions.append(
                        FunctionInfo(
                            name=self._node_text(name_node, source),
                            start_line=node.start_point[0] + 1,
                            end_line=node.end_point[0] + 1,
                            parameters=self._extract_parameters(params_node, source) if params_node else [],
                            docstring=self._extract_jsdoc(node, source),
                            calls=self._extract_calls(body_node, source, known_names) if body_node else [],
                        )
                    )
        return functions

    def _extract_classes(
        self, root: Node, source: bytes, known_names: set[str]
    ) -> list[ClassInfo]:
        classes: list[ClassInfo] = []
        for node in root.children:
            if node.type != "class_declaration":
                continue
            name_node = node.child_by_field_name("name")
            body_node = node.child_by_field_name("body")
            methods: list[FunctionInfo] = []
            if body_node:
                for child in body_node.children:
                    if child.type == "method_definition":
                        methods.append(self._build_function(child, source, known_names))
            classes.append(
                ClassInfo(
                    name=self._node_text(name_node, source) if name_node else "<anonymous>",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    methods=methods,
                    docstring=self._extract_jsdoc(node, source),
                )
            )
        return classes


class TypeScriptParser(JsTsParser):
    def __init__(self) -> None:
        super().__init__(TS_LANGUAGE)

    def _language_name(self) -> str:
        return "typescript"

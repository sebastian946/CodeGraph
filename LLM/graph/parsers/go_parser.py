import tree_sitter_go as tsgo
from tree_sitter import Language, Node

from ..base_parser import BaseCodeParser
from ..models import ClassInfo, FunctionInfo

GO_LANGUAGE = Language(tsgo.language())


class GoParser(BaseCodeParser):
    def __init__(self) -> None:
        super().__init__(GO_LANGUAGE)

    def _language_name(self) -> str:
        return "go"

    # ------------------------------------------------------------------ #
    # Name collection                                                      #
    # ------------------------------------------------------------------ #

    def _collect_top_level_names(self, root: Node, source: bytes) -> set[str]:
        return {
            self._node_text(node.child_by_field_name("name"), source)
            for node in root.children
            if node.type == "function_declaration"
            and node.child_by_field_name("name")
        }

    # ------------------------------------------------------------------ #
    # Imports                                                              #
    # ------------------------------------------------------------------ #

    def _extract_imports(self, root: Node, source: bytes) -> list[str]:
        imports: list[str] = []
        for node in root.children:
            if node.type != "import_declaration":
                continue
            for child in node.children:
                if child.type == "import_spec_list":
                    for spec in child.children:
                        if spec.type == "import_spec":
                            imports.append(self._node_text(spec, source).strip())
                elif child.type == "import_spec":
                    imports.append(self._node_text(child, source).strip())
        return imports

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _extract_godoc(self, node: Node, source: bytes) -> str | None:
        """Collect consecutive // comment lines immediately before the node."""
        lines: list[str] = []
        prev = node.prev_named_sibling
        while prev and prev.type == "comment":
            lines.insert(0, self._node_text(prev, source))
            prev = prev.prev_named_sibling
        return "\n".join(lines) if lines else None

    def _extract_parameters(self, params_node: Node, source: bytes) -> list[str]:
        params: list[str] = []
        for child in params_node.children:
            if child.type == "parameter_declaration":
                # "x, y int" — get only identifiers before the type
                for sub in child.children:
                    if sub.type == "identifier":
                        params.append(self._node_text(sub, source))
                    elif sub.is_named and sub.type not in ("identifier",):
                        # hit the type node — stop
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
            docstring=self._extract_godoc(node, source),
            calls=self._extract_calls(body_node, source, known_names) if body_node else [],
        )

    # ------------------------------------------------------------------ #
    # Go has no classes — structs are separate; methods are functions     #
    # ------------------------------------------------------------------ #

    def _extract_functions(
        self, root: Node, source: bytes, known_names: set[str]
    ) -> list[FunctionInfo]:
        return [
            self._build_function(node, source, known_names)
            for node in root.children
            if node.type == "function_declaration"
        ]

    def _extract_classes(
        self, root: Node, source: bytes, known_names: set[str]
    ) -> list[ClassInfo]:
        return []

"""
AST parser tests — one class per language.

Each test class:
  - parses the matching fixture file
  - verifies imports, function/class names, line numbers, parameters,
    docstrings, and the internal call graph
"""

from pathlib import Path

import pytest

from graph.models import ClassInfo, FileAST, FunctionInfo
from graph.parser_factory import get_parser

FIXTURES = Path(__file__).parent / "fixtures"


# ------------------------------------------------------------------ #
# Python                                                               #
# ------------------------------------------------------------------ #

class TestPythonParser:
    def setup_method(self):
        parser = get_parser("python")
        source = (FIXTURES / "sample.py").read_text(encoding="utf-8")
        self.ast: FileAST = parser.parse(source, "sample.py")

    def test_language(self):
        assert self.ast.language == "python"

    def test_imports(self):
        assert len(self.ast.imports) == 3
        assert any("import os" in imp for imp in self.ast.imports)
        assert any("import sys" in imp for imp in self.ast.imports)
        assert any("pathlib" in imp for imp in self.ast.imports)

    def test_function_names(self):
        names = [f.name for f in self.ast.functions]
        assert "greet" in names
        assert "process" in names

    def test_function_line_numbers(self):
        greet = next(f for f in self.ast.functions if f.name == "greet")
        assert greet.start_line > 0
        assert greet.end_line >= greet.start_line

    def test_function_parameters(self):
        greet = next(f for f in self.ast.functions if f.name == "greet")
        assert greet.parameters == ["name"]

        process = next(f for f in self.ast.functions if f.name == "process")
        assert "data" in process.parameters
        assert "verbose" in process.parameters

    def test_function_docstring(self):
        greet = next(f for f in self.ast.functions if f.name == "greet")
        assert greet.docstring is not None
        assert "greeting" in greet.docstring.lower()

    def test_class_names(self):
        names = [c.name for c in self.ast.classes]
        assert "Calculator" in names

    def test_class_docstring(self):
        calc = next(c for c in self.ast.classes if c.name == "Calculator")
        assert calc.docstring is not None

    def test_class_method_names(self):
        calc = next(c for c in self.ast.classes if c.name == "Calculator")
        method_names = [m.name for m in calc.methods]
        assert "add" in method_names
        assert "subtract" in method_names
        assert "compute" in method_names

    def test_method_parameters_exclude_self(self):
        calc = next(c for c in self.ast.classes if c.name == "Calculator")
        add = next(m for m in calc.methods if m.name == "add")
        assert "self" not in add.parameters
        assert "a" in add.parameters
        assert "b" in add.parameters

    def test_call_graph(self):
        process = next(f for f in self.ast.functions if f.name == "process")
        assert "greet" in process.calls


# ------------------------------------------------------------------ #
# TypeScript                                                           #
# ------------------------------------------------------------------ #

class TestTypeScriptParser:
    def setup_method(self):
        parser = get_parser("typescript")
        source = (FIXTURES / "sample.ts").read_text(encoding="utf-8")
        self.ast: FileAST = parser.parse(source, "sample.ts")

    def test_language(self):
        assert self.ast.language == "typescript"

    def test_imports(self):
        assert len(self.ast.imports) == 2

    def test_function_names(self):
        names = [f.name for f in self.ast.functions]
        assert "greet" in names
        assert "process" in names

    def test_function_parameters(self):
        greet = next(f for f in self.ast.functions if f.name == "greet")
        assert "name" in greet.parameters

    def test_function_line_numbers(self):
        greet = next(f for f in self.ast.functions if f.name == "greet")
        assert greet.start_line > 0
        assert greet.end_line >= greet.start_line

    def test_class_names(self):
        names = [c.name for c in self.ast.classes]
        assert "Calculator" in names

    def test_class_method_names(self):
        calc = next(c for c in self.ast.classes if c.name == "Calculator")
        method_names = [m.name for m in calc.methods]
        assert "add" in method_names
        assert "subtract" in method_names

    def test_call_graph(self):
        process = next(f for f in self.ast.functions if f.name == "process")
        assert "greet" in process.calls


# ------------------------------------------------------------------ #
# JavaScript                                                           #
# ------------------------------------------------------------------ #

class TestJavaScriptParser:
    def setup_method(self):
        parser = get_parser("javascript")
        source = (FIXTURES / "sample.js").read_text(encoding="utf-8")
        self.ast: FileAST = parser.parse(source, "sample.js")

    def test_language(self):
        assert self.ast.language == "javascript"

    def test_imports(self):
        assert len(self.ast.imports) == 2

    def test_function_names(self):
        names = [f.name for f in self.ast.functions]
        assert "greet" in names
        assert "process" in names

    def test_function_parameters(self):
        greet = next(f for f in self.ast.functions if f.name == "greet")
        assert "name" in greet.parameters

    def test_class_names(self):
        names = [c.name for c in self.ast.classes]
        assert "Calculator" in names

    def test_call_graph(self):
        process = next(f for f in self.ast.functions if f.name == "process")
        assert "greet" in process.calls


# ------------------------------------------------------------------ #
# Java                                                                 #
# ------------------------------------------------------------------ #

class TestJavaParser:
    def setup_method(self):
        parser = get_parser("java")
        source = (FIXTURES / "Sample.java").read_text(encoding="utf-8")
        self.ast: FileAST = parser.parse(source, "Sample.java")

    def test_language(self):
        assert self.ast.language == "java"

    def test_imports(self):
        assert len(self.ast.imports) == 3
        assert any("List" in imp for imp in self.ast.imports)
        assert any("HashMap" in imp for imp in self.ast.imports)

    def test_no_top_level_functions(self):
        assert self.ast.functions == []

    def test_class_names(self):
        names = [c.name for c in self.ast.classes]
        assert "Sample" in names

    def test_class_method_names(self):
        sample = next(c for c in self.ast.classes if c.name == "Sample")
        method_names = [m.name for m in sample.methods]
        assert "greet" in method_names
        assert "process" in method_names

    def test_method_parameters(self):
        sample = next(c for c in self.ast.classes if c.name == "Sample")
        greet = next(m for m in sample.methods if m.name == "greet")
        assert "name" in greet.parameters

    def test_method_docstring(self):
        sample = next(c for c in self.ast.classes if c.name == "Sample")
        greet = next(m for m in sample.methods if m.name == "greet")
        assert greet.docstring is not None
        assert "/**" in greet.docstring

    def test_method_line_numbers(self):
        sample = next(c for c in self.ast.classes if c.name == "Sample")
        greet = next(m for m in sample.methods if m.name == "greet")
        assert greet.start_line > 0
        assert greet.end_line >= greet.start_line

    def test_call_graph(self):
        sample = next(c for c in self.ast.classes if c.name == "Sample")
        process = next(m for m in sample.methods if m.name == "process")
        assert "greet" in process.calls


# ------------------------------------------------------------------ #
# Go                                                                   #
# ------------------------------------------------------------------ #

class TestGoParser:
    def setup_method(self):
        parser = get_parser("go")
        source = (FIXTURES / "sample.go").read_text(encoding="utf-8")
        self.ast: FileAST = parser.parse(source, "sample.go")

    def test_language(self):
        assert self.ast.language == "go"

    def test_imports(self):
        assert len(self.ast.imports) == 2
        assert any("fmt" in imp for imp in self.ast.imports)
        assert any("strings" in imp for imp in self.ast.imports)

    def test_function_names(self):
        names = [f.name for f in self.ast.functions]
        assert "Greet" in names
        assert "Process" in names
        assert "Add" in names
        assert "Compute" in names

    def test_function_parameters(self):
        greet = next(f for f in self.ast.functions if f.name == "Greet")
        assert "name" in greet.parameters

    def test_function_line_numbers(self):
        greet = next(f for f in self.ast.functions if f.name == "Greet")
        assert greet.start_line > 0
        assert greet.end_line >= greet.start_line

    def test_godoc(self):
        greet = next(f for f in self.ast.functions if f.name == "Greet")
        assert greet.docstring is not None
        assert "Greet" in greet.docstring

    def test_call_graph_process_calls_greet(self):
        process = next(f for f in self.ast.functions if f.name == "Process")
        assert "Greet" in process.calls

    def test_call_graph_compute_calls_add(self):
        compute = next(f for f in self.ast.functions if f.name == "Compute")
        assert "Add" in compute.calls

    def test_no_classes(self):
        assert self.ast.classes == []


# ------------------------------------------------------------------ #
# Factory edge case                                                    #
# ------------------------------------------------------------------ #

class TestParserFactory:
    def test_unsupported_language_returns_none(self):
        from graph.parser_factory import get_parser
        assert get_parser("cobol") is None

    def test_case_insensitive(self):
        assert get_parser("Python") is not None
        assert get_parser("JAVA") is not None

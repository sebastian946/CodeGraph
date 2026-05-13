# CodeGraph

A multi-language code analysis system that uses tree-sitter to parse and extract structured information from source code. CodeGraph builds Abstract Syntax Trees (AST) to extract functions, classes, imports, documentation, and internal call graphs.

## Features

- **Multi-language Support**: Python, TypeScript, JavaScript, Java, and Go
- **AST-based Parsing**: Leverages tree-sitter for accurate, fast parsing
- **Comprehensive Extraction**:
  - Function and class definitions with line numbers
  - Function parameters (excluding `self`/`cls` in Python)
  - Docstrings and comments (language-specific)
  - Import statements
  - Internal call graphs (which functions call which within the same file)
- **Visitor Pattern**: Clean architecture with abstract base parser
- **Factory Pattern**: Language-agnostic parser instantiation

## Architecture

```
graph/
├── base_parser.py          # Abstract base class with visitor pattern
├── models.py               # Data structures (FileAST, FunctionInfo, ClassInfo)
├── parser_factory.py       # Factory for creating language-specific parsers
└── parsers/
    ├── python_parser.py    # Python AST parser
    ├── typescript_parser.py # TypeScript/JavaScript base parser
    ├── javascript_parser.py # JavaScript parser (extends TypeScript)
    ├── java_parser.py      # Java AST parser
    └── go_parser.py        # Go AST parser
```

### Core Concepts

#### AST Navigation
Each parser uses tree-sitter to navigate the syntax tree:
- `node.children` - iterate over child nodes
- `node.type` - get the node type (e.g., `function_definition`)
- `node.child_by_field_name()` - access specific fields (e.g., `"name"`, `"parameters"`)
- `node.start_point[0]` / `node.end_point[0]` - get line numbers

#### Language-Specific Node Types
Different languages use different AST node names:
- **Python**: `function_definition`, `class_definition`
- **TypeScript/JavaScript**: `function_declaration`, `arrow_function`, `method_definition`
- **Java**: `method_declaration`, `class_declaration`
- **Go**: `function_declaration`

#### Visitor Pattern
`BaseCodeParser` defines abstract methods for each extraction concern:
- `_extract_imports()` - extract import statements
- `_extract_functions()` - extract top-level functions
- `_extract_classes()` - extract classes and their methods
- `_collect_top_level_names()` - collect function/method names for call graph resolution

The `parse()` method orchestrates all extractions and returns a `FileAST` object.

## Installation

### Dependencies
All tree-sitter grammars are included in `pyproject.toml`:

```toml
dependencies = [
    "tree-sitter>=0.22",
    "tree-sitter-python>=0.22",
    "tree-sitter-typescript>=0.22",
    "tree-sitter-javascript>=0.22",
    "tree-sitter-java>=0.22",
    "tree-sitter-go>=0.22",
]
```

### Setup

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies (using uv or pip)
uv sync
# or
pip install -e .
```

## Usage

### Basic Example

```python
from graph.parser_factory import get_parser

# Get a language-specific parser
parser = get_parser("python")  # Case-insensitive: "Python", "PYTHON", etc.

# Parse source code
source_code = """
def greet(name: str) -> str:
    '''Return a personalized greeting.'''
    return f"Hello, {name}!"

def process(data: list) -> dict:
    result = greet("world")
    return {"result": result}
"""

ast = parser.parse(source_code, filepath="example.py")

# Access extracted information
print(f"Language: {ast.language}")
print(f"Functions: {[f.name for f in ast.functions]}")
print(f"Imports: {ast.imports}")

# Inspect function details
for func in ast.functions:
    print(f"\nFunction: {func.name}")
    print(f"  Lines: {func.start_line}-{func.end_line}")
    print(f"  Parameters: {func.parameters}")
    print(f"  Docstring: {func.docstring}")
    print(f"  Calls: {func.calls}")  # Internal call graph
```

### Output Example

```
Language: python
Functions: ['greet', 'process']
Imports: []

Function: greet
  Lines: 2-4
  Parameters: ['name']
  Docstring: Return a personalized greeting.
  Calls: []

Function: process
  Lines: 6-8
  Parameters: ['data']
  Docstring: None
  Calls: ['greet']  # process() calls greet()
```

### Supported Languages

```python
# Python
parser = get_parser("python")

# TypeScript
parser = get_parser("typescript")

# JavaScript
parser = get_parser("javascript")

# Java
parser = get_parser("java")

# Go
parser = get_parser("go")

# Unsupported language returns None
parser = get_parser("cobol")  # None
```

## Data Models

### FileAST
Represents the complete AST for a file:

```python
@dataclass
class FileAST:
    filepath: str
    language: str
    imports: list[str]
    functions: list[FunctionInfo]
    classes: list[ClassInfo]
```

### FunctionInfo
Represents a function or method:

```python
@dataclass
class FunctionInfo:
    name: str
    start_line: int
    end_line: int
    parameters: list[str]           # Excludes 'self'/'cls' in Python
    docstring: str | None           # Language-specific docs
    calls: list[str]                # Internal call graph
```

### ClassInfo
Represents a class definition:

```python
@dataclass
class ClassInfo:
    name: str
    start_line: int
    end_line: int
    methods: list[FunctionInfo]
    docstring: str | None
```

## Documentation Extraction

Each parser extracts language-specific documentation:

| Language   | Documentation Format | Example |
|------------|---------------------|---------|
| Python     | Docstrings (`"""`)  | `"""Returns greeting."""` |
| TypeScript | JSDoc (`/**`)       | `/** Returns greeting. */` |
| JavaScript | JSDoc (`/**`)       | `/** Returns greeting. */` |
| Java       | JavaDoc (`/**`)     | `/** Returns greeting. */` |
| Go         | Godoc comments      | `// Greet returns greeting.` |

## Internal Call Graph

Each parser tracks which functions/methods are called within the same file:

```python
# Python example
def helper():
    pass

def main():
    helper()  # This call is tracked
    print()   # Builtin - not tracked

# Extracted call graph:
# helper.calls = []
# main.calls = ['helper']
```

Only calls to functions/methods defined in the **same file** are tracked.

## Testing

### Run All Tests

```bash
# From project root
.venv/bin/pytest tests/test_ast_parser.py -v

# With coverage
.venv/bin/pytest tests/test_ast_parser.py --cov=graph
```

### Test Coverage

All 5 languages have comprehensive test fixtures and test suites:

```
tests/
├── test_ast_parser.py          # 45 tests - all passing ✓
└── fixtures/
    ├── sample.py               # Python fixture
    ├── sample.ts               # TypeScript fixture
    ├── sample.js               # JavaScript fixture
    ├── Sample.java             # Java fixture
    └── sample.go               # Go fixture
```

Each test class verifies:
- ✅ Language detection
- ✅ Import extraction
- ✅ Function/method names
- ✅ Line numbers (start/end)
- ✅ Parameter extraction
- ✅ Docstring/comment extraction
- ✅ Internal call graph
- ✅ Class and method detection

**Test Results**: `45 passed in 1.53s` ✓

## Advanced Usage

### Creating a Custom Parser

To add support for a new language:

1. **Install the tree-sitter grammar**:
   ```toml
   dependencies = [
       "tree-sitter-rust>=0.22",
   ]
   ```

2. **Create a parser class**:
   ```python
   import tree_sitter_rust as tsrust
   from tree_sitter import Language, Node
   from ..base_parser import BaseCodeParser
   
   RUST_LANGUAGE = Language(tsrust.language())
   
   class RustParser(BaseCodeParser):
       def __init__(self):
           super().__init__(RUST_LANGUAGE)
       
       def _language_name(self) -> str:
           return "rust"
       
       # Implement abstract methods...
   ```

3. **Register in factory**:
   ```python
   # parser_factory.py
   _REGISTRY = {
       "rust": RustParser,
       # ...
   }
   ```

### Extending BaseCodeParser

Override any helper methods for language-specific behavior:

```python
class CustomParser(BaseCodeParser):
    def _extract_docstring(self, node: Node, source: bytes) -> str | None:
        # Custom docstring extraction logic
        pass
    
    def _extract_parameters(self, node: Node, source: bytes) -> list[str]:
        # Custom parameter extraction logic
        pass
```

## Project Context

CodeGraph is part of a larger system that includes:
- **FastAPI server** (`main.py`) - Health check and token management
- **Redis integration** (`indexer/redis_events.py`) - Event storage
- **GitHub integration** (`config/github_generate_token.py`) - GitHub App tokens
- **Repository cloning** (`indexer/repo_cloner.py`) - Clone and analyze repos
- **Indexing system** (`indexer/index.py`) - Code indexing pipeline

## Environment Setup

```bash
# .env file
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY=path/to/private-key.pem
GITHUB_INSTALLATION_ID=your_installation_id

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Development

### Run the FastAPI server

```bash
uvicorn main:app --reload
```

### Run tests

```bash
pytest tests/ -v
```

### Lint and format

```bash
ruff check .
ruff format .
```

## License

[Your License Here]

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting a PR:

```bash
pytest tests/test_ast_parser.py -v
```

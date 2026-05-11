from pathlib import Path

EXTENSION_MAP: dict[str, str] = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".cs": "CSharp",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".scala": "Scala",
    ".sql": "SQL",
    ".sh": "Shell",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
}

IGNORED_DIRS: set[str] = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt",
    "target",   # Rust / Java build output
    "vendor",   # Go dependencies
}

IGNORED_EXTENSIONS: set[str] = {
    ".lock", ".sum",                          # lock files
    ".pyc", ".pyo", ".class", ".o",           # compiled
    ".so", ".dll", ".exe",                    # native binaries
    ".png", ".jpg", ".jpeg", ".gif", ".ico",  # images
    ".mp4", ".mp3", ".wav",                   # media
    ".zip", ".tar", ".gz", ".rar",            # archives
}

IGNORED_FILENAMES: set[str] = {
    "package-lock.json", "yarn.lock", "poetry.lock",
    "Pipfile.lock", "uv.lock", "Cargo.lock", ".DS_Store",
}


def detect_language(path: Path) -> str | None:
    return EXTENSION_MAP.get(path.suffix.lower())


def is_binary(path: Path) -> bool:
    """Reads the first 8 KB and treats the file as binary if it contains null bytes."""
    try:
        with open(path, "rb") as f:
            return b"\x00" in f.read(8192)
    except OSError:
        return True


def should_skip(path: Path) -> bool:
    if path.name in IGNORED_FILENAMES:
        return True
    if path.suffix.lower() in IGNORED_EXTENSIONS:
        return True
    if any(part in IGNORED_DIRS for part in path.parts):
        return True
    return is_binary(path)


def iter_indexable_files(root: Path):
    """Yields (path, language) for every indexable source file under root."""
    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        language = detect_language(path)
        if language is not None:
            yield path, language

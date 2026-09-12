import ast
from pathlib import Path

import pytest

# Define structural restrictions
# Format: "layer_path": ["forbidden_import_sub_string_1", "forbidden_sub_string_2"]
BOUNDARY_RULES = {
    "domain": [
        "veyra.infrastructure",
        "veyra.application",
        "veyra.api",
    ],
    "application": [
        "veyra.infrastructure",
        "veyra.api",
    ],
    "core": [
        "veyra.domain",
        "veyra.application",
        "veyra.infrastructure",
        "veyra.api",
    ],
}


def get_python_files(src_dir: Path) -> list[Path]:
    return list(src_dir.glob("**/*.py"))


def analyze_imports(file_path: Path) -> list[str]:
    """Extracts all imported modules from a python source file."""
    imports = []
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception as e:
        pytest.fail(f"Failed to parse AST for {file_path}: {e}")
    return imports


def test_architectural_boundaries():
    """Enforces boundaries and strict dependency inversion."""
    root_dir = Path(__file__).parent.parent.parent
    src_dir = root_dir / "src" / "veyra"

    assert src_dir.exists(), f"Source directory not found at: {src_dir}"

    violations = []

    for layer, forbidden_targets in BOUNDARY_RULES.items():
        layer_dir = src_dir / layer
        if not layer_dir.exists():
            continue

        for py_file in get_python_files(layer_dir):
            relative_file_path = py_file.relative_to(src_dir)
            imported_modules = analyze_imports(py_file)

            for imp in imported_modules:
                for forbidden in forbidden_targets:
                    if imp.startswith(forbidden):
                        violations.append(
                            f"Rule Violation in '{relative_file_path}': "
                            f"Layer '{layer}' cannot depend on '{forbidden}' (imported: '{imp}')"
                        )

    if violations:
        summary = "\n".join(violations)
        raise AssertionError(
            f"Architectural Boundary Enforcement Failed:\n{summary}\n"
            f"Ensure clean separation and dependency inversion rules are followed."
        )

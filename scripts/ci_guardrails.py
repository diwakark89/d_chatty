from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_COUNTS = {
    "app/main.py": {
        "app = FastAPI(": 1,
    },
    "app/persistence.py": {
        "def save_qa_state(": 1,
        "def load_qa_state(": 1,
    },
    "static/js/api.js": {
        "const API =": 1,
    },
    "README.md": {
        "# DChatty": 1,
    },
    "uvicorn_commands.md": {
        "# Uvicorn Commands": 1,
    },
}

TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".yml",
    ".yaml",
    ".js",
    ".json",
    ".txt",
    ".html",
    ".css",
}

SKIP_PARTS = {".git", ".venv", "uploads", "data", "node_modules"}
CONFLICT_MARKERS = ("<<<<<<<", ">>>>>>>")


def check_expected_counts(errors: list[str]) -> None:
    for rel_path, patterns in EXPECTED_COUNTS.items():
        file_path = ROOT / rel_path
        if not file_path.exists():
            errors.append(f"Missing required file: {rel_path}")
            continue

        content = file_path.read_text(encoding="utf-8")
        for pattern, expected in patterns.items():
            actual = content.count(pattern)
            if actual != expected:
                errors.append(
                    f"{rel_path}: expected {expected} occurrence(s) of '{pattern}' but found {actual}"
                )


def scan_for_conflict_markers(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        rel_path = path.relative_to(ROOT)
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError as exc:
            errors.append(f"Failed to read {rel_path}: {exc}")
            continue

        for line_no, line in enumerate(lines, start=1):
            if line.startswith(CONFLICT_MARKERS):
                errors.append(f"Conflict marker found in {rel_path}:{line_no}")


def main() -> int:
    errors: list[str] = []
    check_expected_counts(errors)
    scan_for_conflict_markers(errors)

    if errors:
        print("Repository guardrails failed:")
        for issue in errors:
            print(f"- {issue}")
        return 1

    print("Repository guardrails passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

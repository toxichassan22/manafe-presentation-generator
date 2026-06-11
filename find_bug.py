import os
from pathlib import Path

def search_text_all_files(dir_path: Path, query: str):
    print(f"Searching for '{query}' in {dir_path} recursively...")
    count = 0
    for path in dir_path.rglob("*"):
        if path.is_file() and not any(part.startswith('.') or part == 'venv' or part == '__pycache__' for part in path.parts):
            try:
                content = path.read_text(encoding="utf-8")
                if query in content:
                    print(f"Found in: {path}")
                    count += 1
                    for idx, line in enumerate(content.splitlines(), 1):
                        if query in line:
                            print(f"  Line {idx}: {line.strip()}")
            except Exception:
                pass
    print(f"Search complete. Found in {count} files.")

if __name__ == "__main__":
    search_text_all_files(Path("d:/workflow/real-estate-proposal-generator"), "landing-content")

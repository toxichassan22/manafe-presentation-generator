import os
from pathlib import Path

def search_text(dir_path: Path, query: str):
    print(f"Searching for '{query}' in {dir_path}...")
    for path in dir_path.rglob("*.py"):
        try:
            content = path.read_text(encoding="utf-8")
            if query in content:
                print(f"Found in: {path}")
                # Print lines containing the query
                for idx, line in enumerate(content.splitlines(), 1):
                    if query in line:
                        print(f"  Line {idx}: {line.strip()}")
        except Exception as e:
            pass

if __name__ == "__main__":
    search_text(Path("d:/workflow/real-estate-proposal-generator"), "landing-content")

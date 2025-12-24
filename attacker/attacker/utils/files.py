import sys

def load_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = [line.strip() for line in f if line.strip()]
        if not data:
            raise ValueError("Empty file")
        return data
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

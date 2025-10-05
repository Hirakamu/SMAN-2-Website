import os
import json

# Root directories
ROOTS = {
    "article": "artikel"
}

index = []

SNIPPET_LENGTH = 200  # number of characters to include in the snippet

for type_, root in ROOTS.items():
    for year in os.listdir(root):
        year_path = os.path.join(root, year)
        if not os.path.isdir(year_path):
            continue
        for month in os.listdir(year_path):
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path):
                continue
            for day in os.listdir(month_path):
                day_path = os.path.join(month_path, day)
                if not os.path.isdir(day_path):
                    continue
                for file in os.listdir(day_path):
                    if file.endswith(".json"):
                        filepath = os.path.join(day_path, file)

                        # Read the JSON file content
                        try:
                            with open(filepath, "r", encoding="utf-8") as f:
                                content_json = json.load(f)
                                content_text = content_json.get("content", "")
                        except Exception as e:
                            content_text = ""
                            print(f"Failed to read {filepath}: {e}")

                        # Extract title from first Markdown heading (# ...)
                        lines = content_text.splitlines()
                        title_found = None
                        snippet_lines = []
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            if line.startswith("#") and title_found is None:
                                title_found = line.lstrip("#").strip()
                            else:
                                snippet_lines.append(line)

                        snippet = " ".join(snippet_lines)
                        snippet = snippet[:SNIPPET_LENGTH] + ("..." if len(snippet) > SNIPPET_LENGTH else "")

                        index.append({
                            "title": title_found if title_found else os.path.splitext(file)[0],
                            "date": f"{year}-{month}-{day}",
                            "path": filepath,
                            "snippet": snippet
                        })

# Save to JSON
with open("index.json", "w", encoding="utf-8") as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

print(f"Indexed {len(index)} files with cleaned titles and snippets.")
